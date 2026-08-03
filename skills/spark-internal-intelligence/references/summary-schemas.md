# Summary Schemas

Phase 3 produces three JSON summary files. Each is a JSON array of summary objects, one per thread in that category. This document defines the fields, scoring rubrics, and WebFetch guidance for each summarizer.

All three summarizers share the same execution pattern:

1. Read `output/<YYYY-MM>/step3_threads_classified.json`
2. Extract only the target category's array
3. For each thread, read the root email `body` and all nested `replies`
4. Produce one summary object
5. Write the array to the output file

---

## Release Summarizer

Output: `output/<YYYY-MM>/step4_release_summary.json`

### Fields per summary object

| Field | Type | Description |
|-------|------|-------------|
| `software_version` | string | Software name + version, e.g. `"Apache Spark 3.5.7"` |
| `key_updates` | string | Main changes. Look for release notes, official site, GitHub tag links. |
| `impact_value` | string | Effect on users, e.g. `"Security fix"`, `"Better stability"`, `"Higher resource utilization"` |
| `score` | object | `{value: 1-5, reason: string}` - see scoring table |
| `links` | array | Each item `{type, url}`; `type` is `"Official"`, `"Download"`, or `"GitHub"` |
| `summary` | string | Comprehensive summary ending with architectural insight. **Append `[Core]` or `[Ecosystem]` tag** so Phase 4 can split releases. |

### Score rubric (`score.value`)

| Value | Meaning | Criteria |
|-------|---------|----------|
| 5 | Critical | CVE security fixes, major version release (4.0), game-changing features (Photon, Connect) |
| 4 | High | Significant performance optimizations, critical bug fixes for common scenarios, useful new APIs |
| 3 | Medium | Standard maintenance release, minor feature additions, stability improvements |
| 2 | Low | Dependency updates, niche bug fixes, docs improvements |
| 1 | Trivial | Purely administrative or non-functional changes |

### Core vs Ecosystem

- **Core**: `Apache Spark x.y.z` main-line releases
- **Ecosystem**: sub-projects like `Apache Spark Kubernetes Operator`, `Spark Connect Swift Client`

Append the tag at the very end of the `summary` string, e.g. `"...the most stable enterprise-grade choice. [Core]"`.

### WebFetch guidance

If a thread links to release notes:
- `spark.apache.org/releases/...`
- `github.com/.../releases/tag/...`

use `WebFetch` to retrieve the changelog. The email body usually only has a summary; the full release notes have the JIRA list, CVEs, and detailed features needed for accurate `key_updates` and scoring.

---

## Discuss Summarizer

Output: `output/<YYYY-MM>/step5_discuss_summary.json`

### Fields per summary object

| Field | Type | Description |
|-------|------|-------------|
| `topic` | string | Thread subject, cleaned of `Re:`/`Fwd:` prefixes |
| `phenomenon` | string | What's happening? Describe the situation or question raised. |
| `pain_point` | string | What's the problem? Why does this phenomenon cause issues? |
| `expectation` | string | What outcome or goal does the initiator want? |
| `opinions` | object | Dict: keys are sender names, values are brief summaries of their views |
| `score` | object | `{clarity: 1-5, difficulty: 1-5, interaction: 1-5, total: 3-15}` |
| `summary` | string | Comprehensive summary ending with architectural insight |

### Score rubric

**`clarity`** - is the question well-posed?

| Value | Criteria |
|-------|----------|
| 5 | Reproduction steps, code, or logs provided |
| 1 | Vague ("Spark is slow") |

**`difficulty`** - technical depth.

| Value | Criteria |
|-------|----------|
| 4-5 | Kernel internals: Catalyst, Optimizer, Shuffle, Tungsten, Codegen, Memory Manager, distributed consensus |
| 3 | Complex SQL, Streaming checkpoints, K8s scheduling |
| 1-2 | Basic pyspark syntax, installation issues, standard configuration |

**`interaction`** - community engagement.

| Value | Criteria |
|-------|----------|
| 1 | Only the sender, no replies |
| 3 | Sender + 1 responder |
| 5 | 3+ participants OR a long thread (>5 messages) |

**`total`** = clarity + difficulty + interaction (range 3-15).

### WebFetch guidance

Rarely needed - the email thread is usually self-contained. Skip unless the thread explicitly references an external doc for context.

---

## SPIP Summarizer

Output: `output/<YYYY-MM>/step6_spip_summary.json`

### Fields per summary object

| Field | Type | Description |
|-------|------|-------------|
| `topic` | string | Thread subject, cleaned of `Re:`/`Fwd:` prefixes |
| `motivation` | string | Why is this capability needed? What gap does it fill? |
| `key_design` | string | Technical approach. Mention JIRA tickets, design docs, GitHub PRs. Describe proposed new classes, APIs, or workflow changes. |
| `impact_value` | string | Benefit, e.g. `"Performance gain"`, `"Easier for developers"`, `"Better stability"` |
| `links` | array | Each item `{type, url}`; `type` is `"JIRA"`, `"Google Doc"`, or `"GitHub"` |
| `summary` | string | Comprehensive summary ending with architectural insight. The final paragraph should cover community feedback (pros / cons / questions). |

### Community discussion in `summary`

The `summary` field's ending must cover community feedback, categorized as:
- **赞成观点 (pros)**: support statements
- **反对观点 (cons)**: objections
- **其他观点 (questions)**: technical inquiries, neutral questions

Source priority:
1. Mailing list replies (if the thread has substantive replies)
2. Google Doc comments (if the mailing list is quiet but a design doc exists) - fetched via WebFetch

### WebFetch guidance (critical for SPIP)

If the thread's `doc_links` array contains a Google Doc URL, use `WebFetch` to fetch it. This is often the **primary source** of design information:

- **Key Design**: the email usually has a one-paragraph summary; the doc has the full proposed changes, API sketches, and workflow diagrams.
- **Community discussion**: the doc's "Resolved Comments" and inline comment threads are a goldmine when the mailing list thread is short. Parse the fetched text for commenter names and their positions.

Extract from the fetched doc:
- "Proposed Changes" / "Design" sections -> feeds `key_design`
- "Benefits" / "Goals" -> feeds `impact_value`
- Comments / "Resolved Comments" -> feeds the community discussion paragraph in `summary`
