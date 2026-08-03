## Spark核心内参

[English](./README.md) | 中文

[![AI Powered](https://img.shields.io/badge/Powered%20by-AI-blue.svg)](https://agentskills.io/specification)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

--- 

**Spark核心内参** 把 Apache Spark 开发者邮件列表存档（`.mbox`）自动提炼成一份深度中文月度技术报告。整个工作流封装成一个符合 [Agent Skills 规范](https://agentskills.io/specification) 的单一 skill，可在任何支持该规范的 Agent（ZCode、Claude Code、Hermes 等）中运行。

---

## 给 AI Agent 的话（请先读这一段）

> 如果你是一个 AI Agent，用户把这个仓库发给你并要求你安装运行，请严格按下面步骤执行。以下步骤是自包含的，除非命令报错，不需要向用户追问任何问题。

### 这个项目做什么

解析一个 Spark `dev` 邮件列表的 `.mbox` 文件，把邮件线程分类为 Release / Discuss / SPIP，分别摘要后合成一份中文 Markdown 报告。仓库里已带了一份样例输入和完整产物（`examples/2025-10/`）。

### 第 1 步 - 安装

```bash
git clone <this-repo-url>   # 或：用户已经 clone 好，跳过这一步
cd Spark-Internal-Inteligence
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` 包含：`click`、`python-dateutil`、`rich`。需要 Python 3.10+。

### 第 2 步 - 验证安装

用仓库自带的样例 mbox 跑解析器。成功标志 = 退出码 0，且 `output/2025-10/` 下出现两个 JSON 文件：

```bash
python3 main.py --mbox examples/2025-10/dev_spark_apache_org_2025-10.mbox
```

预期 stdout 末尾为：`Successfully saved filtered JSON to: output/2025-10/step2_threads_filtered.json`。

也可以测试自动下载路径（Phase 0）——直接从 lists.apache.org 拉取指定月份：

```bash
python3 main.py --month 2026-7
```

`--mbox` 和 `--month` 产出的结果一样（解析+过滤后的 mbox），区别只是 `--month` 会先帮你下载。

### 第 3 步 - 跑完整流水线（skill）

**流水线分五个阶段：下载 -> 解析 -> 分类 -> 摘要 -> 合成。** 阶段 0-2 是确定性 Python 脚本。阶段 3-4 需要 LLM，由 `skills/spark-internal-intelligence/SKILL.md` 中定义的 skill 驱动。

**一条命令路径（自动化首选）：** 知道 YYYY-M 的话，`--month` 能跑完除 LLM 阶段外的所有事：

```bash
python3 main.py --month 2026-7   # Phase 0（下载）+ Phase 1-2（解析 + 过滤）
```

然后交给 skill 执行阶段 3-4（摘要 + 合成）。

**如果你是支持 Agent Skills 规范的 Agent：** 加载 skill `spark-internal-intelligence`，把 mbox 路径传给它：

```
/spark-internal-intelligence 处理 examples/2025-10/dev_spark_apache_org_2025-10.mbox
```

skill 会自动执行：
1. `python3 main.py --mbox <path>`（阶段 1-2：解析 + 过滤）
2. `python3 src/classify_tool.py <step2> <step3>`（阶段 2：分类）
3. 读 `references/summary-schemas.md`，生成 `step4-6_*_summary.json`（阶段 3：摘要 - 三类可并行）
4. 读 `references/report-template.md`，合成最终报告（阶段 4：合成）

**最终产物：** `output/<YYYY-MM>/Spark_Internal_Inteligence_<YYYY>_<MM>.md`

**如果你是不支持 skill 加载的通用 Agent：** 打开 `skills/spark-internal-intelligence/SKILL.md`，按其中描述的四个阶段手动执行。`references/` 里有精确的 schema、评分表和输出模板。

### 第 4 步 - 向用户汇报

告诉用户：
1. 最终报告的绝对路径。
2. 一句话概括本月最重要的一项内容（取自报告顶部标题）。

### 常见问题

| 现象 | 解决 |
|------|------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` 没装完 - 在已激活的 venv 里重跑。 |
| `main.py --month` 下载失败 | 网络问题或该月份暂无归档。在浏览器里打开 `https://lists.apache.org/api/mbox.lua?list=dev&domain=spark.apache.org&d=YYYY-M` 验证。 |
| `main.py` 跑完没线程 | mbox 文件为空或格式不对 - 确认是 Spark dev 列表导出的 `.mbox`。 |
| 阶段 3-4 无产物 | Agent 不支持 Agent Skills 规范 - 按 `SKILL.md` 手动执行四个阶段。 |

---

## 给人看的项目说明

### 为什么做这个

Spark 开发者邮件列表是判断项目走向的一手信息源 - 版本计划、设计提案（SPIP）、疑难 bug 讨论都在这里。但它量大、难扫读。这个项目把一个月的邮件蒸馏成一份可读的内参，并附带架构师视角的点评。

### 五阶段流水线

| 阶段 | 做什么 | 怎么做 | 产物 |
| :--- | :--- | :--- | :--- |
| **0. 下载** | 从 lists.apache.org 下载 mbox | `main.py --month`（Python） | `input/dev_spark_apache_org_<YYYY-M>.mbox` |
| **1. 解析 + 过滤** | mbox 线程化，去掉 JIRA/投票噪音 | `main.py`（Python） | `step1_threads.json`, `step2_threads_filtered.json` |
| **2. 分类** | 按 Release / Discuss / SPIP / Others 归桶 | `src/classify_tool.py`（Python） | `step3_threads_classified.json` |
| **3. 摘要** | 每类深度挖掘 + 专家评分 | LLM（skill） | `step4-6_*_summary.json` |
| **4. 合成** | 合成中文 Markdown 报告 | LLM（skill） | `Spark_Internal_Inteligence_<YYYY>_<MM>.md` |

阶段 1-2 是确定性、可复现的；阶段 3-4 由 LLM 驱动、由 skill 定义。每个阶段都把带编号的 JSON 产物写到 `output/<YYYY-MM>/`，可以检视中间状态、从任意阶段断点续跑。

### 目录结构

```
Spark-Internal-Inteligence/
├── main.py                    # CLI 入口：下载 + 解析 + 过滤（阶段 0-2）
├── src/
│   ├── mbox_parser.py         # mbox -> 线程化 JSON
│   ├── topic_filter.py        # 去噪（unsubscribe、[VOTE]、空内容）
│   ├── classify_tool.py       # 线程归桶（阶段 2）
│   └── fetch_mbox.py          # 从 lists.apache.org 下载 mbox（阶段 0）
├── skills/
│   └── spark-internal-intelligence/
│       ├── SKILL.md           # skill 本体：编排阶段 0-4
│       └── references/        # progressive disclosure
│           ├── classification-rules.md   # 阶段 2 分类规则
│           ├── summary-schemas.md        # 阶段 3 schema + 评分表
│           └── report-template.md        # 阶段 4 报告模板
├── examples/2025-10/          # 自带样例（mbox + 完整流水线产物）
├── input/                     # 下载的 .mbox 落地处（gitignore）
└── output/                    # 产物，按 YYYY-MM 分目录（gitignore）
```

### 获取 mbox 文件

**自动下载（推荐）：** 给 `main.py` 一个 YYYY-M 月份，它直接从 Apache Pony Mail 归档下载——不需要浏览器：

```bash
python3 main.py --month 2026-7
```

**手动下载：** 浏览 [Apache Spark dev 列表归档](https://lists.apache.org/list?dev@spark.apache.org:2026-7)，点击 "Download as mbox" 按钮，把导出的 `.mbox` 文件放进 `input/`。

### 样例产物

仓库带了 2025 年 10 月的完整样例 - 看 `examples/2025-10/Spark_Internal_Inteligence_2025_10.md` 了解最终报告长什么样，`step1-6` 的 JSON 是中间产物。

### 许可证

MIT - 见 [LICENSE](./LICENSE)。
