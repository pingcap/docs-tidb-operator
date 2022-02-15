---
title: TiDB Operator 1.3.0 Release Notes
---

# TiDB Operator 1.3.0 Release Notes

发布日期: 2022 年 2 月 15 日

TiDB Operator 版本：1.3.0

## 兼容性改动

- 由于 [#4400](https://github.com/pingcap/tidb-operator/pull/4400) 的变更，如果使用 v1.3.0-beta.1 及更早版本的 TiDB Operator 跨 Kubernetes 集群部署 TiDB 集群，直接升级 TiDB Operator 会导致集群进行失败的滚动更新。你需要执行以下操作来升级 TiDB Operator：
    1. 更新 CRD。
    2. 添加新的 `spec.acrossK8s` 字段设置为 `true` 到 TidbCluster 定义。
    3. 升级 TiDB Operator。

## 新功能

- 添加新的 `spec.tidb.tlsClient.skipInternalClientCA` 字段，以支持内部组件访问 TiDB 时跳过服务端证书验证 ([#4388](https://github.com/pingcap/tidb-operator/pull/4388), [@just1900](https://github.com/just1900))
- 支持设置所有组件 Pod 的 DNS 配置 ([#4394](https://github.com/pingcap/tidb-operator/pull/4394), [@handlerww](https://github.com/handlerww))
- 添加新的 `spec.tidb.initializer.createPassword` 字段，支持部署新集群时为 TiDB 设置随机密码 ([#4328](https://github.com/pingcap/tidb-operator/pull/4328), [@mikechengwei](https://github.com/mikechengwei))
- 添加新的 `failover.recoverByUID` 字段，以支持为 TiKV/TiFlash/DM Worker 仅执行一次性的 Recover 操作 ([#4373](https://github.com/pingcap/tidb-operator/pull/4373), [@better0332](https://github.com/better0332))
- 添加新的 `sepc.pd.startUpScriptVersion` 字段，以支持在 PD 启动脚本中使用 `dig` 命令而不是 `nslookup` 命令来解析域名 ([#4379](https://github.com/pingcap/tidb-operator/pull/4379), [@july2993](https://github.com/july2993))

## 优化提升

- 部署或更新组件的 StatefulSet 预先检查配置的 VolumeMount 是否存在，防止集群进行失败的滚动更新 ([#4369](https://github.com/pingcap/tidb-operator/pull/4369), [@july2993](https://github.com/july2993))
- 跨 Kubernetes 集群部署 TiDB 集群功能增强，包括：
    - 添加新的 `spec.acrossK8s` 字段来表示跨 Kubernetes 集群部署 TiDB 集群 ([#4400](https://github.com/pingcap/tidb-operator/pull/4400), [@KanShiori](https://github.com/KanShiori))
    - 支持跨 Kubernetes 集群部署 Heterogeneous TiDB 集群 ([#4387](https://github.com/pingcap/tidb-operator/pull/4387), [@KanShiori](https://github.com/KanShiori))
    - 跨 Kubernetes 集群部署 TiDB 集群场景下 `spec.clusterDomain` 字段不是必须的，该字段仅仅用于组件间访问的地址 ([#4408](https://github.com/pingcap/tidb-operator/pull/4408), [@KanShiori](https://github.com/KanShiori))
    - 修复跨 Kubernetes 部署 TiDB 的场景下，某集群的所有 PD 下线导致同一集群内 Pump 异常的问题 ([#4377](https://github.com/pingcap/tidb-operator/pull/4377), [@just1900](https://github.com/just1900))

## Bug 修复

- 修复 Kubernetes v1.23 及之后版本无法部署 tidb scheduler 的问题 ([#4386](https://github.com/pingcap/tidb-operator/pull/4386), [@just1900](https://github.com/just1900))