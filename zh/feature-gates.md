---
title: 特性门控
summary: 介绍如何使用特性门控 (Feature Gates) 在 TiDB 集群中开启或关闭特定功能。
---

# 特性门控

特性门控 (Feature Gates) 是一组开关，用于控制 TiDB Operator 中特定功能的启用状态。这些功能通常处于实验阶段，启用后可能需要重启部分组件。

你可以在 Cluster CR 的 `spec.featureGates` 字段中配置特性门控。以下示例展示如何启用 `FeatureModification` 特性：

```yaml
spec:
  featureGates:
    FeatureModification: true

## 支持的特性门控

本节列出了 TiDB Operator 支持的特性门控。关于特性阶段的定义，请参考[特性门控阶段](#特性门控阶段)。

### `FeatureModification`

- 开启该特性后，你可以修改 `spec.featureGates` 配置。
- 默认值：`false`
- 阶段：v2.0 及之后版本为 Alpha
- 需要重启的组件：无

### `VolumeAttributesClass`

- 开启该特性后，你可以修改 PVC 的 `VolumeAttributesClass` 属性。该功能依赖 Kubernetes 的对应能力。更多信息，请参考 [Kubernetes 官方文档 VolumeAttributesClass](https://kubernetes.io/zh-cn/docs/concepts/storage/volume-attributes-classes/)。
- 默认值：`false`
- 阶段：v2.0 及之后版本为 Alpha
- 需要重启的组件：无

### `DisablePDDefaultReadinessProbe`

- 开启该特性后，TiDB Operator 不再通过 TCP 探测方式检查 PD 的就绪状态。
- 默认值：`false`
- 阶段：v2.0 及之后版本为 Alpha
- 需要重启的组件：PD

### `UsePDReadyAPI`

- 开启该特性后，TiDB Operator 将通过 PD 的 `/ready` API 检查就绪状态。有关实现细节，请参阅 [`tikv/pd` #8749](https://github.com/tikv/pd/pull/8749)。
- 默认值：`false`
- 阶段：v2.0 及之后版本为 Alpha
- 需要重启的组件：PD

### `SessionTokenSigning`

- 开启该特性后，TiDB Operator 会自动配置 TiDB 的 [`session-token-signing-cert`](https://docs.pingcap.com/zh/tidb/stable/tidb-configuration-file/#session-token-signing-cert-从-v640-版本开始引入) 和 [`session-token-signing-key`](https://docs.pingcap.com/zh/tidb/stable/tidb-configuration-file/#session-token-signing-key-从-v640-版本开始引入) 参数。
- 默认值：`false`
- 阶段：v2.0 及之后版本为 Alpha
- 需要重启的组件：TiDB

## 特性门控阶段

特性门控根据功能的成熟度分为 Alpha、Beta 和 GA 三个阶段。

### Alpha

Alpha 阶段的特性具有以下特点：

- 默认关闭。
- 建议仅在新建集群中开启。
- 不保证支持在已有集群中动态开启或关闭。
- 开启后可能出现已知或未知问题。
- **不建议在生产环境中使用**，除非已充分评估并验证风险。

### Beta

Beta 阶段的特性具有以下特点：

- 通常已经过较充分的测试。
- 建议在所有新建集群中开启。
- 通常支持在已有集群中开启或关闭，但可能需要重启相关组件。

### GA

GA (General Availability) 阶段的特性具有以下特点：

- 通常已经过长期和大规模测试。
- 默认开启。
- 不支持关闭。

## 特性说明

### FeatureModification

开启后支持变更 `spec.featureGates`.

### VolumeAttributesClass

开启后支持变更 PVC 的 VolumeAttributesClass. 需要 Kubernetes 支持对应功能, 详见 [VolumeAttributesClass](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/)

### DisablePDDefaultReadinessProbe

开启后不再通过 tcp ping 来检查 PD 的 readiness

### UsePDReadyAPI

开启后通过 `/ready` 来检查 PD 的 readiness, 详见 [tikv/pd#8749](https://github.com/tikv/pd/pull/8749)

### SessionTokenSigning

开启后 TiDB 会配置 `session-token-signing-cert` 和 `session-token-signing-key`, 详见 [TiDB 配置文件](https://docs.pingcap.com/tidb/stable/tidb-configuration-file/#session-token-signing-cert-new-in-v640)
