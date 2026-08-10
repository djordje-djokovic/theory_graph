# theory_graph

Turn startup pitch transcripts into numbers you can analyze (theory **breadth**, optional DFV composition, optional domain groupings), then run regressions.

**Coauthors (non-coding):** open [`reference/README.md`](reference/README.md). Finished spreadsheets and regression reports for the n=375 GPT-4o-mini and Qwen runs are there. No install or API key needed.

---

## How the pipeline fits together

Think of two phases:

| Phase | Commands | What it does | When you use it |
|---|---|---|---|
| **1. Encoding** (expensive) | `init` → `encode` | Calls an LLM on each pitch and saves structured JSON | Only when you need **new** AI coding (new model, new prompt, new sample) |
| **2. Analysis** (cheap) | `measure` → `analyze` | Turns JSON into a spreadsheet, then runs regressions | Whenever you want results, new models, or a re-check |

**Most people working on the paper should start with analysis**, not encoding.

- Published confirmatory outputs live under `reference/` (CSV + regression tables already built).
- Raw LLM JSON under `experiments/` is local / optional; it is not required to re-run stats on the published runs.
- Encoding is what *creates* those variables. Once you have `aggregated/dataset.csv`, you can open it in Excel / R / Stata or re-run `analyze` many times without calling any LLM again.

```
Transcripts ──encode──► JSON encodings ──measure──► dataset.csv ──analyze──► results.md
                              ▲                            │
                              │                            └── also open in Excel / R / Stata
                         (slow, costs $ / hours)
```

---

## Quick start: run the analysis (no re-encoding)

**One-time setup** (once per computer):

```powershell
cd theory_graph
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

You do **not** need an API key for this path.

**Re-run regressions on the published n=375 results:**

```powershell
theory-graph analyze --run reference/full_n375_k3_v211_gpt4o_mini
theory-graph analyze --run reference/full_n375_k3_v211_qwen3_32b
```

That reads `aggregated/dataset.csv` + `config.snapshot.yaml` and writes / refreshes `analysis/results.md`.

**Or skip the CLI:** open these files directly:

| File | What it is |
|---|---|
| `reference/.../aggregated/dataset.csv` | One row per pitch: breadth, DFV, domains, outcome, controls |
| `reference/.../analysis/results.md` | Logit tables already computed |
| `reference/.../validation/reliability_report.md` | Within-model agreement (Krippendorff α, etc.) |

See [`reference/README.md`](reference/README.md) for a plain-language tour of columns and takeaways.

### Change the regressions (still no encoding)

Edit the analysis block in the run’s `config.snapshot.yaml` (or copy the folder and edit the copy), then run `analyze` again.

Built-in battlefield models (`analysis.preset: battlefield`) cover breadth linear/quadratic, DFV composition, domains, and common controls.

Custom example:

```yaml
analysis:
  preset: custom
  outcome: GotSelected
  models:
    - name: Simple breadth model
      formula: "GotSelected ~ breadth_z + word_count_z"
    - name: Quadratic breadth
      formula: "GotSelected ~ breadth_z + I(breadth_z**2) + word_count_z"
```

Formulas use [statsmodels](https://www.statsmodels.org/) syntax. Columns must exist in `dataset.csv`.

---

## What encoding is for (use later, when needed)

**Encoding** = ask an LLM to read each transcript and write structured codes (premises, optional DFV tags, optional domains).

Use encoding only when you need **new** machine coding, for example:

- try a different LLM (`llm.model` in the config)
- change the codebook / prompt
- expand or shrink the sample
- add a pass you do not have yet (e.g. DFV after premises-only)

Do **not** re-encode just to change a regression. Change the analysis config and run `analyze`.

| Encode pass (`-p`) | What the AI produces | Typical research use |
|---|---|---|
| `premises` | List of claims → **breadth** | Confirmatory IV (Prop 1) |
| `dfv` | Tag each claim D / F / V / Other | Composition / balance (Prop 2) |
| `domains` | Group claims into themes | Exploratory modularity |

`dfv` and `domains` need `premises` first. Passes are independent after that: you can encode premises today and add DFV later without redoing premises.

Rough cost: pitches × passes × `k_runs` (often 3 for premises).  
Examples: `smoke_n20` for learning; `full_n375` for confirmatory work (many API calls; GPT-4o-mini premises-scale runs were on the order of a few dollars and a couple of hours).

---

## Full pipeline (only if you are encoding)

You do **not** need to edit Python. Day to day you use:

1. **Prompt files** in `prompts/` (instructions to the AI)
2. **Config files** in `configs/` (YAML = plain-text settings checklist)
3. **Commands:** `init` → `encode` → `measure` → `analyze`

### One-time setup for API / local LLM

```powershell
cd theory_graph
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

Add an API key to `.env` for OpenAI / Anthropic, **or** use Ollama locally (see below).

### Minimal encode → measure → analyze

```powershell
copy configs\examples\smoke_openai.yaml configs\my_first_run.yaml
# edit run_id in that YAML

theory-graph init --config configs\my_first_run.yaml
theory-graph encode --run my_first_run -p premises
theory-graph measure --run my_first_run
theory-graph analyze --run my_first_run
```

| Command | Plain English |
|---|---|
| `init` | Creates `experiments/<run_id>/` from your config (once per run) |
| `encode` | Calls the AI; writes JSON under `encodings/` (slow / costly) |
| `measure` | Validates JSON + builds **`aggregated/dataset.csv`** |
| `analyze` | Runs regressions → **`analysis/results.md`** |
| `status` | Shows encode progress |

After `init`, later commands use the frozen `config.snapshot.yaml` inside the experiment folder (not your original YAML).

**Staged encoding** (inspect premises before DFV/domains):

```powershell
theory-graph encode --run my_first_run -p premises
theory-graph status --run my_first_run
theory-graph encode --run my_first_run -p dfv,domains
theory-graph measure --run my_first_run
theory-graph analyze --run my_first_run
```

Use commas in `-p`: `-p premises,dfv,domains`. Spaces alone do not work in PowerShell.

**Re-do a pass** (clears dependent passes when needed):

```powershell
theory-graph encode --run my_first_run -p premises --force
theory-graph encode --run my_first_run -p dfv,domains
theory-graph measure --run my_first_run
```

### Starter configs

Copy from `configs/examples/` (do not edit the originals):

| File | Good for |
|---|---|
| `smoke_openai.yaml` | OpenAI API |
| `smoke_anthropic.yaml` | Anthropic |
| `smoke_ollama_local.yaml` | Free local model (Ollama) |
| `smoke_manual.yaml` | No AI — you paste JSON yourself |

Confirmatory sample configs (n=375):

- `configs/full_n375_k3_v211_gpt4o_mini_premises.yaml`
- `configs/full_n375_k3_v211_premises.yaml` (Qwen / local)

### Config cheat sheet

| Field | Meaning |
|---|---|
| `experiment.run_id` | Folder name under `experiments/` |
| `experiment.sample` | `smoke_n20` or `full_n375` |
| `llm.model` | e.g. `openai/gpt-4o-mini`, `ollama/qwen3:32b` |
| `passes` | Which encode steps exist + which prompt file |
| `encoding.k_runs` / per-pass `k_runs` | How many independent AI repeats |
| `dataset.outcome` | e.g. `GotSelected` |
| `analysis.preset` | `battlefield` (built-in) or `custom` |

API keys go in `.env`, never in the YAML.

### Changing the prompt

Do not edit published codebook versions in place. Copy and rename:

```powershell
copy prompts\v2_1_1_premises.md prompts\my_premises_v1.md
```

Point the config at the new name (without `.md`) and use a **new** `run_id`.

### Manual mode (no API)

1. `init` writes message files under `messages/`
2. Save human/LLM JSON under `encodings/<pass>/run{k}/`
3. `measure` then optional `analyze`

### Local model (Ollama)

1. Install [Ollama](https://ollama.com) and pull a model  
2. Use `configs/examples/smoke_ollama_local.yaml`  
3. In `.env`: `OLLAMA_BASE_URL=http://localhost:11434`

---

## Where files live

```
theory_graph/
├── prompts/                 ← codebook / AI instructions
├── configs/                 ← experiment settings (YAML)
├── data/corpora/            ← transcripts + sample lists + cases.csv
├── reference/               ← published analysis handoffs (use these first)
│   ├── README.md
│   ├── full_n375_k3_v211_gpt4o_mini/
│   └── full_n375_k3_v211_qwen3_32b/
└── experiments/             ← local runs (often gitignored encodings)
    └── <run_id>/
        ├── config.snapshot.yaml
        ├── encodings/…          ← raw LLM JSON (from encode)
        ├── aggregated/dataset.csv
        ├── analysis/results.md
        └── validation/…
```

---

## Common problems

| Problem | Fix |
|---|---|
| `run already exists` | Change `run_id` and `init` again |
| `missing …/dataset.csv` | Run `measure`, or point `--run` at a `reference/…` folder that already has the CSV |
| `cannot encode dfv: run premises first` | Encode `-p premises` first |
| Encode skips everything | Outputs exist; add `--force` to redo |
| API errors | Check `.env` and `llm.model` in the snapshot |

---

## Compare two finished runs

```powershell
theory-graph compare --runs run_a --runs run_b
```

---

## Developer checks (CI / before a live API run)

```powershell
theory-graph smoke
theory-graph reproduce --pipeline all
theory-graph equivalence
```

All three should print `PASS`. Details of what `smoke` covers are in the toolkit tests; for paper work, prefer `reference/` + `analyze`.

**Add a new dataset:** see `data/corpora/README.md`.  
**Prompt history:** see `prompts/registry.md`.

---

## Command reference

```powershell
# Analysis on published results (no LLM)
theory-graph analyze --run reference/full_n375_k3_v211_gpt4o_mini

# Full encode path
theory-graph init --config configs\my_run.yaml
theory-graph encode --run my_run -p premises,dfv,domains
theory-graph measure --run my_run
theory-graph analyze --run my_run
theory-graph status --run my_run
theory-graph --help
```
