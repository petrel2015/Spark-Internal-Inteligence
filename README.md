# Spark Internal Intelligence

English | [中文](./README.zh.md)

[![AI Powered](https://img.shields.io/badge/Powered%20by-AI-blue.svg)](https://agentskills.io/specification)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

**Spark Internal Intelligence** turns Apache Spark developer mailing-list archives (`.mbox`) into a polished monthly technical report in Chinese. The workflow is packaged as a single [Agent Skills](https://agentskills.io/specification)-compliant skill that runs in any supporting agent (ZCode, Claude Code, Hermes, etc.).

---

## For AI Agents (read this first)

> If you are an AI agent whose user shared this repository with you and asked you to install and run it, follow the steps below exactly. They are self-contained — no need to ask the user anything unless a command fails.

### What this project does

It parses a Spark `dev` mailing-list `.mbox` file, classifies threads into Release / Discuss / SPIP, summarizes each category, and composes a Chinese Markdown report. A sample input and its full output are already in the repo (`examples/2025-10/`).

### Step 1 — Install

```bash
git clone <this-repo-url>   # or: the user already cloned it, skip this
cd Spark-Internal-Inteligence
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` contains: `click`, `python-dateutil`, `rich`. Python 3.10+ is required.

### Step 2 — Verify the install

Run the parser on the bundled sample mbox. Success = exit code 0 and two JSON files appear under `output/2025-10/`:

```bash
python3 main.py --mbox examples/2025-10/dev_spark_apache_org_2025-10.mbox
```

Expected stdout ends with: `Successfully saved filtered JSON to: output/2025-10/step2_threads_filtered.json`.

You can also test the auto-download path (Phase 0) - this fetches a month directly from lists.apache.org:

```bash
python3 main.py --month 2026-7
```

Both `--mbox` and `--month` produce the same result (a parsed, filtered mbox). `--month` just downloads it for you first.

### Step 3 — Run the full pipeline (the skill)

**The pipeline has five phases: fetch -> parse -> classify -> summarize -> compose.** Phases 0-2 are deterministic Python scripts. Phases 3-4 require an LLM and are driven by the skill definition at `skills/spark-internal-intelligence/SKILL.md`.

**One-command path (recommended for automation):** if you know the YYYY-M, `--month` does everything except the LLM phases:

```bash
python3 main.py --month 2026-7   # Phase 0 (download) + Phase 1-2 (parse + filter)
```

Then hand off to the skill for Phases 3-4 (summarize + compose).

**If you are an Agent Skills-compatible agent:** load the skill `spark-internal-intelligence` and give it the mbox path:

```
/spark-internal-intelligence process examples/2025-10/dev_spark_apache_org_2025-10.mbox
```

The skill will:
1. Run `python3 main.py --mbox <path>` (Phase 1-2: parse + filter)
2. Run `python3 src/classify_tool.py <step2> <step3>` (Phase 2: classify)
3. Read `references/summary-schemas.md` and generate `step4-6_*_summary.json` (Phase 3: summarize — three categories can run in parallel)
4. Read `references/report-template.md` and compose the final report (Phase 4: compose)

**Final deliverable:** `output/<YYYY-MM>/Spark_Internal_Inteligence_<YYYY>_<MM>.md`

**If you are a general-purpose agent without skill loading:** open `skills/spark-internal-intelligence/SKILL.md` and follow the four phases it describes. The `references/` files contain the exact schemas, scoring rubrics, and output templates.

### Step 4 — Report back to the user

Tell the user:
1. The absolute path of the final report.
2. A one-line highlight of the month's most important item (from the report's top headline).

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | `pip install -r requirements.txt` didn't finish — rerun in the active venv. |
| `main.py --month` fails to download | Network issue or that month has no archives yet. Test the URL `https://lists.apache.org/api/mbox.lua?list=dev&domain=spark.apache.org&d=YYYY-M` in a browser. |
| `main.py` exits with no threads | The mbox file is empty or malformed; verify it's a Spark dev-list export. |
| Phase 3-4 produce no output | The agent doesn't support the Agent Skills spec; follow `SKILL.md` manually as a general-purpose agent. |

---

## For Humans

### Why this exists

The Spark dev mailing list is the source of truth for where the project is heading — release plans, design debates (SPIPs), and tricky bug discussions. But it's high-volume and hard to scan. This project distills a month of it into a readable briefing with editorial insight.

### The five-phase pipeline

| Phase | What it does | How | Output |
| :--- | :--- | :--- | :--- |
| **0. Fetch** | Download the mbox from lists.apache.org | `main.py --month` (Python) | `input/dev_spark_apache_org_<YYYY-M>.mbox` |
| **1. Parse & Filter** | Thread the mbox, drop JIRA/vote noise | `main.py` (Python) | `step1_threads.json`, `step2_threads_filtered.json` |
| **2. Classify** | Bucket into Release / Discuss / SPIP / Others | `src/classify_tool.py` (Python) | `step3_threads_classified.json` |
| **3. Summarize** | Deep-dive each category with expert scoring | LLM (skill) | `step4-6_*_summary.json` |
| **4. Compose** | Synthesize a Chinese Markdown report | LLM (skill) | `Spark_Internal_Inteligence_<YYYY>_<MM>.md` |

Phases 1-2 are deterministic and reproducible; Phases 3-4 are LLM-driven and defined by the skill. Every phase writes a numbered JSON artifact to `output/<YYYY-MM>/`, so you can inspect intermediate state and resume from any point.

### Directory structure

```
Spark-Internal-Inteligence/
├── main.py                    # CLI entry: fetch + parse + filter (Phase 0-2)
├── src/
│   ├── mbox_parser.py         # mbox -> threaded JSON
│   ├── topic_filter.py        # drop noise (unsubscribe, [VOTE], empty)
│   ├── classify_tool.py       # bucket threads (Phase 2)
│   └── fetch_mbox.py          # download mbox from lists.apache.org (Phase 0)
├── skills/
│   └── spark-internal-intelligence/
│       ├── SKILL.md           # the skill: orchestrates Phase 0-4
│       └── references/        # progressive disclosure
│           ├── classification-rules.md   # Phase 2 rules
│           ├── summary-schemas.md        # Phase 3 schemas + rubrics
│           └── report-template.md        # Phase 4 report format
├── examples/2025-10/          # bundled sample (mbox + full pipeline output)
├── input/                     # .mbox downloads land here (gitignored)
└── output/                    # generated artifacts, by YYYY-MM (gitignored)
```

### Getting mbox files

**Automatic (preferred):** give `main.py` a YYYY-M month and it downloads straight from the Apache Pony Mail archive - no browser needed:

```bash
python3 main.py --month 2026-7
```

**Manual:** browse the [Apache Spark dev list archive](https://lists.apache.org/list?dev@spark.apache.org:2026-7), click the "Download as mbox" button, and place the exported `.mbox` file in `input/`.

### Sample output

The repo ships a complete sample for October 2025 — see `examples/2025-10/Spark_Internal_Inteligence_2025_10.md` for what the final report looks like, and the `step1-6` JSONs for intermediate state.

### License

MIT — see [LICENSE](./LICENSE).
