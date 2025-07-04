---
title: TiDB Operator 2.0.0-beta.0 Release Notes
summary: TiDB Operator 2.0.0-beta.0 版本发布。v2 版本对 v1 版本进行了大幅重构，主要改动包括将 `TidbCluster` 拆分为多个 CRD、移除对 StatefulSet 的依赖，并引入 Overlay 功能以实现更灵活的自定义配置。
---

# TiDB Operator 2.0.0-beta.0 Release Notes

发布日期：2025 年 7 月 x 日 <!-- TODO: update release date -->

TiDB Operator 版本：2.0.0-beta.0

随着 TiDB 和 Kubernetes 生态的快速发展，TiDB Operator 发布 v2.0.0-beta.0 版本，对 v1 进行了全面重构，旨在提供更稳定、高效且易于维护的集群管理体验。

关于 TiDB Operator v2 与 v1 的详细差异，请参考 [TiDB Operator v2 与 v1 版本对比](../v2-vs-v1.md)。

> **警告：**
>
> 此版本为 beta 版本，**建议在生产环境中部署前进行充分测试**。

## 主要变化和改进

### 核心架构重构

TiDB Operator v2 对 v1 的核心架构进行了全面重构，主要包括：

- **CRD 拆分**：将 v1 中的 `TidbCluster` CRD 拆分为多个独立的 CRD，实现更细粒度的组件管理，提高可维护性和灵活性。
- **直接管理 Pod**：移除对 StatefulSet 的依赖，改为直接管理 Pod，提供更高的灵活性，便于更精细地控制 Pod 的生命周期和调度行为。
- **控制器架构升级**：基于 [controller-runtime](https://github.com/kubernetes-sigs/controller-runtime) 框架实现控制器逻辑，简化控制器的开发流程，提升开发效率，并增强系统的稳定性与可靠性。

### 新特性与功能增强

- **支持 Overlay 字段**：
    - 允许用户在不修改 TiDB Operator 源码的情况下，灵活地为 Pod 指定 Kubernetes 支持的所有字段
    - 提供安全校验机制，防止关键系统标签被误覆盖

- **拓扑感知调度**：
    - 支持 `EvenlySpread` 策略，实现 Pod 在不同拓扑域间的均匀分布
    - 支持拓扑权重配置，可灵活控制各拓扑域中实例的分布比例
    - 提升集群高可用性和容错能力

- **增强字段校验**：
    - 集成 Kubernetes 的[合法性检查规则 (Validation Rule)](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) 和[验证准入策略 (Validating Admission Policy)](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/validating-admission-policy/)
    - 支持字段格式与取值范围校验
    - 提供更明确、易理解的错误提示信息，便于问题定位

- **支持 [CRD 子资源](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#subresources)**：
    - 支持 `status` 子资源，实现统一的状态管理
    - 支持 `scale` 子资源，可与 [HorizontalPodAutoscaler (HPA)](https://kubernetes.io/zh-cn/docs/tasks/run-application/horizontal-pod-autoscale/) 集成，实现自动扩缩容
    - 增强与 Kubernetes 生态系统的集成能力

- **优化配置管理**：
    - 优化配置哈希算法，避免因无效变更导致不必要的滚动更新

### 移除功能

- 移除[基于 AWS EBS 卷快照的备份恢复](https://docs.pingcap.com/zh/tidb-in-kubernetes/v1.6/volume-snapshot-backup-restore/)相关功能。
- 移除 `tidb-scheduler` 组件。
- 移除 `TiDBInitializer`、`TiDBDashboard`、`DMCluster`、`FedVolumeBackup`、`FedVolumeBackupSchedule`、`FedVolumeRestore` 等 CRD。
- 移除 `TiDBMonitor`、`TiDBNGMonitoring` 等 CRD，相关功能已通过其他方式集成，详情请查阅 [TiDB 集群的监控与告警](../monitor-a-tidb-cluster.md)。

## 致谢

感谢所有为 TiDB Operator 做出贡献的开发者和社区成员！我们期待您的反馈和建议，共同完善这个重要的里程碑版本。
