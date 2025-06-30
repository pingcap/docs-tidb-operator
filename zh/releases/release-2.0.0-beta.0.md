---
title: TiDB Operator 2.0.0-beta.0 Release Notes
summary: TiDB Operator 2.0.0-beta.0 版本发布。v2 版本对 v1.x 版本进行了大幅重构，主要改动包括将 `TidbCluster` 拆分为多个 CRD、移除对 StatefulSet 的依赖，并引入 Overlay 功能以实现更灵活的自定义配置。
---

# TiDB Operator 2.0.0-beta.0 Release Notes

发布日期：2025 年 7 月 x 日

TiDB Operator 版本：2.0.0-beta.0

随着 TiDB 和 Kubernetes 生态的快速发展，TiDB Operator 迎来了重大升级。我们很高兴地宣布 TiDB Operator v2.0.0-beta.0 的发布！此版本是对 TiDB Operator 的一次重大重构，旨在提供更稳定、更高效、更易于维护的 TiDB 集群管理体验。

    > **提示：**
    >
    > - 此版本为 beta 版本，**建议在生产环境使用前进行充分测试**。
    > - 关于 v2 与 v1 的详细差异，请参考 [TiDB Operator v2 与 v1 版本对比](../tidb-operator-v2-vs-v1.md)。

## 主要变化和改进

### 核心架构重构

- **CRD 拆分**：将 v1 的 `TidbCluster` CRD 拆分成了多个 CRD，支持更细粒度的组件管理，提高了可维护性和管理性。
- **直接管理 Pod**：移除了对 StatefulSet 依赖，改成直接管理 Pod，带来了更大的灵活性，能够更精细地控制 Pod 的生命周期和调度行为。
- **控制器架构升级**：基于 [controller-runtime](https://github.com/kubernetes-sigs/controller-runtime) 框架实现，简化控制器开发，提高开发效率，增强了稳定性和可靠性。

### 新功能与增强

- **Overlay 字段**：
    - 允许用户在不修改 TiDB Operator 源码的情况下，灵活地为 Pod 指定 Kubernetes 支持的所有字段
    - 提供安全校验，防止覆盖系统关键标签

- **拓扑感知调度**
    - 支持 `EvenlySpread` 策略，确保 Pod 在不同拓扑域均匀分布
    - 支持权重配置，灵活控制各拓扑域的实例分布比例
    - 提高集群可用性和容错能力

- **增强的字段校验**：
    - 集成了 Kubernetes 的[合法性检查规则 (Validation Rule)](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) 和[验证准入策略 (Validating Admission Policy)](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/validating-admission-policy/)
    - 字段格式和取值范围验证
    - 提供更友好的错误提示

- **[CRD 子资源](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#subresources)支持**：
    - `status` 子资源：统一的状态管理
    - `scale` 子资源：支持与 HPA 集成实现自动扩缩容
    - 更好地融入 Kubernetes 生态系统

- **优化配置管理**：
    - 通过改进配置哈希算法，可避免不必要的滚动更新

### 功能调整与移除

- 移除了 AWS EBS Snapshot 相关功能。
- 移除了 `tidb-scheduler` 组件。
- 移除了 `DMCluster`、`FedVolumeBackup`、`FedVolumeBackupSchedule`、`FedVolumeRestore` 等 CRD。
- 移除了 `TiDBInitializer`、`TiDBDashboard`、`TiDBMonitor`、`TiDBNGMonitoring` 等 CRD，这些功能已通过其他方式集成，详情请查阅相关文档。

## 致谢

感谢所有为 TiDB Operator 做出贡献的开发者和社区成员！我们期待您的反馈和建议，共同完善这个重要的里程碑版本。
