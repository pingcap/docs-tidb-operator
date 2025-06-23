---
title: TiDB Operator v1 和 v2 的对比
summary: 介绍 TiDB Operator v1 和 v2 的差异
---

# TiDB Operator v1 和 v2 的对比

TiDB Operator v2 对 v1 进行了一次比较大的重构，将核心 CRD (TidbCluster) 按组件拆分成了多个 CRD，并对移除了核心组件对 StatefulSet 的依赖，同时引入了 [Overlay](overlay.md) 机制来应对快速发展的 Kubernetes 生态

## TiDB Operator v2 新特性

### 拆分 TidbCluster CRD

将 TidbCluster CRD 按组件拆分成多个 CRD, 并引入 Cluster CRD 代表一个 TiDB 集群

- PDGroup/PD
- TiKVGroup/TiKV
- TiDBGroup/TiDB
- TiFlashGroup/TiFlash
- TiCDCGroup/TiCDC
- ...

### 移除了 StatefulSet 依赖

扩缩容不在受到 StatefulSet 的顺序限制，并且能够支持修改 volume size 和 [VolumeAttributeClass](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/)

### 支持 Overlay

支持 [Overlay](overlay.md), 能够指定 Pod 上支持的所有字段。

### 增强 Validation

通过 [Validation Rule](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) 和 [Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/) 增强了 validation，提升了易用性。

### 支持 /status 和 /scale subresource

支持 [CRD subresource](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#subresources), 能够和 Kubernetes 提供的 [HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) 集成。

## 功能对比

### 组件支持


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
| TidbInitilizer | 不通过 CRD 支持 | 支持 |
| TidbMonitor | 不通过 CRD 支持 | 支持 |
| TidbNgMonitoring | 不通过 CRD 支持| 支持 |
| TidbDashboard | 不通过 CRD 支持| 支持 |


### 运维操作


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
| 自动 Failover | 不支持 | 支持 |


### 集群配置


| 集群配置 | v2 | v1 |
|:---|:---| :---|
| MySQL mTLS | 支持 | 支持 |
| 集群内 mTLS | 支持 | 支持 |
| 组件的 toml 配置文件 | 支持 | 支持 |


### Kubernetes 相关的 Pod 配置

v2 支持指定 Pod 上的所有字段，详见 [Overlay](overlay.md)


