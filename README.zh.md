## Spark核心内参

[English](./README.md) | 中文

[![AI Powered](https://img.shields.io/badge/Powered%20by-Gemini%20AI-blue.svg)](https://deepmind.google/technologies/gemini/)

--- 

**Spark核心内参** 是一个基于 Gemini AI 的自动化技术情报处理系统。它能够自动解析 Apache Spark 开发者邮件列表（.mbox），通过多智能体协作（Multi-Agent）流程，产出极具深度的月度技术内参报告。

### 🤖 智能体编辑部

项目模拟了专业编辑部的运作流程，每个角色由专门的 AI Skill 驱动：

| 角色 | 职能 |
| :--- | :--- |
| **主编 (Chief Editor)** | 负责整体流程调度与质量把控。 |
| **策划编辑 (Planning Editor)** | 负责内容供应链，管理从数据清洗到分类的自动化管道。 |
| **责任编辑 (Responsible Editor)** | 负责最终报告的合成、润色与技术专家点评。 |
| **专项摘要专家** | 针对 **SPIP** (提案)、**Release** (发布)、**Discuss** (讨论) 三大板块进行深度技术挖掘。 |

### 🛠 数据生产流水线

系统生成的中间件和产物遵循严格的顺序编号，确保处理过程透明：

1.  **`step1_threads.json`**: 原始邮件解析后的初步线程化数据。
2.  **`step2_threads_filtered.json`**: 过滤掉 JIRA 更新等噪音后的核心对话。
3.  **`step3_threads_classified.json`**: 自动分类后的 Release, Discuss, SPIP 线程。
4.  **`step4_release_summary.json`**: 针对版本发布的特性、影响力及重要指数分析。
5.  **`step5_discuss_summary.json`**: 针对技术讨论的问题现象、痛点及社区观点分析。
6.  **`step6_spip_summary.json`**: 针对 Spark 项目改进建议（SPIP）的动机、设计及价值分析。

**最终产物**: `output/<YYYY-MM>/Spark_Internal_Inteligence_<YYYY>_<MM>.md`

### 📂 目录结构

*   `input/`: 存放原始的 `.mbox` 邮件列表文件。
*   `output/`: 按月份存放生成的 JSON 中间件和最终生成的 Markdown 报告。
*   `src/`: 包含解析器、分类器和过滤器等核心 Python 脚本。
*   `.gemini/skills/`: 定义各个 AI 角色的 SKILL 指令。

### 🚀 快速开始

#### 1. 准备数据
将 Spark 邮件列表文件（如 `dev_spark_apache_org_2025-10.mbox`）放入 `input/` 目录。

#### 2. 激活主编技能
使用 `gemini-cli` 激活主编并下达任务：

```bash
activate_skill spark-internal-inteligence-chief-editor
```

#### 3. 生成报告
告知主编需要处理的 mbox 文件路径，系统将自动调用策划编辑和责任编辑完成所有步骤。
