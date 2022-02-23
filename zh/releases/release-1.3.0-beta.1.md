---
title: TiDB Operator 1.3.0-beta.1 Release Notes
---

# TiDB Operator 1.3.0-beta.1 Release Notes

发布日期: 2022 年 1 月 12 日

TiDB Operator 版本：1.3.0-beta.1

## 兼容性改动

- 由于 [#4209](https://github.com/pingcap/tidb-operator/pull/4209) 的变更，如果使用 v1.2 及更早版本的 TiDB Operator 在集群部署了 Webhook，并启用了 Pod `ValidatingWebhook` 和 `MutatingWebhook`，升级 TiDB Operator 到 v1.3.0-beta.1 版本后，Pod `ValidatingWebhook` 和 `MutatingWebhook` 被删除，但这不会对 TiDB 集群管理产生影响，也不会影响正在运行的 TiDB 集群。

- 由于 [#4151](https://github.com/pingcap/tidb-operator/pull/4151) 的变更，如果部署了 v1 CRD，1.3.0-beta.1 后 TiDB Operator 会默认设置各组件的 `baseImage` 字段。如果你使用了各组件的 `image` 字段而不是 `baseImage` 字段来设置镜像，那么直接升级到 1.3.0-beta.1 及以后的 TiDB Operator，会改变正在使用的镜像的版本，导致 TiDB 集群滚动重建甚至无法正常运行。你必须按照以下操作来升级 TiDB Operator：
    1. 在各组件的配置中，使用 `baseImage` 与 `version` 字段代替当前使用的 `image` 字段，可以参考文档[部署配置](../configure-a-tidb-cluster.md#版本)。
    2. 升级 TiDB Operator。

- 由于 [#4434](https://github.com/pingcap/tidb-operator/pull/4434) 的问题，在部署 v1.3.0-beta.1 版本的 TiDB Operator 情况下，直接升级 TiFlash 到 v5.4.0 及更高版本可能会导致 TiFlash **无法使用并且丢失元数据**。如果集群中部署了 TiFlash，推荐升级到 v1.3.1 及之后版本，再执行升级操作。
  
- 由于 [#4435](https://github.com/pingcap/tidb-operator/pull/4435) 的问题，在部署 v1.3.0-beta.1 版本的 TiDB Operator 情况下，如果 TiFlash 的配置不包含 `tmp_path` 字段，则无法使用 v5.4.0 版本的 TiFlash。推荐升级到 v1.3.1 及之后版本后，再使用 TiFlash。
  
## 滚动升级改动

- 由于 [#4358](https://github.com/pingcap/tidb-operator/pull/4358) 的变更，如果使用 v1.2 版本 TiDB Operator 部署了 v5.4 及更新版本的 TiDB 集群，升级 TiDB Operator 到 v1.3.0-beta.1 版本会导致 TiFlash 组件滚动更新。建议在升级 TiDB 集群到 v5.4.0 或更新版本之前，先升级 TiDB Operator 到 v1.3 及以上版本。
- 由于 [#4169](https://github.com/pingcap/tidb-operator/pull/4169) 的变更，如果部署了 v5.0 及更新版本的 TiDB 集群，并且设置了 `spec.tikv.seperateRocksDBLog: true` 或者 `spec.tikv.separateRaftLog: true`，升级 TiDB Operator 到 v1.3.0-beta.1 版本会导致 TiKV 组件滚动更新。
- 由于 [#4198](https://github.com/pingcap/tidb-operator/pull/4198) 的改动，升级 TiDB Operator 会导致 TidbMonitor Pod 删除重建。

## 新功能

- 支持为 TiFlash 的 init container 配置资源使用量 ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- 支持为 TiDB 集群开启[持续性能分析](../access-dashboard.md#启用持续性能分析) ([#4287](https://github.com/pingcap/tidb-operator/pull/4287), [@KanShiori](https://github.com/KanShiori))
- 支持通过配置 annotation 的方式优雅重启单个 TiKV Pod ([#4279](https://github.com/pingcap/tidb-operator/pull/4279), [@july2993](https://github.com/july2993))
- 支持为 Discovery 组件自定义 PodSecurityContext 等更多配置 ([#4259](https://github.com/pingcap/tidb-operator/pull/4259), [@csuzhangxc](https://github.com/csuzhangxc), [#4208](https://github.com/pingcap/tidb-operator/pull/4208), [@KanShiori](https://github.com/KanShiori))
- 支持为 TidbCluster CR 配置 PodManagementPolicy ([#4211](https://github.com/pingcap/tidb-operator/pull/4211), [@mianhk](https://github.com/mianhk))
- 支持在 TidbMonitor CR 中配置 Prometheus 分片 ([#4198](https://github.com/pingcap/tidb-operator/pull/4198), [@mikechengwei](https://github.com/mikechengwei))
- 支持在 v1.22 及更新版本的 kubernetes 集群中使用 TiDB Operator ([#4195](https://github.com/pingcap/tidb-operator/pull/4195), [#4202](https://github.com/pingcap/tidb-operator/pull/4202), [@KanShiori](https://github.com/KanShiori))
- 生成 v1 版本 CRD 以支持在 1.22 及更新版本的 Kubernetes 集群中使用 ([#4151](https://github.com/pingcap/tidb-operator/pull/4151), [@KanShiori](https://github.com/KanShiori))

## 优化提升

- 适配 v5.4.0 版本 TiFlash 的配置变动，去除和变更了 TiFlash 的默认配置。如果使用 v1.2 版本 TiDB Operator 部署了 v5.4 及更新版本的 TiDB 集群，升级 TiDB Operator 到 v1.3.0-beta.1 版本会导致 TiFlash 组件滚动更新。([#4358](https://github.com/pingcap/tidb-operator/pull/4358), [@KanShiori](https://github.com/KanShiori))
- 优化 TidbMonitor 部署示例 ([#4242](https://github.com/pingcap/tidb-operator/pull/4242), [@mianhk](https://github.com/mianhk))
- 优化异构集群使用体验，可以在同一个 Dashboard 中查看 TidbCluster 和与它异构部署的 TidbCluster 的监控项 ([#4210](https://github.com/pingcap/tidb-operator/pull/4210), [@mikechengwei](https://github.com/mikechengwei))
- 优化在 TidbMonitor 中使用 secretRef 来获取 Grafana 的密码，避免使用明文密码 ([#4135](https://github.com/pingcap/tidb-operator/pull/4135), [@mianhk](https://github.com/mianhk))
- 优化副本数小于 2 的 PD 和 TiKV 组件升级过程，默认强制升级 PD 和 TiKV 组件，避免升级过程耗时过长 ([#4107](https://github.com/pingcap/tidb-operator/pull/4107), [#4091](https://github.com/pingcap/tidb-operator/pull/4091), [@mianhk](https://github.com/mianhk))
- 升级 Grafana 镜像版本为 7.5.11，提升安全性 ([#4212](https://github.com/pingcap/tidb-operator/pull/4212), [@makocchi-git](https://github.com/makocchi-git))
- 废弃 Pod validating 和 mutating webhook ([#4209](https://github.com/pingcap/tidb-operator/pull/4209), [@mianhk](https://github.com/mianhk))
- Helm chart 支持配置 tidb-controller-manager 的 workers 数量 ([#4111](https://github.com/pingcap/tidb-operator/pull/4111), [@mianhk](https://github.com/mianhk))
