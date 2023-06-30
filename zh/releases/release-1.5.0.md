---
title: TiDB Operator 1.5.0 Release Notes
---

# TiDB Operator 1.5.0 Release Notes

发布日期: 2023 年 7 月 TODO 日

TiDB Operator 版本：1.5.0

## 新功能

- TODO

## 优化提升

- 为 DM master 增加 `startUpScriptVersion` 字段以支持设置启动脚本版本 ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))
- 为 DmCluster、TidbDashboard、TidbMonitor 以及 TidbNGMonitoring 增加 `spec.preferIPv6` 支持 ([#4977](https://github.com/pingcap/tidb-operator/pull/4977), [@KanShiori](https://github.com/KanShiori))
- 支持为 TiKV 驱逐 leader 和 PD 转移 leader 设置过期时间 ([#4997](https://github.com/pingcap/tidb-operator/pull/4997), [@Tema](https://github.com/Tema))
- 支持为 TidbInitializer 设置 tolerations  ([#5047](https://github.com/pingcap/tidb-operator/pull/5047), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 PD 设置启动超时时间 ([#5071](https://github.com/pingcap/tidb-operator/pull/5071), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- 当 TiKV 在扩展 PVC 的大小时不再执行驱逐 leader 操作 ([#5101](https://github.com/pingcap/tidb-operator/pull/5101), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug 修复

- 修复升级 TiKV 时由于部分 store 下线而造成失去 quorum 的问题 ([#4979](https://github.com/pingcap/tidb-operator/pull/4979), [@Tema](https://github.com/Tema))
- 修复升级 PD 时由于部分 member 下线而造成失去 quorum 的问题 ([#4995](https://github.com/pingcap/tidb-operator/pull/4995), [@Tema](https://github.com/Tema))
- 修复 TiDB Operator 在未配置任何 Kubernetes 集群级别权限时 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- 修复在 TidbCluster 中设置 `AdditionalVolumeMounts` 时 TiDB Operator 可能 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
