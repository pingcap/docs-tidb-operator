---
title: TiDB Operator v2 和 v1 的对比
summary: 介绍 TiDB Operator v2 与 v1 的主要差异。
---

# TiDB Operator v2 和 v1 的对比

TiDB Operator v2 对 v1 进行了大幅重构：将核心 Custom Resource Definition (CRD) `TidbCluster` 按组件拆分为多个 CRD，移除了核心组件对 StatefulSet 的依赖，并引入了 [Overlay](overlay.md) 机制，以更好地适应快速发展的 Kubernetes 生态。

## TiDB Operator v2 的新特性

### 拆分 `TidbCluster` CRD

TiDB Operator v2 将 `TidbCluster` CRD 按组件拆分为多个独立的 CRD，并新增 `Cluster` CRD，用于表示一个 TiDB 集群：

| 组件 | 组 CRD | 实例 CRD |
|---------|--------|---------|
| PD | `PDGroup` | `PD` |
| TiKV | `TiKVGroup` | `TiKV` |
| TiDB | `TiDBGroup` | `TiDB` |
| TiFlash | `TiFlashGroup` | `TiFlash` |
| TiCDC | `TiCDCGroup` | `TiCDC` |

### 移除对 StatefulSet 的依赖

TiDB Operator v2 不再依赖 StatefulSet，扩缩容操作不再受顺序限制，同时支持修改 Volume 大小以及配置 [VolumeAttributeClass](https://kubernetes.io/zh-cn/docs/concepts/storage/volume-attributes-classes/)。

### 支持 Overlay

TiDB Operator v2 引入 [Overlay](overlay.md) 机制，支持为 Pod 指定 Kubernetes 支持的所有字段，提升了灵活性与可定制性。

### 增强验证能力

TiDB Operator v2 通过[合法性检查规则 (Validation Rule)](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) 和[验证准入策略 (Validating Admission Policy)](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/validating-admission-policy/) 增强配置校验能力，提高了系统的易用性与健壮性。

### 支持 `/status` 和 `/scale` 子资源

TiDB Operator v2 支持 [CRD 子资源](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#subresources)，可与 Kubernetes 提供的 [HorizontalPodAutoscaler (HPA)](https://kubernetes.io/zh-cn/docs/tasks/run-application/horizontal-pod-autoscale/) 集成，实现自动化扩缩容。

## 功能对比

### 组件支持情况

| 组件 | v2 | v1 |
|:---|:---| :---|
| PD | 支持 | 支持 |
| TiKV | 支持 | 支持 |
| TiDB | 支持 | 支持 |
| TiFlash | 支持 | 支持 |
| TiCDC | 支持 | 支持 |
| TiProxy | 支持 | 支持 |
| Backup/Restore | 支持 | 支持 |
| PD micro service | 支持 | 支持 |
| Pump| 不通过 CRD 支持 | 支持 |
| Lightning | 不通过 CRD 支持 | 支持 |
| TidbInitializer | 不通过 CRD 支持 | 支持 |
| TidbMonitor | 不通过 CRD 支持 | 支持 |
| TidbNgMonitoring | 不通过 CRD 支持| 支持 |
| TidbDashboard | 不通过 CRD 支持| 支持 |

### 运维能力对比

| 运维操作 | v2 | v1 |
|:---|:---| :---|
| 创建/删除集群 | 支持 | 支持 |
| 滚动更新集群 | 支持 | 支持 |
| 横向扩缩容 | 支持 | 支持 |
| 升级集群 | 支持 | 支持 |
| 暂停 | 支持 | 支持 |
| 挂起 | 支持 | 支持 |
| 磁盘扩容 | 支持 | 支持 |
| 磁盘参数变更 | 支持 | 支持 |
| Debug 模式 | 暂不支持 | 支持 |
| 优雅关闭 | 支持 | 支持 |
| 重启 Pod | 支持 | 支持 |
| 自动故障转移 (Failover) | 不支持 | 支持 |

### 集群配置支持情况

| 集群配置 | v2 | v1 |
|:---|:---| :---|
| MySQL mTLS | 支持 | 支持 |
| 集群内部 mTLS | 支持 | 支持 |
| 组件的 TOML 配置文件 | 支持 | 支持 |

### Kubernetes 相关的 Pod 配置

TiDB Operator v2 支持为 Pod 配置 Kubernetes 所支持的全部字段，详细说明请参见 [Overlay](overlay.md)。
