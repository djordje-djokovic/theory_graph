# theory_graph

Turn startup pitch transcripts into structured data (lists of **premises**, optional tags, optional groupings) and run simple statistical analysis.

You do **not** need to edit Python code. Everything is driven by:

1. **Prompt files** (instructions for the AI) in `prompts/`
2. **Config files** (settings for one experiment) in `configs/`
3. **Commands** in the terminal: `init` → `encode` → `measure` → `analyze`

---

## Quick start (copy and paste)

**One-time setup** (do this once on your computer):

```powershell
cd theory_graph
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

Open `.env` in a text editor and add an API key (for OpenAI, Anthropic, etc.), **or** skip this if you use a local Ollama model (see below).

**Run a small test** (20 pitches, uses an AI API):

```powershell
copy configs\examples\smoke_openai.yaml configs\my_first_run.yaml
```

Open `configs\my_first_run.yaml` and change `run_id:` to something unique, e.g. `my_first_run`.

The encode step uses **`-p`** to pick which AI steps to run (comma-separated, no spaces):

| Flag | Meaning |
|---|---|
| `premises` | Extract the main claims from each pitch (always start here) |
| `dfv` | Tag each claim: **D**esirability / **F**easibility / **V**iability / Other |
| `domains` | Group claims into strategic themes (optional third step) |

Then run these lines (comments explain each step):

```powershell
# Create the experiment folder (do once per run_id)
theory-graph init --config configs\my_first_run.yaml

# Call the AI for each pitch:
#   premises = list claims  |  dfv = D/F/V tags on those claims
# To also run the domains step, use: -p premises,dfv,domains
theory-graph encode --run my_first_run -p premises,dfv

# Check JSON + build the full analysis spreadsheet (take this CSV to Excel/R)
theory-graph measure --run my_first_run

# Run regressions listed in your config (optional if you only want the CSV)
theory-graph analyze --run my_first_run
```

**Simplest first try:** use `-p premises` only in the encode line above; add `,dfv` or `,domains` later when you want those steps.

Each command prints a plain-English summary and a **Next step:** line with the exact command to run.

**Results:**

- `experiments\my_first_run\aggregated\dataset.csv` — **main handoff file** (all variables, one row per pitch)
- `experiments\my_first_run\analysis\results.md` — regression output (if you ran `analyze`)

---

## What each command does

| Command | Plain English |
|---|---|
| `init` | Creates a new experiment folder from your config. **Run once per experiment.** |
| `encode` | Sends transcripts to the AI and saves JSON answers. Slow/expensive step. |
| `measure` | Checks JSON + builds **`aggregated/dataset.csv`** (full analysis spreadsheet). |
| `analyze` | Runs regressions from your config → **`analysis/results.md`**. Optional. |
| `status` | Shows encode progress (done / pending per pass). |

---

## The three encoding steps (passes)

Each pitch can go through up to three AI steps. The names after **`-p`** in commands match the first column here:

| Name in commands | Prompt file | What the AI does |
|---|---|---|
| `premises` | `prompts/v2_1_0_premises.md` | List the main claims/premises in the pitch |
| `dfv` | `prompts/v2_1_0_dfv.md` | Tag each premise: **D**esirability / **F**easibility / **V**iability / Other |
| `domains` | `prompts/v2_1_0_domains.md` | Group premises into strategic “domains” (themes) |

**Order matters:** `dfv` and `domains` need `premises` done first (they read the premise list from step 1).

You can run all steps in **one command** (comments optional):

```powershell
# premises first, then dfv tags, then domain groupings — order in -p does not matter
theory-graph encode --run my_first_run -p premises,dfv,domains
```

The order on the command line does not matter — the tool always runs premises first.

---

## Step-by-step: your first experiment

### Step 1 — Pick a starter config

Copy an example (do not edit the originals in `configs/examples/`):

| File | Good for |
|---|---|
| `smoke_openai.yaml` | OpenAI (needs `OPENAI_API_KEY` in `.env`) |
| `smoke_anthropic.yaml` | Anthropic |
| `smoke_ollama_local.yaml` | Free local model (needs Ollama running) |
| `smoke_manual.yaml` | No AI — you paste JSON files yourself |

```powershell
copy configs\examples\smoke_openai.yaml configs\my_first_run.yaml
```

### Step 2 — Edit the config (minimal)

Open `configs\my_first_run.yaml` in any text editor. Change at least:

```yaml
experiment:
  run_id: my_first_run    # pick a new name every time you change something important
```

**Important:** If a folder `experiments/my_first_run/` already exists, `init` will refuse. Pick a new `run_id` (e.g. `my_first_run_v2`).

Other useful fields (defaults are fine for a first try):

```yaml
  sample: smoke_n20       # 20 pitches (use full_n376 for everything)
llm:
  model: "openai/gpt-4.1"   # which AI to call
encoding:
  backend: api            # api = call AI | manual = you write JSON
  run_passes: [premises]  # optional: only encode premises by default
```

### Step 3 — Init (create the experiment folder)

```powershell
theory-graph init --config configs\my_first_run.yaml
```

This creates `experiments/my_first_run/` with:

- `config.snapshot.yaml` — frozen copy of your settings (used from now on)
- `cases.csv` — list of pitches in this run
- `messages/` — ready-made prompts per pitch (for manual review)
- empty `encodings/` folders

**After init, you do not use `--config` again.** All later commands use the snapshot inside the experiment folder.

### Step 4 — Encode (call the AI)

Encode everything at once:

```powershell
theory-graph encode --run my_first_run -p premises,dfv,domains
```

Or in stages (inspect premises before continuing):

```powershell
theory-graph encode --run my_first_run -p premises
theory-graph status --run my_first_run
theory-graph encode --run my_first_run -p dfv,domains
```

If you started with **premises only** in the config and later run `-p dfv` or `-p domains`, those steps are added automatically — no extra setup command.

Check progress anytime:

```powershell
theory-graph status --run my_first_run
```

**Re-do premises** (also clears dfv/domains so they stay in sync):

```powershell
theory-graph encode --run my_first_run -p premises --force
theory-graph encode --run my_first_run -p dfv,domains
```

### Step 5 — Measure (build dataset.csv)

```powershell
theory-graph measure --run my_first_run
```

This writes:

- **`aggregated/dataset.csv`** — one row per pitch: AI variables + outcome + controls + similarity controls + validation flags (+ optional embeddings)
- **`validation/measures.csv`** — technical detail per JSON file (for debugging)

Similarity columns (`premise_sim_mean`, `domain_sep`, …) are recomputed from the encoding JSON each time you run `measure`. Re-run after re-encoding or adding the domains pass (`domain_sep` needs domains).

You can stop here and analyze in Excel, R, or Stata using `dataset.csv`.

### Step 6 — Analyze (optional regressions)

```powershell
theory-graph analyze --run my_first_run
```

Runs the models in your config → **`analysis/results.md`**.

You can skip this step if you only wanted the CSV.

---

## Changing the prompt (instructions to the AI)

Prompts live as markdown files in `prompts/`.

**Do not edit the published old versions** (`v1_3_2.md`, `v1_5_1.md`). Copy and rename instead:

```powershell
copy prompts\v2_1_0_premises.md prompts\my_premises_v1.md
# edit my_premises_v1.md in a text editor
```

Point your config at the new file (filename **without** `.md`):

```yaml
passes:
  - name: premises
    prompt_version: my_premises_v1
    k_runs: 3
```

Use a **new** `run_id` when you init again.

---

## Config file cheat sheet

Your config is YAML. Only a few fields matter day to day:

| Field | What to put |
|---|---|
| `experiment.run_id` | Unique name for this experiment → folder `experiments/<run_id>/` |
| `experiment.sample` | `smoke_n20` (small test) or `full_n376` (full dataset) |
| `experiment.corpus` | Usually `startup_battlefield` (bundled data) |
| `passes` | Which steps exist and which prompt file each uses |
| `encoding.run_passes` | Default steps for bare `encode` (omit = all listed passes) |
| `encoding.backend` | `api` or `manual` |
| `llm.model` | AI model string, e.g. `openai/gpt-4.1`, `ollama/qwen2.5:14b` |
| `dataset.outcome` | Outcome column from corpus data, e.g. `GotSelected` |
| `dataset.join_columns` | Extra columns to pull from corpus `cases.csv` (defaults are fine) |
| `dataset.similarities.enabled` | `true` by default — TF-IDF cosine controls (`premise_sim_mean`, `domain_sep`, …) |
| `dataset.embeddings.enabled` | `false` by default; set `true` to add `emb_0`, `emb_1`, … columns |
| `analysis.preset` | `battlefield` = built-in models; `custom` = use `analysis.models` below |
| `analysis.models` | List of `{name, formula}` regressions (statsmodels syntax) |

**API keys** go in `.env`, never in the YAML file.

Example with all three passes declared but only premises encoded first:

```yaml
experiment:
  run_id: my_staged_run
  corpus: startup_battlefield
  sample: smoke_n20

passes:
  - name: premises
    prompt_version: v2_1_0_premises
    k_runs: 3
  - name: dfv
    prompt_version: v2_1_0_dfv
    k_runs: 1
    requires: premises
  - name: domains
    prompt_version: v2_1_0_domains
    k_runs: 1
    requires: premises

llm:
  model: "openai/gpt-4.1"
encoding:
  backend: api
  run_passes: [premises]

dataset:
  outcome: GotSelected
  similarities:
    enabled: true
    method: tfidf
  embeddings:
    enabled: false

analysis:
  preset: battlefield    # built-in regressions; or preset: custom + models: [...]
  outcome: GotSelected
```

**Custom regressions** (`preset: custom`):

```yaml
analysis:
  preset: custom
  outcome: GotSelected
  models:
    - name: Simple breadth model
      formula: "GotSelected ~ breadth_z + word_count_z"
    - name: Quadratic breadth
      formula: "GotSelected ~ breadth_z + I(breadth_z**2) + word_count_z"
      when: varies:breadth_z
```

Use `when: column:n_domains` or `when: varies:truncated` to skip a model when a column is missing or constant.

---

## Manual mode (no API)

For `smoke_manual.yaml` or `backend: manual`:

1. `init` creates message files under `experiments/<run>/messages/`
2. You (or someone else) produce JSON and save to:
   `experiments/<run>/encodings/premises/run1/pilot-123.json` (etc.)
3. `theory-graph encode --run my_run -p dfv,domains` registers later passes (writes message files; no API call)
4. Then run `measure` (builds `dataset.csv`); optionally `analyze`

---

## Useful encode options

| What you want | Command |
|---|---|
| Encode default steps from config | `theory-graph encode --run my_run` |
| Encode specific steps | `theory-graph encode --run my_run -p premises,dfv` |
| Encode all declared steps | `theory-graph encode --run my_run --all` |
| Re-do a step (and clear dependent steps) | `theory-graph encode --run my_run -p premises --force` |
| Check progress | `theory-graph status --run my_run` |

**Tip:** Use commas in one `-p` flag: `-p premises,dfv,domains`.  
`-p premises dfv domains` (spaces only) does **not** work in PowerShell.

---

## Where files live

```
theory_graph/
├── prompts/              ← AI instruction files (markdown)
├── configs/examples/     ← copy these to configs/my_run.yaml
├── data/corpora/         ← pitch transcripts and sample lists
├── experiments/          ← one folder per run_id (your outputs)
│   └── my_first_run/
│       ├── config.snapshot.yaml
│       ├── encodings/premises/run1/*.json
│       ├── validation/measures.csv   ← debug: per-json validation
│       ├── aggregated/dataset.csv    ← main export (all variables)
│       └── analysis/results.md       ← regressions (optional)
└── reference/            ← published baseline runs (read-only)
```

---

## Local model (Ollama, no cloud key)

1. Install [Ollama](https://ollama.com) and pull a model
2. Use `configs/examples/smoke_ollama_local.yaml`
3. In `.env`: `OLLAMA_BASE_URL=http://localhost:11434`

---

## Common problems

| Problem | Fix |
|---|---|
| `run already exists` | Change `run_id` in your YAML to a new name |
| `cannot encode dfv: run premises first` | Run `-p premises` first, or include premises in the same command |
| `run not found` | Use the `run_id` name (`my_first_run`) or full path (`experiments/my_first_run`) |
| Encode skips everything | Files already exist; add `--force` to redo |
| API errors | Check `.env` keys and `llm.model` in the snapshot |

---

## Costs and sample size

- `smoke_n20` = 20 pitches — use this to learn the tool and test prompt wording
- `full_n376` = full dataset — use only when you are ready (many API calls)

Rough cost: each pitch × each pass × `k_runs` (often 3 for premises) = number of AI calls.  
Example: 20 pitches × (3 premise runs + 1 dfv) ≈ 80 calls for a small smoke test.

---

## For researchers (optional reading)

**What analysis produces:** premise count (**breadth**) from the premises step; optional composition tags from dfv; optional domain counts from domains. See `experiments/<run>/analysis/results.md`.

**Before publishing:** human-code a random subsample and report agreement with the AI. The pipeline checks JSON shape, not whether coding is “correct.”

**Reproduce bundled baselines** (developers / CI):

```powershell
theory-graph equivalence
theory-graph reproduce --pipeline all
theory-graph smoke
```

`equivalence` and `reproduce` check published v1.3/v1.5 baselines. `smoke` runs the **v2.1 pipeline** on 3 synthetic cases:

| Step | CLI / behaviour tested |
|---|---|
| init | premises-only experiment |
| measure | corpus join, similarities, premises IVs |
| encode -p dfv | staged pass registration (manual) |
| measure | DFV composition columns, no domains yet |
| encode -p domains | second staged pass |
| measure | full join: breadth + dfv + domains + similarities |
| analyze | battlefield preset (M1–M6) |
| status | done/pending counts |
| force -p dfv / domains / premises | selective vs full downstream clear |
| encode --all | all declared passes |
| analyze-only | edit snapshot analysis, re-run analyze |
| custom analysis preset | one formula on synthetic data |
| guard rails | duplicate init, encode before premises, empty measure |
| compare | two runs, matched cases |

All three should print `PASS`.

**Before a live API run:**

```powershell
python -m theory_graph.cli smoke
python -m theory_graph.cli reproduce --pipeline all
python -m theory_graph.cli equivalence
```

Then start with `configs/examples/smoke_openai.yaml` (or Ollama/manual) on `smoke_n20` before `full_n376`.

**Compare two finished runs:**

```powershell
theory-graph compare --runs run_a --runs run_b
```

**Add a new dataset:** see `data/corpora/README.md`.

**Prompt history:** see `prompts/registry.md`.

---

## Command reference

```powershell
theory-graph init --config configs\my_run.yaml
theory-graph encode --run my_run -p premises,dfv,domains
theory-graph measure --run my_run
theory-graph analyze --run my_run
theory-graph status --run my_run
theory-graph --help
```
