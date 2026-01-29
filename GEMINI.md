# Gemini AI 辅助系统设计 (Spark核心内参)

本项目深度集成 Gemini AI 能力，通过一系列专门化的 **Skills (智能体技能)** 实现从海量邮件列表到高质量技术月刊的自动化生产。

## 🤖 智能体团队 (AI Agents Role)

系统采用多角色协作模式，模拟报社编辑部的运作流程：

| 角色 | Skill 名称 | 职责描述 |
| :--- | :--- | :--- |
| **主编** | `spark-internal-inteligence-chief-editor` | 负责整体调度，指挥策划编辑准备数据，指挥责任编辑完成写作。 |
| **策划编辑** | `spark-internal-inteligence-planning-editor` | 负责数据预处理：解析 mbox、按月组织目录、调用分类器。 |
| **分类专家** | `thread-classifier` | 将邮件线程自动归类为：`SPIP` (提案)、`Release` (发布)、`Discuss` (讨论)。 |
| **摘要专家** | `spip/release/discuss-summarizer` | 针对不同类型的线程，提取核心矛盾、技术要点、专家观点及重要性评分。 |
| **责任编辑** | `spark-internal-inteligence-responsible-editor` | 整合各类摘要，进行中文润色、排版，生成最终的《Spark核心内参》Markdown 报告。 |

## 🛠 AI 工作流 (Pipeline)

1.  **数据注入**：手动或自动将 `.mbox` 文件放入 `input/`。
2.  **结构化**：`mbox_parser.py` 将邮件聚合成 JSON 线程。
3.  **分类路由**：`thread-classifier` 根据内容判定线程属性。
4.  **深度摘要**：针对不同类别调用特定 Prompt 模板进行信息浓缩。
5.  **月刊合成**：按照日期结构汇聚当月所有高价值信息。

## 📂 技能定义目录

所有 AI 逻辑和 Prompt 存储在：
- `.gemini/skills/`: 包含各角色的 `SKILL.md` 指令说明。

## 🚀 使用目标

通过 `gemini-cli` 激活相应技能，实现：
- `activate_skill spark-internal-inteligence-chief-editor`
- 自动化生成 2025-12 或 2026-01 的《Spark核心内参》。