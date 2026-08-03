# Spark 核心内参 · AI Skill 设计说明

本项目通过一个符合 [Agent Skills 规范](https://agentskills.io/specification) 的单一 Skill，实现从 Spark 邮件列表 mbox 到高质量技术月刊的自动化生产。可在任何支持该规范的 Agent（ZCode、Claude Code 等）中运行。

## 🤖 Skill 结构

整个工作流封装在一个 skill 中，采用 progressive disclosure 分层加载：

| 文件 | 职责 |
| :--- | :--- |
| `skills/spark-internal-intelligence/SKILL.md` | 主编排：四阶段流水线（解析 → 分类 → 摘要 → 合成） |
| `skills/.../references/classification-rules.md` | Phase 2 线程分类规则（Release/Discuss/SPIP/Others 优先级与匹配条件） |
| `skills/.../references/summary-schemas.md` | Phase 3 三类摘要的输出字段、评分表、WebFetch 指引 |
| `skills/.../references/report-template.md` | Phase 4 最终 Markdown 报告模板（含字面量示例） |

## 🛠 四阶段流水线 (Pipeline)

| Phase | 做什么 | 产物 |
| :--- | :--- | :--- |
| **1. Parse & Filter** | 运行 `main.py` 线程化 mbox 并过滤噪音 | `step1_threads.json`, `step2_threads_filtered.json` |
| **2. Classify** | 运行 `src/classify_tool.py` 按 Release/Discuss/SPIP/Others 归桶 | `step3_threads_classified.json` |
| **3. Summarize** | 三类摘要独立生成（可并行 subagent） | `step4-6_*_summary.json` |
| **4. Compose** | 合成中文 Markdown 月刊，融入架构师视角的编者按 | `Spark_Internal_Inteligence_<YYYY>_<MM>.md` |

每个 phase 产出的 JSON 都落盘到 `output/<YYYY-MM>/`，处理过程透明、可断点续跑。

## 🚀 使用方式

在任意支持 Agent Skills 规范的 Agent 中：

```
/spark-internal-intelligence 处理 2026-7
```

Skill 会自动判断是从头跑全流程，还是从某个已存在的 `stepN_*.json` 断点续跑。
