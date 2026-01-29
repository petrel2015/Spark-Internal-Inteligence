# Spark Internal Intelligence

English | [中文](./README.zh.md)

[![AI Powered](https://img.shields.io/badge/Powered%20by-Gemini%20AI-blue.svg)](https://deepmind.google/technologies/gemini/)

---

**Spark Internal Intelligence** is an automated technical intelligence processing system powered by Gemini AI. It parses Apache Spark developer mailing lists (`.mbox`), orchestrates a multi-agent collaboration workflow, and produces professional-grade monthly technical reports.

### 🤖 The Editorial Team (AI Agents)

This project simulates the workflow of a professional editorial office, with each role driven by specialized AI Skills:

| Role | Responsibility |
| :--- | :--- |
| **Chief Editor** | Oversees the entire production lifecycle and quality control. |
| **Planning Editor** | Manages the content supply chain, from data ingestion to classification. |
| **Responsible Editor** | Compiles, polishes, and provides expert technical commentary for the final report. |
| **Domain Summarizers** | Specialized agents for deep mining of **SPIP** (Proposals), **Release** announcements, and **Discuss** threads. |

### 🛠 The Data Pipeline

The system generates intermediate assets following a strict sequential numbering to ensure transparency:

1.  **`step1_threads.json`**: Raw threaded data parsed from the mbox file.
2.  **`step2_threads_filtered.json`**: Core conversations filtered of noise (e.g., JIRA automated updates).
3.  **`step3_threads_classified.json`**: Threads classified into **Release**, **Discuss**, and **SPIP** categories.
4.  **`step4_release_summary.json`**: Analysis of software updates, impact, and importance scores.
5.  **`step5_discuss_summary.json`**: Analysis of technical discussions, including phenomena, pain points, and community opinions.
6.  **`step6_spip_summary.json`**: Analysis of Spark Project Improvement Proposals, covering motivation, design, and value.

**Final Output**: `output/<YYYY-MM>/Spark_Internal_Inteligence_<YYYY>_<MM>.md`

### 📂 Directory Structure

*   `input/`: Place raw `.mbox` mailing list files here.
*   `output/`: Contains generated JSON intermediates and the final Markdown report, organized by month.
*   `src/`: Core Python scripts for parsing, filtering, and classifying.
*   `.gemini/skills/`: Definitions and instructions for each AI Agent Skill.

### 🚀 Quick Start

#### 1. Prepare Data
Download a mailing list archive (e.g., from [Apache Archives](https://lists.apache.org/list.html?dev@spark.apache.org)) and place the `.mbox` file in the `input/` directory.

#### 2. Activate the Chief Editor
Using the `gemini-cli`, activate the Chief Editor skill:

```bash
activate_skill spark-internal-inteligence-chief-editor
```

#### 3. Generate Report
Instruct the Chief Editor to process your specific mbox file. The system will automatically delegate tasks to the Planning Editor and Responsible Editor to complete the pipeline.
