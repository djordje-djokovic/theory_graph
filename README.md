# theory_graph

Encode entrepreneurial theories as structured graphs (P → D → V), measure architecture
(breadth, modularity / `n_domains`, …), and relate those measures to outcomes.

Corpus-agnostic: ship any source under `data/corpora/<name>/`. The bundled reference
runs use Startup Battlefield pitches and `GotSelected`; other corpora (e.g. Shark Tank)
plug in the same pipeline.

Independent of the paper drafts in `entrepreneurial_theories`. Copy or zip this folder
anywhere (exclude `.venv/` if present).

## Setup

```powershell
cd theory_graph
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env
# edit .env with your API key(s) — or use ollama (no key)
```

```powershell
python -m theory_graph --help
# after pip install -e .:
theory-graph --help
```

Before handing the folder off, both should print `PASS`:

```powershell
theory-graph equivalence
theory-graph reproduce --pipeline all
```

## Layout

```
theory_graph/
├── prompts/          # versioned codebooks
├── configs/examples/ # starter YAMLs
├── data/corpora/     # one folder per data source
├── reference/        # published corpora + shipped analysis
├── experiments/      # your new runs (never overwrite)
└── toolkit/theory_graph/
```

Published references: `reference/v1_3_2_nested/` (v1.3.2 nested) and
`reference/v1_5_1_crossed/` (v1.5.1 crossed), both n=376 Battlefield cases.
See `data/corpora/README.md` to add another corpus.

---

## How to — run a prompt experiment

End-to-end path for trying a new codebook version and getting outcome models
(for the bundled Battlefield corpus: GotSelected).

### 1. Spec the prompt

Edit a markdown codebook under **`prompts/`**.

```
prompts/
  v1_3_2.md      # published (nested reference)
  v1_5_1.md      # published (crossed reference)
  v2_0_0.md      # recommended base for new trials
  v2_0_1.md      # your copy — create this
  registry.md    # optional human log of versions
```

Do not edit published files in place. Copy and bump the name:

```powershell
copy prompts\v2_0_0.md prompts\v2_0_1.md
# edit prompts\v2_0_1.md
```

Add a row to `prompts/registry.md` when you lock a version you care about.

### 2. Spec the run (YAML)

Point at that prompt version in a config under **`configs/`** (start from an example):

```powershell
copy configs\examples\smoke_ollama_local.yaml configs\try_v2_0_1.yaml
```

Minimum fields:

```yaml
experiment:
  corpus: startup_battlefield          # folder under data/corpora/
  prompt_version: v2_0_1               # → prompts/v2_0_1.md
  sample: smoke_n20                    # or full_n376
  design: nested                       # nested | crossed (logged; k from encoding)
llm:
  model: "ollama/qwen2.5:14b"          # any LiteLLM model string
  temperature: 0.0
  max_tokens: 6000
encoding:
  backend: api                         # or manual
  k_runs: 3
```

| You want to change… | Edit… |
|---|---|
| Prompt text | `prompts/<version>.md` |
| Which prompt this run uses | `experiment.prompt_version` |
| Model / temperature | `llm:` |
| Sample size | `experiment.sample` |
| Corpus | `experiment.corpus` + `data/corpora/<name>/` |
| API keys | `.env` only (never YAML) |

### 2b. LiteLLM and API keys

With `encoding.backend: api`, calls go through **LiteLLM** (`litellm.completion`).
The `llm.model` value is a LiteLLM model string (`provider/model`).

Secrets and endpoints go in **`theory_graph/.env`** (copy from `.env.example`; do not commit `.env`):

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
```

Use only the vars for providers you call. Local Ollama usually needs no key if the
server is running. YAML never holds API keys — only `llm.model`, temperature, and
`max_tokens`.

### 3. Run the pipeline

```powershell
cd theory_graph
# activate venv if needed

theory-graph init --config configs\try_v2_0_1.yaml
# → creates experiments/<timestamp>_<corpus>_<prompt>_<model>_<sample>/
#    with prompt.snapshot.md, case list, per-case messages

theory-graph encode --run experiments\<that_folder>
# → writes encodings/run1..runK/*.json via LiteLLM (or skip if backend: manual)

theory-graph measure --run experiments\<that_folder>
# → validates JSON → validation/measures.csv (breadth etc. per run file)

theory-graph analyze --run experiments\<that_folder>
# → aggregates k runs → joins cases.csv → aggregated/cases.csv + analysis/results.md
```

Manual / Cursor encoding: set `encoding.backend: manual`, drop JSON into
`encodings/run{k}/`, then `measure` + `analyze`.

### 4. Where results land

| Output | Path |
|---|---|
| Frozen prompt for this run | `experiments/<run>/prompt.snapshot.md` |
| Raw encodings | `experiments/<run>/encodings/run*/` |
| Case-level IVs + DV | `experiments/<run>/aggregated/cases.csv` |
| Primary logits write-up | `experiments/<run>/analysis/results.md` |

Compare two prompt versions after both are analyzed:

```powershell
theory-graph compare --runs experiments\<run_a> --runs experiments\<run_b>
```

### 5. What analysis calculates (today)

From each case’s P→D→V JSON (median across `k` runs):

- **breadth** — premise count
- **n_domains** (modularity proxy) — domain count
- **balance**, **granularity**, truncation flags
- **GotSelected** logits — breadth (linear/quadratic), domains, word-count control
  (Battlefield reference analyses; other corpora need their own outcome column wired in)

**Not in the toolkit today:** embedding / semantic-similarity controls, inverted-U
diagnostics that used external embedding models, or Pass B taxonomy coding. Those
lived in older analyses and were not ported. If you need them again, that is a
separate feature, not part of `measure` / `analyze`.

### 6. Smoke vs full

| Goal | Config knobs |
|---|---|
| Cheap prompt check | `sample: smoke_n20`, local `ollama/…` |
| Paper-style N | `sample: full_n376`, cloud model, budget for 376 × k calls |

Reproduce published baselines (no new encoding):

```powershell
theory-graph reproduce --pipeline all
theory-graph equivalence
```

`reproduce` re-aggregates frozen `reference/` corpora into `analysis/_recomputed/`
and diffs vs shipped outputs (`PASS` = IVs within |Δ| < 1e-6). Optional live check:
`theory-graph equivalence --live --model openai/gpt-4.1` (descriptive only; offline
equivalence is the hard gate).

### Checklist for a new prompt version

1. Copy `prompts/v2_0_0.md` → `prompts/vX_Y_Z.md` and edit
2. Set `experiment.prompt_version: vX_Y_Z` in a fresh YAML
3. `init` → `encode` → `measure` → `analyze`
4. Read `analysis/results.md` and `aggregated/cases.csv`
5. Optionally `compare` against a baseline run or a `reference/` pipeline
