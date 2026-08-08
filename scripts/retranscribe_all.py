"""Re-transcribe all startup_battlefield PITCH and Q&A from local pre-cut mp4s.

GPU-only via mediaflow-lite conda env. Each *-PITCH.mp4 / *-Q&A.mp4 is transcribed
from t=0 to end (CSV subsegment timestamps are NOT applied).

Outputs (staging until --apply):
  data/corpora/startup_battlefield/transcripts_full/pitch/pilot-NNN.txt
  data/corpora/startup_battlefield/transcripts_full/qa/pilot-NNN.txt

Example:
    conda run -n mediaflow-lite python scripts/retranscribe_all.py --dry-run
    conda run -n mediaflow-lite python scripts/retranscribe_all.py
    conda run -n mediaflow-lite python scripts/retranscribe_all.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
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
CASES = ROOT / "data/corpora/startup_battlefield/cases.csv"
STAGING_ROOT = ROOT / "data/corpora/startup_battlefield/transcripts_full"
STAGING_PITCH = STAGING_ROOT / "pitch"
STAGING_QA = STAGING_ROOT / "qa"
CORPUS_PITCH = ROOT / "data/corpora/startup_battlefield/transcripts"
CORPUS_QA = ROOT / "data/corpora/startup_battlefield/transcripts_qa"
MANIFEST = STAGING_ROOT / "manifest.jsonl"
REPORT = ROOT / "data/corpora/startup_battlefield/analysis/retranscribe_full_qc.csv"

SEGMENTS = ("PITCH", "Q&A")

# cases.csv event labels -> perfect_pitch CSV event labels (norm_key on both sides)
EVENT_ALIASES = {
    "HARDWAREBATTLEFIELD": "HARDWAREBATTLEFIELD2014",
    "DISRUPTEUROPE2013": "DISRUPTBERLIN2013",
    "DISRUPTEUROPE2014LONDON": "DISRUPTLONDON2014",
    "DISRUPTNYC2010": "DISRUPTNY2010",
    "STARTUPBATTLEFIELDAUSTRALIA": "STARTUPBATTLEFIELDAUSTRALIA2017",
    "TECHCRUNCH502009": "TECHCRUNCHDISRUPT2009",
    "TECHCRUNCHSTARTUPBATTLEFIELDAFRICA": "STARTUPBATTLEFIELDAFRICA2017",
    "STARTUPBATTLEFIELDLATINAMERICA": "STARTUPBATTLEFIELDLATINAMERICA2018",
}

# case_id -> pitch csv_id when name/event fuzzy match is ambiguous or missing
CASE_CSV_OVERRIDES: dict[str, str] = {}


def to_db_id(csv_id: str) -> str:
    return re.sub(r"-(\d+)-", lambda m: f"-{int(m.group(1)):02d}-", csv_id, count=1)


def norm_key(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def event_key_for(s: str) -> str:
    key = norm_key(s)
    return EVENT_ALIASES.get(key, key)


def fuzzy_pp_rows(name: str, event: str, pp: pd.DataFrame) -> pd.DataFrame:
    sn = norm_key(name)
    if len(sn) < 4:
        return pp.iloc[0:0]
    hits = pp[
        pp["name"].map(norm_key).str.contains(sn[:8], na=False)
        | pp["id"].map(norm_key).str.contains(sn[:6], na=False)
    ]
    if event:
        ev = event_key_for(event)
        evhits = hits[hits["event"].map(event_key_for).str.contains(ev[:8], na=False)]
        if len(evhits):
            hits = evhits
    return hits


def qa_csv_id(pitch_csv_id: str) -> str:
    return pitch_csv_id.replace("-PITCH", "-Q&A")


def resolve_csv_id(
    case_id: str, name: str, event: str, segment: str, pp: pd.DataFrame
) -> str | None:
    if case_id in CASE_CSV_OVERRIDES:
        pitch_id = CASE_CSV_OVERRIDES[case_id]
        return pitch_id if segment == "PITCH" else qa_csv_id(pitch_id)

    pp_seg = pp[pp.subsegment_id == segment]
    exact = pp_seg[
        (pp_seg["name"].map(norm_key) == norm_key(name))
        & (pp_seg["event"].map(event_key_for) == event_key_for(event))
    ]
    if len(exact) == 1:
        return exact.iloc[0]["id"]
    if len(exact) > 1:
        return None

    hits = fuzzy_pp_rows(name, event, pp_seg)
    if len(hits) == 1:
        return hits.iloc[0]["id"]
    return None


def resolve_video_path(
    csv_id: str | None, name: str, segment: str
) -> Path | None:
    if isinstance(csv_id, str) and csv_id:
        p = video_path_for(csv_id)
        if p and p.exists():
            return p

    slug = norm_key(name)[:12]
    if not slug:
        return None
    seg_token = "PITCH" if segment == "PITCH" else "Q&A"
    hits = []
    for p in VIDEO_ROOT.rglob(f"*{seg_token}*.mp4"):
        stem = norm_key(p.stem)
        if slug in stem or stem.startswith(slug[:8]):
            hits.append(p)
    return hits[0] if len(hits) == 1 else None


def video_path_for(csv_id: str) -> Path | None:
    seg = "PITCH" if csv_id.endswith("-PITCH") else "Q&A"
    base = csv_id.replace("-PITCH", "").replace("-Q&A", "")
    m = re.match(r"^SB-(.+)-(\d+)-(.+)$", base)
    if not m:
        return None
    folder = VIDEO_ROOT / m.group(1) / m.group(2)
    for name in (f"{csv_id}.mp4", f"{to_db_id(csv_id)}.mp4"):
        p = folder / name
        if p.exists():
            return p
    slug = base.split("-")[-1]
    pattern = f"*{slug}*{seg}*.mp4"
    hits = list(folder.glob(pattern))
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


def extract_wav(video: Path, wav: Path) -> None:
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-ar",
            "16000",
            "-ac",
            "1",
            str(wav),
        ]
    )


def transcribe_wav(wav: Path, model) -> str:
    segments, _ = model.transcribe(
        str(wav),
        beam_size=5,
        language="en",
        vad_filter=True,
        word_timestamps=False,
    )
    return " ".join(s.text.strip() for s in segments if s.text.strip())


def staging_dir(segment: str) -> Path:
    return STAGING_PITCH if segment == "PITCH" else STAGING_QA


def corpus_dir(segment: str) -> Path:
    return CORPUS_PITCH if segment == "PITCH" else CORPUS_QA


def load_old_transcript(case_id: str, segment: str) -> str | None:
    d = corpus_dir(segment)
    p = d / f"{case_id}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    if segment == "PITCH":
        return load_transcript(CORPUS_PITCH, case_id)
    return None


def build_jobs() -> pd.DataFrame:
    cases = pd.read_csv(CASES, dtype={"id": str, "case_id": str})
    pp = pd.read_csv(PP_CSV)

    rows = []
    for segment in SEGMENTS:
        for _, case in cases.iterrows():
            csv_id = resolve_csv_id(
                case["case_id"], case["name"], case["event"], segment, pp
            )
            video = resolve_video_path(csv_id, case["name"], segment)
            rows.append(
                {
                    "case_id": case["case_id"],
                    "name": case["name"],
                    "event": case["event"],
                    "segment": segment,
                    "csv_id": csv_id,
                    "video_path": str(video) if video else None,
                    "video_exists": bool(video and video.exists()),
                }
            )

    return pd.DataFrame(rows)


def qc_row(case_id: str, segment: str, old_t: str | None, new_t: str, video_s: float | None) -> dict:
    new_words = len(new_t.split())
    old_words = len(old_t.split()) if old_t else 0
    wpm = round(new_words / (video_s / 60), 1) if video_s and video_s > 0 else None
    return {
        "case_id": case_id,
        "segment": segment,
        "old_words": old_words,
        "new_words": new_words,
        "delta_words": new_words - old_words,
        "video_s": round(video_s, 1) if video_s else None,
        "new_wpm": wpm,
        "old_incomplete": bool(transcript_incomplete(old_t)) if old_t else None,
        "new_incomplete": bool(transcript_incomplete(new_t)),
        "new_trailing": bool(transcript_truncated(new_t)),
        "new_opening": bool(transcript_opening_truncated(new_t)),
        "new_template": bool(transcript_template_leak(new_t)),
        "new_head": new_t[:100],
        "new_tail": new_t[-100:],
    }


def job_key(case_id: str, segment: str) -> str:
    return f"{case_id}|{segment}"


def load_manifest_no_video() -> set[str]:
    if not MANIFEST.exists():
        return set()
    missing = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("status") == "no_video":
            missing.add(job_key(rec["case_id"], rec["segment"]))
    return missing


def load_manifest_done() -> set[str]:
    if not MANIFEST.exists():
        return set()
    done = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("status") == "ok":
            done.add(job_key(rec["case_id"], rec["segment"]))
    return done


def append_manifest(entry: dict) -> None:
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="h2oai/faster-whisper-large-v3-turbo",
        help="faster-whisper model id (mediaflow-lite default ASR)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--segment", choices=["PITCH", "Q&A", "both"], default="both")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--case", action="append", default=[], help="Only these pilot- IDs")
    parser.add_argument(
        "--only-no-video",
        action="store_true",
        help="Only jobs previously marked no_video in manifest",
    )
    args = parser.parse_args()

    if args.apply:
        applied = 0
        for segment in SEGMENTS:
            src = staging_dir(segment)
            dst = corpus_dir(segment)
            dst.mkdir(parents=True, exist_ok=True)
            for txt in sorted(src.glob("pilot-*.txt")):
                shutil.copy2(txt, dst / txt.name)
                applied += 1
        print(f"Applied {applied} files -> {CORPUS_PITCH} and {CORPUS_QA}")
        return

    jobs = build_jobs()
    if args.segment != "both":
        jobs = jobs[jobs.segment == args.segment]
    if args.case:
        jobs = jobs[jobs.case_id.isin(args.case)]
    if args.only_no_video:
        prev = load_manifest_no_video()
        jobs = jobs[
            jobs.apply(lambda r: job_key(r.case_id, r.segment) in prev, axis=1)
        ]
    if args.limit:
        jobs = jobs.head(args.limit)

    print(f"Jobs: {len(jobs)} ({jobs.segment.value_counts().to_dict()})")
    print(f"With video: {jobs.video_exists.sum()} / {len(jobs)}")
    missing = jobs[~jobs.video_exists]
    if len(missing):
        print(f"\nMissing video ({len(missing)}):")
        print(missing.groupby("segment").size().to_string())

    if args.dry_run:
        print(jobs.head(20).to_string(index=False))
        return

    import torch
    from faster_whisper import WhisperModel
    from mediaflow_lite.models.cache import models_cache_dir
    from mediaflow_lite.util.cuda_device import ensure_windows_ctranslate2_cuda_dlls

    if not torch.cuda.is_available():
        raise SystemExit(
            "CUDA required. Run: conda run -n mediaflow-lite python scripts/retranscribe_all.py"
        )

    done = load_manifest_done()
    todo = jobs[
        ~jobs.apply(lambda r: job_key(r.case_id, r.segment) in done, axis=1)
    ]
    print(f"Already done: {len(done)} | Remaining: {len(todo)}")

    ensure_windows_ctranslate2_cuda_dlls()
    cache_dir = str(models_cache_dir("whisper"))
    print(f"Loading {args.model} on {torch.cuda.get_device_name(0)}")
    model = WhisperModel(
        args.model,
        device="cuda",
        compute_type="int8",
        download_root=cache_dir,
    )

    STAGING_PITCH.mkdir(parents=True, exist_ok=True)
    STAGING_QA.mkdir(parents=True, exist_ok=True)
    qc_rows = []

    for i, (_, row) in enumerate(todo.iterrows(), 1):
        case_id = row.case_id
        segment = row.segment
        out_dir = staging_dir(segment)
        out_txt = out_dir / f"{case_id}.txt"

        if not row.video_exists:
            append_manifest(
                {"case_id": case_id, "segment": segment, "status": "no_video"}
            )
            print(f"[{i}/{len(todo)}] {case_id} {segment}: NO VIDEO")
            continue

        video = Path(row.video_path)
        wav = out_dir / f"{case_id}.wav"
        t0 = time.time()
        try:
            extract_wav(video, wav)
            new_t = " ".join(transcribe_wav(wav, model).split())
            out_txt.write_text(new_t + "\n", encoding="utf-8")
            wav.unlink(missing_ok=True)

            old_t = load_old_transcript(case_id, segment)
            vid_s = ffprobe_duration(video)
            qc = qc_row(case_id, segment, old_t, new_t, vid_s)
            qc["status"] = "ok"
            qc["elapsed_s"] = round(time.time() - t0, 1)
            qc["device"] = "cuda"
            qc["model"] = args.model
            qc_rows.append(qc)
            append_manifest(qc)
            print(
                f"[{i}/{len(todo)}] {case_id} {segment}: "
                f"{qc['old_words'] or 0} -> {qc['new_words']} w "
                f"({qc['elapsed_s']}s)"
            )
        except Exception as exc:
            append_manifest(
                {
                    "case_id": case_id,
                    "segment": segment,
                    "status": "error",
                    "error": str(exc),
                }
            )
            print(f"[{i}/{len(todo)}] {case_id} {segment}: ERROR {exc}")

    if qc_rows:
        existing = pd.read_csv(REPORT) if REPORT.exists() else pd.DataFrame()
        pd.concat([existing, pd.DataFrame(qc_rows)], ignore_index=True).drop_duplicates(
            ["case_id", "segment"], keep="last"
        ).to_csv(REPORT, index=False)
        print(f"\nQC -> {REPORT}")


if __name__ == "__main__":
    main()
