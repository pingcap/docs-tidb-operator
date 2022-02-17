---
title: TiDB Operator v1.3 新特性
---

# TiDB Operator v1.3 新特性

TiDB Operator v1.3 引入了以下关键特性，从扩展性、易用性、安全性等方面帮助你更轻松地管理 TiDB 集群及其周边工具。

## 兼容性改动

- 跨 Kubernetes 部署 TiDB 集群优化。如果使用 v1.3.0-beta.1 及更早版本的 TiDB Operator 跨 Kubernetes 集群部署 TiDB 集群，直接升级 TiDB Operator 会导致集群滚动更新并进入异常状态。如果从更早版本升级 TiDB Operator 到 v1.3，你需要执行以下操作：

  1. 更新 CRD。
  2. 修改 TidbCluster 定义将 `spec.acrossK8s` 字段设置为 `true`。
  3. 升级 TiDB Operator。

- 弃用 Pod `ValidatingWebhook` 和 `MutatingWebhook`。如果使用 v1.2 及更早版本的 TiDB Operator 在集群部署了 Webhook，并启用了 Pod `ValidatingWebhook` 和 `MutatingWebhook`，升级 TiDB Operator 到 v1.3.0-beta.1 及之后版本，Pod `ValidatingWebhook` 和 `MutatingWebhook` 被删除，但这不会对 TiDB 集群管理产生影响，也不会影响正在运行的 TiDB 集群。

- 生成 v1 版本 CRD 以支持在 1.22 及更新版本的 Kubernetes 集群中使用。1.3.0-beta.1 后 Operator 会默认设置各组件的 `baseImage` 字段。如果你使用了各组件的 `image` 字段而不是 `baseImage` 字段来设置镜像版本，那么直接升级 1.3.0-beta.1 及以后的 TiDB Operator，会改变正在使用的镜像的版本，导致 TiDB 集群滚动重建甚至无法正常运行。你必须按照以下操作来升级 TiDB Operator：
    1. 使用各组件配置 `baseImage` 与 `version` 替代当前使用的 `image` 字段，可以参考文档[部署配置](configure-a-tidb-cluster.md#版本)。
    2. 升级 TiDB Operator。

## 滚动更新改动

- TiFlash（>= v5.4.0）默认配置优化。TiDB Operator v1.3.0-beta.1 及之后版本针对 TiFlash v5.4.0 及之后版本的默认配置进行了优化，如果使用 v1.2 版本 TiDB Operator 部署了 v5.4 及更新版本的 TiDB 集群，升级 TiDB Operator 到 v1.3.0-beta.1 及之后版本会导致 TiFlash 组件滚动更新。建议在升级 TiDB 集群到 v5.4.0 或更新版本之前，先升级 TiDB Operator 到 v1.3 及以上版本。
- 特定配置下 TiKV 可能滚动更新。如果部署了 v5.0 及更新版本的 TiDB 集群，并且设置了 `spec.tikv.seperateRocksDBLog: true` 或者 `spec.tikv.separateRaftLog: true`，升级 TiDB Operator 到 v1.3.0-beta.1 及之后版本会导致 TiKV 组件滚动更新。
- 为了支持在 TidbMonitor CR 中配置 Prometheus 分片，升级 TiDB Operator 到 v1.3.0-beta.1 及之后版本会导致 TidbMonitor Pod 删除重建。

## 扩展性

- [跨多个 Kubernetes 集群部署一个 TiDB 集群](deploy-tidb-cluster-across-multiple-kubernetes.md)特性 GA，并支持跨 Kubernetes 集群部署[异构集群](deploy-heterogeneous-tidb-cluster.md)
- 新增 `failover.recoverByUID` 字段，以支持为 TiKV/TiFlash/DM Worker 仅执行一次性的 Recover 操作
- 支持为 TiDB 集群组件 StatefulSet 配置 [PodManagementPolicy](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#pod-management-policies)
- 支持设置所有组件 Pod 的 DNS 配置
- 支持 Kubernetes >= v1.22

## 易用性

- 支持通过配置 annotation 的方式[优雅重启单个 TiKV Pod](restart-a-tidb-cluster.md#优雅重启单个-tikv-pod)
- 优化异构集群使用体验，可以在同一个 Dashboard 中查看 TidbCluster 和与它异构部署的 TidbCluster 的监控项
- 支持为 TiDB 集群开启[持续性能分析](access-dashboard.md#启用持续性能分析)

## 安全性

- 新增 `spec.tidb.tlsClient.skipInternalClientCA` 字段，以支持内部组件访问 TiDB 时跳过服务端证书验证
- 新增 `spec.tidb.initializer.createPassword` 字段，支持部署新 TiDB 集群时设置随机密码
- 优化在 TidbMonitor 中使用 secretRef 来获取 Grafana 的密码，避免使用明文密码
