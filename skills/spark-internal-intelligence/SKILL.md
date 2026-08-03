---
name: spark-internal-intelligence
description: Generate a monthly technical intelligence report ("Spark核心内参") from Apache Spark developer mailing list mbox files. Use whenever the user wants to process Spark mailing list archives, download Spark dev-list emails, parse mbox files, summarize Spark releases/discussions/proposals, or produce a Spark technical newsletter. Triggers on phrases like "生成内参", "处理 mbox", "出月报", "下载 Spark 邮件", "Spark 核心内参", "Spark 技术情报", "summarize Spark mailing list", "download Spark mbox", or whenever an .mbox file from the Spark dev list needs to be turned into a report. Can fetch the mbox automatically from lists.apache.org given just a YYYY-M month.
license: MIT
compatibility: Requires Python 3.10+ with mailbox, dateutil, click, rich (see requirements.txt). Phase 0 downloads from lists.apache.org (network access needed). Optionally uses WebFetch to pull release notes and design docs.
---

# Spark 核心内参 · 生成器

Turn an Apache Spark dev-list `.mbox` archive into a polished monthly technical intelligence report in Chinese. The pipeline runs in five phases: **fetch → parse → classify → summarize → compose**. Each phase produces a numbered JSON artifact so progress is transparent and resumable.

## The Pipeline at a Glance

```
YYYY-M ──▶ (download .mbox from lists.apache.org) ──▶ input/dev_spark_apache_org_<YYYY-M>.mbox
                                                              │
.mbox ──▶ step1_threads.json        (parse + thread)
       └─▶ step2_threads_filtered.json  (filter noise)
              └─▶ step3_threads_classified.json  (bucket into 4 categories)
                     ├─▶ step4_release_summary.json  ┐
                     ├─▶ step5_discuss_summary.json  ├─▶ Spark_Internal_Inteligence_<YYYY>_<MM>.md
                     └─▶ step6_spip_summary.json     ┘
```

All artifacts land in `output/<YYYY-MM>/`. The `YYYY-MM` is derived from the first email's date in the mbox.

## Phase 0 - Fetch (optional)

If the user gives a month (e.g. `2026-7`) instead of a file path, download the mbox straight from the Apache Pony Mail archive - no browser needed. The "Download as mbox" button on the web UI just calls a backend API; `main.py --month` hits the same endpoint via `src/fetch_mbox.py` (standard-library `urllib`, no extra deps):

```bash
python3 main.py --month <YYYY-M>
```

This downloads to `input/dev_spark_apache_org_<YYYY-M>.mbox` **and** immediately runs Phase 1 (parse + filter) in one shot. So `--month` is a shorthand for "fetch then process" - you do not run Phase 1 separately after it.

The API endpoint (for reference, in case the user asks): `https://lists.apache.org/api/mbox.lua?list=dev&domain=spark.apache.org&d=<YYYY-M>`.

If the user already has a `.mbox` file, skip Phase 0 and use `--mbox <path>` in Phase 1 instead.

## Phase 1 — Parse & Filter

Run the project's CLI, which does step1 (parse + thread) and step2 (filter JIRA/vote noise) in one shot:

```bash
python3 main.py --mbox <mbox_path>
```

- Creates `output/<YYYY-MM>/` automatically
- Produces `step1_threads.json` and `step2_threads_filtered.json`
- **Capture `YYYY-MM` from stdout** — every later phase needs it

If the command fails: check `pip install -r requirements.txt` first (needs `python-dateutil`, `click`, `rich`).

## Phase 2 — Classify

Bucket the filtered threads into 4 categories by running the classifier script:

```bash
python3 src/classify_tool.py output/<YYYY-MM>/step2_threads_filtered.json output/<YYYY-MM>/step3_threads_classified.json
```

Output structure (`step3_threads_classified.json`):

```json
{
  "discuss":  [ ... full thread objects ... ],
  "release":  [ ... ],
  "spip":     [ ... ],
  "others":   [ ... ]
}
```

Each thread object gains two fields: `doc_links` (Google Doc URLs found in the body) and `doc_content` (empty placeholder for Phase 3).

The classification rules (priority: release > spip > discuss > others) are defined in **[references/classification-rules.md](references/classification-rules.md)**. Read that file if a thread's category is ambiguous or the user asks why something was bucketed a certain way.

## Phase 3 — Summarize (parallel)

Generate three independent summaries from the classified threads. These have **no dependencies on each other**, so run them concurrently — either with three parallel `Agent` subagent calls (preferred when available) or sequentially.

For each category, read `step3_threads_classified.json`, extract only that category's array, and produce the corresponding summary file. The exact output schema, scoring rubrics, and per-field guidance are in **[references/summary-schemas.md](references/summary-schemas.md)**.

| Category | Output | Reference section |
|----------|--------|-------------------|
| release  | `step4_release_summary.json` | "Release Summarizer" |
| discuss  | `step5_discuss_summary.json` | "Discuss Summarizer" |
| spip     | `step6_spip_summary.json`    | "SPIP Summarizer" |

**Why parallel:** the three summaries are the most token-heavy work in the pipeline (each reads the full classified JSON). Running them as subagents keeps each one's context focused on a single category and cuts total wall time.

### Parallel subagent pattern

If `Agent` tool is available, dispatch all three in **one message** (they run concurrently):

```
Agent (release): "Read output/<YYYY-MM>/step3_threads_classified.json, process only the 'release' array per references/summary-schemas.md §Release Summarizer, write step4_release_summary.json, return the path + top highlight."
Agent (discuss):  "Read output/<YYYY-MM>/step3_threads_classified.json, process only the 'discuss' array per references/summary-schemas.md §Discuss Summarizer, write step5_discuss_summary.json, return the path + top highlight."
Agent (spip):     "Read output/<YYYY-MM>/step3_threads_classified.json, process only the 'spip' array per references/summary-schemas.md §SPIP Summarizer, write step6_spip_summary.json, return the path + top highlight."
```

### WebFetch usage (release & spip only)

- **Release**: if a thread links to release notes (`spark.apache.org/releases/...`, `github.com/.../releases/tag/...`), use `WebFetch` to pull the actual changelog — the email body usually lacks detail.
- **SPIP**: if `doc_links` contains a Google Doc, use `WebFetch` to fetch it. The email often omits the full design; the doc has it, plus comments that feed the `community_discussion` section when the mailing list itself is quiet.
- **Discuss**: rarely needs WebFetch — the email thread is usually self-contained.

## Phase 4 — Compose the Report

Read the three summary JSONs and synthesize the final Markdown report. You are a **senior Spark kernel architect** and a **master technical writer** in one role: translate, polish, and add editorial insight.

**Read [references/report-template.md](references/report-template.md)** for the exact per-section format with literal examples. That file is authoritative for output structure.

### Report skeleton

```markdown
# Spark核心内参：<YYYY>年<MM>月：<Headline>

### 航向追踪
<Core releases — from step4 where summary tags [Core]>

---

### 前线研讨
<Discussions — from step5>

---

### 方案思辨
<SPIPs — from step6>

---

### 生态拓扑
<Ecosystem releases — from step4 where summary tags [Ecosystem]>
```

### Writing rules

1. **Translate** into fluent professional Chinese; **keep technical terms in English** (Shuffle, Catalyst, Tungsten, Codegen, Kubernetes, SPIP, PR, CVE, HPA).
2. **Star conversion**: `score.value` (1-5) → that many ⭐; `score.total` (3-15) → `round(total/15*5)` stars. Never show raw numbers like `(10/15)`.
3. **Curate**: split releases into Core vs Ecosystem using the `[Core]`/`[Ecosystem]` tag the Release Summarizer appended to each `summary` field.
4. **Editor's note (编者按)**: every item ends with one — take the `summary` field and weave in architectural insight.
5. **No data loss**: every release, discussion, and SPIP from the summary JSONs must appear in the report.

Save to `output/<YYYY-MM>/Spark_Internal_Inteligence_<YYYY>_<MM>.md`.

## When the User Gives Only a Partial Task

Not every invocation runs the full pipeline. Detect which phase the user wants:

| User says | Run |
|-----------|-----|
| "生成内参" / "出月报" / "处理 2026-7" | Full pipeline (Phases 0-4) |
| "处理这个 mbox" / 已有 mbox 文件 | Full pipeline (Phases 1-4) |
| "下载 Spark 邮件" / "下载 mbox" / "fetch mbox" | Phase 0 only (download, no parse) |
| "解析 mbox" / "parse threads" | Phase 1 only |
| "分类线程" / "classify threads" | Phase 2 only (needs step2 input) |
| "摘要 release" / "分析讨论" / "step4" | Phase 3, one category |
| "写报告" / "合成内参" | Phase 4 only (needs step4-6) |

When resuming mid-pipeline, check which `stepN_*.json` files already exist in `output/<YYYY-MM>/` and skip the phases whose outputs are present and non-empty — don't redo work.

## Input

| Parameter | Description | Example |
|-----------|-------------|---------|
| `month` | YYYY-M to download from lists.apache.org | `2026-7`, `2025-10` |
| `mbox_path` | Path to an existing `.mbox` file (alternative to `month`) | `examples/2025-10/dev_spark_apache_org_2025-10.mbox` |

## Output

Final deliverable: `output/<YYYY-MM>/Spark_Internal_Inteligence_<YYYY>_<MM>.md`
Intermediate artifacts: `step1_threads.json` through `step6_spip_summary.json` in the same directory.

## Error Handling

- **Phase 0 download fails**: usually a network issue or the month has no archives yet. Check the URL `https://lists.apache.org/api/mbox.lua?list=dev&domain=spark.apache.org&d=<YYYY-M>` in a browser.
- **Missing mbox**: report the path error to the user; do not start Phase 1.
- **Phase 1 fails**: usually a dependency gap (`pip install -r requirements.txt`) or malformed mbox. Don't proceed.
- **Phase 3 subagent fails**: the other two are independent — finish what you can, report which category failed.
- **Phase 4 fails but Phase 3 succeeded**: tell the user the JSON summaries are ready and Phase 4 can be retried alone.

## Reference Files

- **[references/classification-rules.md](references/classification-rules.md)** — Phase 2 rules: priority order, per-category matching criteria, edge cases. Read when a thread's category is ambiguous.
- **[references/summary-schemas.md](references/summary-schemas.md)** — Phase 3 schemas: output fields, scoring rubrics, WebFetch guidance for each of the three summarizers.
- **[references/report-template.md](references/report-template.md)** — Phase 4 format: per-section templates with literal examples, star conversion, Core/Ecosystem split.
