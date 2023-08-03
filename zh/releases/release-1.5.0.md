---
title: TiDB Operator 1.5.0 Release Notes
---

# TiDB Operator 1.5.0 Release Notes

发布日期: 2023 年 8 月 4 日

TiDB Operator 版本：1.5.0

## 滚动升级改动

- 由于 [#5075](https://github.com/pingcap/tidb-operator/pull/5075) 的改动，如果 v7.1.0+ 版本的集群中部署了 TiFlash，升级 TiDB Operator 到 v1.5.0 之后 TiFlash 组件会滚动升级。

## 新功能

- 添加 BR Federation Manager，支持跨多个 Kubernetes 集群编排 `Backup` 和 `Restore` CR ([#4996](https://github.com/pingcap/tidb-operator/pull/4996), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持用 `VolumeBackup` 对跨多个 Kubernetes 部署的 TiDB 集群做基于 EBS snapshot 的备份 ([#5013](https://github.com/pingcap/tidb-operator/pull/5013), [@WangLe1321](https://github.com/WangLe1321))
- 支持用 `VolumeRestore` 对跨多个 Kubernetes 部署的 TiDB 集群做基于 EBS snapshot 的恢复 ([#5039](https://github.com/pingcap/tidb-operator/pull/5039), [@WangLe1321](https://github.com/WangLe1321))
- 支持用 `VolumeBackupSchedule` 对跨多个 Kubernetes 部署的 TiDB 集群做基于 EBS snapshot 的自动备份 ([#5036](https://github.com/pingcap/tidb-operator/pull/5036), [@BornChanger](https://github.com/BornChanger))
- 支持对跨多个 Kubernetes 部署的 TiDB 集群做基于 EBS snapshot 的备份时备份与 `TidbCluster` 相关的 CR 数据 ([#5207](https://github.com/pingcap/tidb-operator/pull/5207), [@WangLe1321](https://github.com/WangLe1321))

## 优化提升

- 为 DM master 增加 `startUpScriptVersion` 字段以支持设置启动脚本版本 ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))
- 为 DmCluster、TidbDashboard、TidbMonitor 以及 TidbNGMonitoring 增加 `spec.preferIPv6` 支持 ([#4977](https://github.com/pingcap/tidb-operator/pull/4977), [@KanShiori](https://github.com/KanShiori))
- 支持为 TiKV 驱逐 leader 和 PD 转移 leader 设置过期时间 ([#4997](https://github.com/pingcap/tidb-operator/pull/4997), [@Tema](https://github.com/Tema))
- 支持为 TidbInitializer 设置 tolerations  ([#5047](https://github.com/pingcap/tidb-operator/pull/5047), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 PD 设置启动超时时间 ([#5071](https://github.com/pingcap/tidb-operator/pull/5071), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- 当 TiKV 在扩展 PVC 的大小时不再执行驱逐 leader 操作 ([#5101](https://github.com/pingcap/tidb-operator/pull/5101), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持更新 PD、TiKV、TiFlash、TiProxy、DM-Master 与 DM-worker 组件 Service 的 annotation 与 label ([#4973](https://github.com/pingcap/tidb-operator/pull/4973), [@wxiaomou](https://github.com/wxiaomou))
- 默认启用 volume resize 支持 ([#5167](https://github.com/pingcap/tidb-operator/pull/5167), [@liubog2008](https://github.com/liubog2008))

## Bug 修复

- 修复升级 TiKV 时由于部分 store 下线而造成失去 quorum 的问题 ([#4979](https://github.com/pingcap/tidb-operator/pull/4979), [@Tema](https://github.com/Tema))
- 修复升级 PD 时由于部分 member 下线而造成失去 quorum 的问题 ([#4995](https://github.com/pingcap/tidb-operator/pull/4995), [@Tema](https://github.com/Tema))
- 修复 TiDB Operator 在未配置任何 Kubernetes 集群级别权限时 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- 修复在 TidbCluster 中设置 `AdditionalVolumeMounts` 时 TiDB Operator 可能 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- 修复 TidbDashboard 在使用自定义 image registry 时解析 `baseImage` 错误的问题 ([#5014](https://github.com/pingcap/tidb-operator/pull/5014), [@linkinghack](https://github.com/linkinghack))
