# Classification Rules

Phase 2 buckets each filtered thread into exactly one of four categories. The `src/classify_tool.py` script implements these rules; this document explains them so ambiguous cases can be reasoned about.

## Priority Order

Check in this order - first match wins:

```
release > spip > discuss > others
```

A thread that matches both `release` and `spip` criteria goes to `release`. This prevents a release announcement that mentions a SPIP from being misfiled.

## Category: release

**Hard rule**: the subject MUST contain the string `announce` (case-insensitive).

- Match: `[ANNOUNCE] Apache Spark 3.5.7 released`, `Spark 4.1.0-preview3 announcement`
- No match: a subject that only says "release" or mentions a version number but lacks `announce`

Why so strict? The Spark dev list has many threads that *discuss* releases (planning, voting, retrospective) without being the official announcement. Only official announcements belong in the "航向追踪/生态拓扑" report sections.

## Category: spip

Subject contains `SPIP` (case-insensitive) - shorthand for *Spark Project Improvement Proposal*.

Body typically links to:
- Google Docs (design docs)
- GitHub Issues
- JIRA tickets (`issues.apache.org/jira/browse/SPARK-xxxxx`)

## Category: discuss

Matches if **any** of these hold:

1. Subject contains `[DISCUSS]` (case-insensitive)
2. Subject ends with a question mark `?`
3. Subject contains `question`, `how to`, or `help` (case-insensitive)
4. The body asks for feedback or poses a question, AND the subject does NOT contain a suppressive tag: `[FYI]`, `[JIRA]`, `[post-commit]`

Rule 4 exists because the Spark list gets automated `[JIRA]` notifications whose body text may contain a question mark but aren't human discussions.

## Category: others

Everything that doesn't match above. Typical contents: `[JIRA]` updates, `[VOTE]` leftovers that survived filtering, build notifications, meeting minutes.

## Fields Added by the Classifier

Each thread object in the output gains:

- `doc_links`: array of Google Doc URLs found in the root email body, via regex `https?://docs\.google\.com/document/d/[a-zA-Z0-9_-]+`. Deduplicated.
- `doc_content`: empty string `""` - a placeholder. The SPIP Summarizer in Phase 3 may fill it with content fetched via WebFetch.

## Critical Constraint

Classification **groups** threads; it does **not** summarize or truncate them. Every thread object - including `body`, `replies`, all nested content - is preserved verbatim in its bucket. The `classify_tool.py` script already enforces this; do not strip fields if hand-editing.

## Verification Checklist

After running the classifier:

1. All four keys (`discuss`, `release`, `spip`, `others`) exist in the output.
2. Total thread count across all buckets equals the input thread count - no threads lost.
3. Every thread object has `doc_links` and `doc_content` fields.
