# Spark核心内参：2025年10月：Spark 4.1 预览版三发布，迈向 Java 21 与语义化引擎的新纪元

### 航向追踪

### Apache Spark 4.1.0-preview3
#### 重要指数: ⭐⭐⭐⭐
#### 关键更新:
-   **环境现代化**: 全面支持 Java 17/21、Scala 2.13 以及 Python 3.10+。
-   **远程连接增强**: 重点优化 Spark Connect 架构，提升远程连接的稳定性和功能覆盖。
-   **部署方案演进**: 包含对 Standalone、YARN 以及 Kubernetes 部署模式的最新改进。
#### 主要影响: 为社区提供了对 Spark 4.1 新特性的早期测试机会，特别是 Spark Connect 和现代 Java 运行时的兼容性验证。
#### 相关链接:
-   [Official：https://spark.apache.org/docs/4.1.0-preview3/](https://spark.apache.org/docs/4.1.0-preview3/)
-   [Download：https://dist.apache.org/repos/dist/release/spark/spark-4.1.0-preview3/](https://dist.apache.org/repos/dist/release/spark/spark-4.1.0-preview3/)
#### 编者按: 这是 Spark 4.1 路线图中的关键里程碑。通过拥抱 Java 21 和持续打磨 Spark Connect，Spark 正在释放出强烈的信号：未来将转向更加解耦、现代化的客户端-服务器架构。作为架构师，建议开发者积极在开发环境验证 Java 21 带来的性能红利。

### Apache Spark 3.5.7
#### 重要指数: ⭐⭐⭐
#### 关键更新:
-   **正确性修复**: 解决了错误的日期类型解析问题 [SPARK-52721] 以及 UDAF 导致的数据损坏风险 [SPARK-52023]。
-   **稳定性提升**: 修复了 Spark History UI 中的异常以及多处内存泄漏 [SPARK-52516]。
-   **依赖更新**: 升级 ORC 至 1.9.7，Jetty 升级至 9.4.58.v20250814。
#### 主要影响: 为 3.5 分支用户提供了更高的稳定性和安全性保障，是生产环境升级的首选版本。
#### 相关链接:
-   [Official：https://spark.apache.org/releases/spark-release-3-5-7.html](https://spark.apache.org/releases/spark-release-3-5-7.html)
#### 编者按: Spark 3.5.7 延续了 3.5.x 分支作为“企业级稳健选择”的传统。特别是针对 UDAF 数据损坏和内存泄漏的修复，对于大规模生产作业而言价值极高。推荐所有追求稳定性的存量用户尽快完成这一补丁版本的升级。

---

### 前线研讨

### Spark-Pipelines 在 macOS 环境下的类型错误 (TypeError in spark-pipelines due to GeographyType)
-   综合指数: ⭐⭐⭐

#### 问题现象: 在最新的 Spark master 分支中，由于 GeographyType 使用了现代 Python 的类型提示语法（`int | str`），在 macOS 默认的 Python 3.9 环境下运行时会抛出 TypeError。
#### 问题痛点: 虽然 PySpark 官方要求 Python 3.10+，但许多操作系统（如 macOS 12.x）默认仍带 3.9，导致开发者在未手动切换环境时遇到运行障碍。
#### 预期和目标: 确认这是代码层面的 bug 还是环境配置问题，并探讨是否需要对旧版 Python 进行兼容。
#### 各方观点:
-   **Jacek Laskowski**: 报告了该问题，并建议将 GeographyType 显式添加到 `pyspark/sql/types.py` 的 `__all__` 中，以提高可见性。
-   **Ruifeng Zheng**: 确认需要正确设置 `PYSPARK_PYTHON` 等环境变量，并同意应将 GeographyType 和 GeometryType 纳入公共 API。
#### 编者按: 这是一个典型的环境不匹配问题。随着 Spark 逐步迈向 Python 3.10+ 时代，旧版环境的“阵痛”在所难免。社区的共识倾向于通过更清晰的环境要求说明和公共 API 规范化来解决。

### Java 版本升级导致的 now() 函数精度差异 (Different output precision of now() in Spark 3.5.1 between Java 8 and Java 21)
-   综合指数: ⭐⭐⭐

#### 问题现象: 在 Spark 3.5.1 中，`now()` 函数在 Java 8 环境下返回毫秒精度，而在 Java 21 环境下则返回微秒精度。
#### 问题痛点: 对于将时间戳以固定长度字符串形式存储的下游业务系统，JVM 版本的升级会导致数据截断或解析错误，破坏了向后兼容性。
#### 预期和目标: 澄清此行为是否符合预期，以及 Spark 是否应该在不同 JVM 版本间保证一致的输出精度。
#### 各方观点:
-   **Yu Hong**: 详细分析了 JDK `Instant.now()` 的底层实现差异，并寻求社区对于是否应为此增加配置项的建议。
#### 编者按: 此案例折射出基础设施升级中微妙的副作用。虽然 ISO-8601 标准允许变长精度，但现实中的遗留系统往往依赖于某种“偶然的稳定性”。这提醒我们在进行 JVM 现代化转型时，需额外关注时间处理函数的行为差异。

### GroupBy 同时使用 Count Distinct 与 Percentile 导致的复杂计划 (Unexpected behavior when using groupBy and count_distinct + percentile)
-   综合指数: ⭐⭐⭐⭐

#### 问题现象: 在执行包含 `count_distinct` 和 `percentile` 的聚合查询时，Spark Catalyst 会生成一个包含多层 ObjectHashAggregate 的复杂物理计划。
#### 问题痛点: 复杂的计划导致执行性能下降，且开发者难以理解为何简单的聚合逻辑会演变成如此厚重的计划。
#### 预期和目标: 验证该执行计划的正确性，探讨是否有优化空间。
#### 各方观点:
-   **FengYu Cao**: 提供了详尽的复现代码和物理计划图，质疑计划的合理性。
-   **Herman van Hovell**: 解释称这是为了正确处理 `count_distinct` 而触发的多步重写逻辑，是 Catalyst 优化器的既定行为。
#### 编者按: 这是对 Catalyst 聚合重写逻辑的一次深度审视。多去重（Multi-distinct）或去重与复杂聚合（如百分位数）的组合，往往会迫使优化器选择更复杂的计划以平衡内存占用和 Shuffle 数据量。这再次印证了在分布式计算中，逻辑的简洁并不总能等同于执行的轻量。

### 增强 JSON 解析以支持标准合规性 (Enhance JSON Parsing to Support Standard Compliance)
-   综合指数: ⭐⭐⭐

#### 问题现象: Spark 现有的 JSON 解析器（源于对 Hive 的兼容）允许单引号、未转义控制字符等非标准行为。
#### 问题痛点: 与 RFC 8259 标准的不一致会导致 Spark 接受或产生“坏 JSON”，在与其他企业级系统对接时引发解析异常。
#### 预期和目标: 引入配置项，允许用户强制执行严格的 JSON 标准检查。
#### 各方观点:
-   **Philo**: 提议进行增强，并列举了多个违反标准的具体案例。
-   **Wenchen Fan**: 建议明确需要更改的具体行为列表。
#### 编者按: Spark 正在从一个“不惜代价求兼容”的引擎向“拥抱标准”的成熟系统演进。这对于企业级集成来说是一个巨大的进步，尽管为了兼容历史包袱，这种“严格模式”在很长一段时间内可能仍将是可选的。

---

### 方案思辨

### Spark 指标与语义建模提案 (SPIP: The metrics & semantic modeling in Spark)

#### 核心动机: 弥合业务逻辑（指标）与物理数据架构之间的语义鸿沟。目前指标在不同工具间被重复定义且不一致，通过该提案可以实现“定义一次，处处复用”，并为 LLM 提供更精准的语义层。
#### 关键设计: 在 Spark 内部引入语义建模层。主要特性包括：1) 业务指标的一次性定义与多维复用；2) 逻辑名与物理列的语义映射；3) 与 Spark SQL 集成，将逻辑查询自动解析为物理执行计划。
#### 影响价值: 确保组织内业务结果的一致性，简化指标管理，并极大增强了 Spark 在 AI/LLM 时代的易用性。
#### 相关链接
-   [JIRA：https://issues.apache.org/jira/browse/SPARK-54119](https://issues.apache.org/jira/browse/SPARK-54119)
-   [Google Doc：https://docs.google.com/document/d/1xVTLijvDTJ90lZ_ujwzf9HvBJgWg0mY6cYM44Fcghl0](https://docs.google.com/document/d/1xVTLijvDTJ90lZ_ujwzf9HvBJgWg0mY6cYM44Fcghl0)
#### 社区探讨:
-   赞成观点: 普遍认为这能够显著提升数据一致性，并降低业务人员使用 Spark 的门槛。
-   反对观点: 担心引入过重的语义层会增加 Catalyst 优化器的复杂度，并可能导致性能损耗。
#### 编者按: 这是一个雄心勃勃的提案，标志着 Spark 正在从纯粹的“计算引擎”向“语义引擎”跨越。通过将指标定义下沉到引擎内部，Spark 能确保无论通过 SQL 还是 AI Agent 查询，“营收”等指标的含义始终如一。这是构建现代化数据架构的基石之举。

---

### 生态拓扑

### Apache Spark Kubernetes Operator 0.5.0
#### 重要指数: ⭐⭐⭐⭐
#### 关键更新:
-   **K8s 版本适配**: 扩展了对 Kubernetes v1.32 至 v1.34 的支持。
-   **CRD 演进**: 引入了正式的 SparkApp 和 SparkCluster V1 版本自定义资源。
-   **弹性伸缩**: 增加了对 SparkCluster 的 HPA（水平 Pod 自动扩缩容）支持。
-   **安全与运维**: 默认启用 `ExitOnOutOfMemoryError`，并支持 Java 25 和 Prometheus 监控增强。
#### 主要影响: 极大提升了 Spark 在 Kubernetes 上的原生体验，通过 HPA 实现了更精细的资源利用。
#### 相关链接:
-   [GitHub：https://github.com/apache/spark-kubernetes-operator/releases/tag/0.5.0](https://github.com/apache/spark-kubernetes-operator/releases/tag/0.5.0)
#### 编者按: Kubernetes Operator 0.5.0 的发布是 Spark 云原生进程的重要一步。HPA 的支持和 V1 版本 CRD 的推出，意味着该组件正逐步走向成熟，能够满足生产环境下对高可用和动态伸缩的严苛要求。

### Apache Spark Connect Swift Client 0.4.0
#### 重要指数: ⭐⭐
#### 关键更新:
-   **API 扩展**: 新增了对 Timestamp 类型以及 DataflowGraph、SqlGraphElements 等 API 的支持。
-   **稳定性增强**: 升级了 gRPC Swift 库，并引入了针对 Swift 6.2 的 CI 测试。
#### 主要影响: 允许 iOS/macOS 开发者能够利用 Swift 原生接入 Spark 集群进行大规模数据处理。
#### 相关链接:
-   [GitHub：https://github.com/apache/spark-connect-swift/releases/tag/0.4.0](https://github.com/apache/spark-connect-swift/releases/tag/0.4.0)
#### 编者按: 虽然仍处于实验阶段，但 Swift 客户端的持续迭代展示了 Spark Connect 协议在构建跨语言生态方面的潜力。这为非 JVM/Python 栈的开发者打开了一扇通往分布式计算的大门。
