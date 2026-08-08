"""Re-transcribe incomplete startup_battlefield pitches from local PITCH mp4s.

GPU-only (mediaflow-lite conda env). Uses faster-whisper with the same Windows
CUDA DLL setup as mediaflow-lite VOICE (ensure_windows_ctranslate2_cuda_dlls).

Example (from theory_graph repo root):
    conda run -n mediaflow-lite python scripts/retranscribe_incomplete.py --dry-run
    conda run -n mediaflow-lite python scripts/retranscribe_incomplete.py
    conda run -n mediaflow-lite python scripts/retranscribe_incomplete.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "toolkit") not in sys.path:
    sys.path.insert(0, str(ROOT / "toolkit"))

from theory_graph.validate import (  # noqa: E402
    load_transcript,
    transcript_incomplete,
    transcript_opening_truncated,
    transcript_template_leak,
    transcript_truncated,
)

PP_CSV = Path(
    r"C:\Users\djdjoko\Data\uni\OneDrive - Universitaet St.Gallen\data\perfect_pitch\input_startup_battlefield.csv"
)
VIDEO_ROOT = Path(
    r"C:\Users\djdjoko\Data\uni\OneDrive - Universitaet St.Gallen\data\perfect_pitch\video\SB"
)
INCOMPLETE_SCREEN = ROOT / "data/corpora/startup_battlefield/analysis/transcript_completeness_screen.csv"
CASES = ROOT / "data/corpora/startup_battlefield/cases.csv"
TRANSCRIPTS = ROOT / "data/corpora/startup_battlefield/transcripts"
STAGING = ROOT / "data/corpora/startup_battlefield/transcripts_full/pitch"
REPORT = ROOT / "data/corpora/startup_battlefield/analysis/rewhisper_qc.csv"
MANIFEST = STAGING / "manifest.jsonl"


def to_db_id(csv_id: str) -> str:
    return re.sub(r"-(\d+)-", lambda m: f"-{int(m.group(1)):02d}-", csv_id, count=1)


def norm_key(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def parse_ts(ts: str) -> float | None:
    if not isinstance(ts, str) or not str(ts).strip() or pd.isna(ts):
        return None
    parts = str(ts).strip().split(":")
    if len(parts) != 3:
        return None
    h, m, s = map(int, parts)
    return h * 3600 + m * 60 + s


def video_path_for(csv_id: str) -> Path | None:
    base = csv_id.replace("-PITCH", "").replace("-Q&A", "")
    m = re.match(r"^SB-(.+)-(\d+)-(.+)$", base)
    if not m:
        return None
    season, session = m.group(1), m.group(2)
    folder = VIDEO_ROOT / season / session
    for name in (f"{csv_id}.mp4", f"{to_db_id(csv_id)}.mp4"):
        p = folder / name
        if p.exists():
            return p
    slug = base.split("-")[-1]
    hits = list(folder.glob(f"*{slug}*PITCH*.mp4"))
    return hits[0] if hits else None


def ffprobe_duration(path: Path) -> float | None:
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
        return float(out)
    except Exception:
        return None


def extract_wav(video: Path, wav: Path, start: float | None, end: float | None) -> None:
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    if start is not None and start > 0:
        cmd.extend(["-ss", str(start)])
    cmd.extend(["-i", str(video)])
    if end is not None and start is not None:
        cmd.extend(["-t", str(max(0.1, end - start))])
    elif end is not None:
        cmd.extend(["-t", str(end)])
    cmd.extend(["-ar", "16000", "-ac", "1", str(wav)])
    subprocess.check_call(cmd)


def transcribe_wav(wav: Path, model) -> str:
    segments, _ = model.transcribe(
        str(wav),
        beam_size=5,
        language="en",
        vad_filter=True,
        word_timestamps=False,
    )
    return " ".join(s.text.strip() for s in segments if s.text.strip())


def build_case_table() -> pd.DataFrame:
    screen = pd.read_csv(INCOMPLETE_SCREEN)
    inc = screen[screen.incomplete == True].copy()  # noqa: E712
    cases = pd.read_csv(CASES, dtype={"id": str, "case_id": str})
    pp = pd.read_csv(PP_CSV)
    pp_pitch = pp[pp.subsegment_id == "PITCH"].copy()
    pp_pitch["name_key"] = pp_pitch["name"].map(norm_key)
    pp_pitch["event_key"] = pp_pitch["event"].map(norm_key)
    cases["name_key"] = cases["name"].map(norm_key)
    cases["event_key"] = cases["event"].map(norm_key)

    m = inc.merge(cases[["case_id", "name", "event", "name_key", "event_key"]], on="case_id")
    m = m.merge(
        pp_pitch[
            [
                "id",
                "name_key",
                "event_key",
                "subsegment_start",
                "subsegment_end",
                "raw_video_remotepath",
            ]
        ],
        on=["name_key", "event_key"],
        how="left",
        suffixes=("", "_pp"),
    )
    m["pitch_csv_id"] = m["id"]
    m["video_path"] = m["pitch_csv_id"].map(lambda x: video_path_for(x) if isinstance(x, str) else None)
    m["video_exists"] = m["video_path"].map(lambda p: bool(p and Path(p).exists()))
    return m


def qc_row(case_id: str, old_t: str | None, new_t: str, video_s: float | None) -> dict:
    new_words = len(new_t.split())
    old_words = len(old_t.split()) if old_t else 0
    wpm = round(new_words / (video_s / 60), 1) if video_s and video_s > 0 else None
    return {
        "case_id": case_id,
        "old_words": old_words,
        "new_words": new_words,
        "delta_words": new_words - old_words,
        "video_s": round(video_s, 1) if video_s else None,
        "new_wpm": wpm,
        "old_incomplete": bool(transcript_incomplete(old_t)) if old_t else True,
        "new_incomplete": bool(transcript_incomplete(new_t)),
        "old_trailing": bool(transcript_truncated(old_t)) if old_t else True,
        "new_trailing": bool(transcript_truncated(new_t)),
        "old_opening": bool(transcript_opening_truncated(old_t)) if old_t else True,
        "new_opening": bool(transcript_opening_truncated(new_t)),
        "old_template": bool(transcript_template_leak(old_t)) if old_t else False,
        "new_template": bool(transcript_template_leak(new_t)),
        "old_head": (old_t or "")[:100],
        "old_tail": (old_t or "")[-100:],
        "new_head": new_t[:100],
        "new_tail": new_t[-100:],
        "looks_complete": (
            not transcript_incomplete(new_t)
            and (wpm is None or wpm >= 80)
            and new_words >= max(old_words, 200)
        ),
    }


def load_manifest_done() -> set[str]:
    if not MANIFEST.exists():
        return set()
    done = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            if rec.get("status") == "ok":
                done.add(rec["case_id"])
    return done


def append_manifest(entry: dict) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="h2oai/faster-whisper-large-v3-turbo",
        help="faster-whisper model id (default: mediaflow-lite ASR)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Copy staged transcripts into corpus dir")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--case", action="append", default=[], help="Only these pilot- IDs")
    args = parser.parse_args()

    if args.apply:
        rows = []
        for txt in sorted(STAGING.glob("pilot-*.txt")):
            case_id = txt.stem
            new_t = txt.read_text(encoding="utf-8").strip()
            old_t = load_transcript(TRANSCRIPTS, case_id)
            video = None
            # best-effort duration from manifest
            dur = None
            if MANIFEST.exists():
                for line in MANIFEST.read_text(encoding="utf-8").splitlines():
                    rec = json.loads(line)
                    if rec.get("case_id") == case_id:
                        dur = rec.get("video_s")
                        break
            rows.append(qc_row(case_id, old_t, new_t, dur))
            shutil.copy2(txt, TRANSCRIPTS / f"{case_id}.txt")
        pd.DataFrame(rows).to_csv(REPORT, index=False)
        print(f"Applied {len(rows)} transcripts -> {TRANSCRIPTS}")
        print(f"QC report -> {REPORT}")
        return

    table = build_case_table()
    if args.case:
        table = table[table.case_id.isin(args.case)]
    if args.limit:
        table = table.head(args.limit)

    print(f"Incomplete cases to process: {len(table)}")
    print(f"Video found: {table.video_exists.sum()} / {len(table)}")
    missing = table[~table.video_exists][["case_id", "name", "event"]]
    if len(missing):
        print("\nMissing video:")
        print(missing.to_string(index=False))

    if args.dry_run:
        print(table[["case_id", "name", "words", "video_exists", "subsegment_start", "subsegment_end"]].to_string())
        return

    import torch
    from faster_whisper import WhisperModel
    from mediaflow_lite.models.cache import models_cache_dir
    from mediaflow_lite.util.cuda_device import ensure_windows_ctranslate2_cuda_dlls

    if not torch.cuda.is_available():
        raise SystemExit(
            "CUDA required. Run via: conda run -n mediaflow-lite python scripts/retranscribe_incomplete.py\n"
            "If DLL errors persist, reinstall GPU stack from mediaflow-lite:\n"
            "  powershell -ExecutionPolicy Bypass -File C:\\Projects\\uni\\sources\\mediaflow-lite\\scripts\\install_gpu_stack.ps1"
        )

    done = load_manifest_done()
    todo = table[~table.case_id.isin(done)]
    print(f"Already done: {len(done)} | Remaining: {len(todo)}")

    ensure_windows_ctranslate2_cuda_dlls()
    device = "cuda"
    compute_type = "int8"
    cache_dir = str(models_cache_dir("whisper"))
    print(f"Loading whisper model={args.model} device={device} gpu={torch.cuda.get_device_name(0)}")
    model = WhisperModel(
        args.model,
        device=device,
        compute_type=compute_type,
        download_root=cache_dir,
    )

    STAGING.mkdir(parents=True, exist_ok=True)
    qc_rows = []

    for i, (_, row) in enumerate(todo.iterrows(), 1):
        case_id = row.case_id
        out_txt = STAGING / f"{case_id}.txt"
        if not row.video_exists:
            append_manifest({"case_id": case_id, "status": "no_video"})
            continue

        video = Path(row.video_path)
        # PITCH mp4s are already cut from the main stream; CSV subsegment_start/end
        # locate the segment in the *source* video, not trim instructions here.
        start = None
        end = None
        wav = STAGING / f"{case_id}.wav"
        t0 = time.time()

        try:
            extract_wav(video, wav, start, end)
            new_t = transcribe_wav(wav, model)
            new_t = " ".join(new_t.split())
            out_txt.write_text(new_t + "\n", encoding="utf-8")
            wav.unlink(missing_ok=True)

            old_t = load_transcript(TRANSCRIPTS, case_id)
            vid_s = ffprobe_duration(video)
            qc = qc_row(case_id, old_t, new_t, vid_s)
            qc["status"] = "ok"
            qc["elapsed_s"] = round(time.time() - t0, 1)
            qc_rows.append(qc)
            append_manifest({**qc, "status": "ok", "device": "cuda", "model": args.model})
            print(
                f"[{i}/{len(todo)}] {case_id}: {qc['old_words']} -> {qc['new_words']} w "
                f"inc={qc['old_incomplete']}->{qc['new_incomplete']} "
                f"({qc['elapsed_s']}s)"
            )
        except Exception as exc:
            append_manifest({"case_id": case_id, "status": "error", "error": str(exc)})
            print(f"[{i}/{len(todo)}] {case_id}: ERROR {exc}")

    if qc_rows:
        existing = pd.read_csv(REPORT) if REPORT.exists() else pd.DataFrame()
        pd.concat([existing, pd.DataFrame(qc_rows)], ignore_index=True).drop_duplicates(
            "case_id", keep="last"
        ).to_csv(REPORT, index=False)
        print(f"\nQC report -> {REPORT}")
        fixed = sum(1 for r in qc_rows if not r["new_incomplete"])
        print(f"Newly complete this run: {fixed}/{len(qc_rows)}")


if __name__ == "__main__":
    main()
