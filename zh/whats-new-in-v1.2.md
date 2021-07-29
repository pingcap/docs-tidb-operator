---
title: What's New in TiDB Operator 1.2
---

# What's New in TiDB Operator 1.2

TiDB Operator 1.2 在 1.1 基础上完善了 TidbCluster CR（Custom Resource）的功能，支持对 Pump 的完整生命周期管理，并对 TidbMonitor controller 进行了重构，支持监控多个集群、Remotewrite、Thanos sidecar 等多个新功能，并针对 TiDB Operator 部署做了优化，支持部署 namespace scoped 以及支持部署多套 TiDB Operator 分别管理不同的 TiDB 集群。同时在易用性上做了许多改进，支持通过 CR 管理 DM 2.0 集群，为 TiKV、TiFlash 自定义 Store 标签等等。以下是主要变化：

## 扩展性

- 支持为 TidbCluster 中的 Pod 与 service 自定义 label 及 annotation
- 支持为所有 TiDB 组件设置 podSecurityContext、topologySpreadConstraints
- 支持对 Pump 的完整生命周期管理
- TidbMonitor 支持[监控多个 TidbCluster](monitor-a-tidb-cluster.md#多集群监控)
- TidbMonitor 支持 remotewrite
- TidbMonitor 支持[配置 Thanos sidecar](aggregate-multiple-cluster-monitor-data.md)
- TidbMonitor 管理资源从 Deployment 变为 StatefulSet
- 支持在[仅有 namespace 权限时部署 TiDB Operator](deploy-tidb-operator.md#自定义部署-tidb-operator)
- 支持[部署多套 TiDB Operator](deploy-multiple-tidb-operator.md) 分别管理不同的 TiDB 集群

## 易用性

- 新增 [DMCluster CR 用于管理 DM 2.0](deploy-tidb-dm.md)
- 支持为 TiKV、TiFlash 自定义 Store 标签
- 支持为 [TiDB slow log 自定义存储](configure-a-tidb-cluster.md#配置-tidb-慢查询日志持久卷)
- TiDB Lightning chart [支持 local backend、持久化 checkpoint](restore-data-using-tidb-lightning.md)

## 安全性

- [TiDB Lightning chart 和 TiKV Importer chart 支持配置 TLS](enable-tls-between-components.md)

## 实验性特性

- [跨多个 Kubernetes 集群部署一个 TiDB 集群](deploy-tidb-cluster-across-multiple-kubernetes.md)

TiDB Operator 在 Kubernetes 上部署参见[安装文档](deploy-tidb-operator.md)，CRD 文档参见 [API References](https://github.com/pingcap/tidb-operator/blob/master/docs/api-references/docs.md)。
