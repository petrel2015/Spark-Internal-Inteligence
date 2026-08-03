# Report Template

Phase 4 composes the final Markdown report. This document is **authoritative** for output structure - follow it exactly. Every section below has a literal example.

## Star Conversion

Two different score types appear in the summary JSONs; convert them differently:

- **Release `score.value`** (1-5): direct star count. `3` -> `⭐⭐⭐`, `4` -> `⭐⭐⭐⭐`, `5` -> `⭐⭐⭐⭐⭐`.
- **Discuss `score.total`** (3-15): convert to a 5-star scale via `round(total / 15 * 5)`. `10` -> `round(3.33)` -> `⭐⭐⭐`. `12` -> `round(4.0)` -> `⭐⭐⭐⭐`.

Never display raw score numbers like `(10/15)` in the final report - stars only.

## Title Format

```markdown
# Spark核心内参：<YYYY>年<MM>月：<Headline>
```

`<Headline>` is a 1-2 sentence editorial hook you curate from the month's most impactful content. Example:

```markdown
# Spark核心内参：2025年10月：Spark 4.1 预览版三发布，迈向 Java 21 与语义化引擎的新纪元
```

## Report Skeleton

```markdown
# Spark核心内参：<YYYY>年<MM>月：<Headline>

### 航向追踪

<Core Release items, one block each>

---

### 前线研讨

<Discuss items, one block each>

---

### 方案思辨

<SPIP items, one block each>

---

### 生态拓扑

<Ecosystem Release items, one block each>
```

Separate chapters with `---` horizontal rules. Blank line before each chapter heading.

---

## Chapter 1: 航向追踪 (Core Releases)

**Source**: `step4_release_summary.json`, filtered to items whose `summary` ends with `[Core]`.

### Format per item

```markdown
### <software_version>
#### 重要指数: <stars from score.value>
#### 关键更新:
-   <Key Update A>: <Content>
-   <Key Update B>: <Content>
#### 主要影响: <impact_value>
#### 相关链接:
-   [<link.type>：<link.url>](<link.url>)
#### 编者按: <summary field, weaving in architectural insight>
```

### Literal example

```markdown
### Apache Spark 4.1.0-preview3
#### 重要指数: ⭐⭐⭐⭐
#### 关键更新:
-   **环境现代化**: 全面支持 Java 17/21、Scala 2.13 以及 Python 3.10+。
-   **远程连接增强**: 重点优化 Spark Connect 架构，提升远程连接的稳定性和功能覆盖。
#### 主要影响: 为社区提供了对 Spark 4.1 新特性的早期测试机会，特别是 Spark Connect 和现代 Java 运行时的兼容性验证。
#### 相关链接:
-   [Official：https://spark.apache.org/docs/4.1.0-preview3/](https://spark.apache.org/docs/4.1.0-preview3/)
#### 编者按: 这是 Spark 4.1 路线图中的关键里程碑。通过拥抱 Java 21 和持续打磨 Spark Connect，Spark 正在释放出强烈的信号：未来将转向更加解耦、现代化的客户端-服务器架构。
```

---

## Chapter 2: 前线研讨 (Discussions)

**Source**: `step5_discuss_summary.json`.

### Format per item

```markdown
### <中文翻译的话题标题> (<原始英文主题>)
-   综合指数: <stars from score.total>

#### 问题现象: <phenomenon>
#### 问题痛点: <pain_point>
#### 预期和目标: <expectation>
#### 各方观点:
-   <Person A>: <Opinion>
-   <Person B>: <Opinion>
#### 编者按: <summary field, weaving in architectural insight>
```

### Literal example

```markdown
### GroupBy 同时使用 Count Distinct 与 Percentile 导致的复杂计划 (Unexpected behavior when using groupBy and count_distinct + percentile)
-   综合指数: ⭐⭐⭐⭐

#### 问题现象: 在执行包含 `count_distinct` 和 `percentile` 的聚合查询时，Spark Catalyst 会生成一个包含多层 ObjectHashAggregate 的复杂物理计划。
#### 问题痛点: 复杂的计划导致执行性能下降，且开发者难以理解为何简单的聚合逻辑会演变成如此厚重的计划。
#### 预期和目标: 验证该执行计划的正确性，探讨是否有优化空间。
#### 各方观点:
-   **FengYu Cao**: 提供了详尽的复现代码和物理计划图，质疑计划的合理性。
-   **Herman van Hovell**: 解释称这是为了正确处理 `count_distinct` 而触发的多步重写逻辑，是 Catalyst 优化器的既定行为。
#### 编者按: 这是对 Catalyst 聚合重写逻辑的一次深度审视。多去重或去重与复杂聚合的组合，往往会迫使优化器选择更复杂的计划以平衡内存占用和 Shuffle 数据量。
```

---

## Chapter 3: 方案思辨 (SPIPs)

**Source**: `step6_spip_summary.json`.

### Format per item

```markdown
### <中文翻译的话题标题> (<原始英文主题>)

#### 核心动机: <motivation>
#### 关键设计: <key_design>
#### 影响价值: <impact_value>
#### 相关链接
-   [<link.type>：<link.url>](<link.url>)
#### 社区探讨:
-   赞成观点: <pros>
-   反对观点: <cons>
-   其他观点: <questions>
#### 编者按: <summary field, weaving in architectural insight>
```

The `社区探讨` pros/cons/questions come from the community feedback paragraph at the end of the SPIP `summary` field. If the mailing list was quiet but the Google Doc had comments, those comments are the source.

### Literal example

```markdown
### Spark 指标与语义建模提案 (SPIP: The metrics & semantic modeling in Spark)

#### 核心动机: 弥合业务逻辑（指标）与物理数据 schema 之间的语义鸿沟。当前指标在不同工具下重复定义，导致不一致。
#### 关键设计: 在 Spark 内引入语义建模层。核心特性：1) 一次定义指标，跨维度复用；2) 语义映射逻辑名到物理列；3) 集成 Spark SQL 将逻辑查询解析为物理计划。关联 SPARK-54119。
#### 影响价值: 跨组织一致的指标产出、简化指标管理、增强 AI/LLM 数据探索能力。
#### 相关链接
-   [JIRA：https://issues.apache.org/jira/browse/SPARK-54119](https://issues.apache.org/jira/browse/SPARK-54119)
-   [Google Doc：https://docs.google.com/document/d/1xVTLijvDTJ90lZ_ujwzf9HvBJgWg0mY6cYM44Fcghl0](https://docs.google.com/document/d/1xVTLijvDTJ90lZ_ujwzf9HvBJgWg0mY6cYM44Fcghl0)
#### 社区探讨:
-   赞成观点: 认为这是 Spark 向"语义引擎"演进的关键一步。
-   反对观点: 担忧引擎职责膨胀，增加维护复杂度。
-   其他观点: 关注与现有 Catalog 体系的兼容性。
#### 编者按: 这是一个高度雄心的提案，推动 Spark 从"计算引擎"走向"语义引擎"。通过将指标定义内嵌到引擎，确保 "Revenue" 在 SQL、Scala 或 LLM agent 中语义一致。
```

---

## Chapter 4: 生态拓扑 (Ecosystem Releases)

**Source**: `step4_release_summary.json`, filtered to items whose `summary` ends with `[Ecosystem]`.

### Format per item

Identical to Chapter 1 (航向追踪):

```markdown
### <software_version>
#### 重要指数: <stars from score.value>
#### 关键更新:
-   <Key Update A>: <Content>
-   <Key Update B>: <Content>
#### 主要影响: <impact_value>
#### 相关链接:
-   [<link.type>：<link.url>](<link.url>)
#### 编者按: <summary field, weaving in architectural insight>
```

### Literal example

```markdown
### Apache Spark Kubernetes Operator 0.5.0
#### 重要指数: ⭐⭐⭐⭐
#### 关键更新:
-   **K8s 版本扩展**: 支持 Kubernetes v1.32-v1.34，Spark 3.5/4.0/4.1。
-   **CRD GA**: 引入 SparkApp 和 SparkCluster v1 CRD，Artifact Hub 集成。
#### 主要影响: 更原生的 Kubernetes 体验，HPA 支持带来更好的可扩展性。
#### 相关链接:
-   [GitHub：https://github.com/apache/spark-kubernetes-operator/releases/tag/0.5.0](https://github.com/apache/spark-kubernetes-operator/releases/tag/0.5.0)
#### 编者按: K8s Operator 0.5.0 是让 Kubernetes 成为 Spark 一等公民的重要一步。HPA 和 V1 CRD 的引入使其接近与传统资源管理器的功能对等。
```

---

## Writing Rules (apply to all chapters)

1. **Translate** into fluent professional Chinese.
2. **Keep technical terms in English**: Shuffle, Catalyst, Tungsten, Codegen, Kubernetes, SPIP, PR, CVE, HPA, CRD, etc. These terms lose precision when translated.
3. **Polish, don't machine-translate**: use mature technical-prose idioms like 阵痛、基石、演进、解耦、一等公民.
4. **Every item ends with `编者按`**: take the `summary` field and weave in your own architectural insight. Don't just copy-paste the summary.
5. **No data loss**: every item from the three summary JSONs must appear in the report. If a summary JSON has 5 releases, the report has 5 release blocks (split across Core/Ecosystem chapters).
6. **Consistent formatting**: same heading depth (`###` for items, `####` for sub-fields), same bullet style (`-   ` with two trailing spaces), same blank-line spacing.
