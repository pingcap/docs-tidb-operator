---
title: TiDB Operator 1.5.0 Release Notes
summary: 了解 TiDB Operator 1.5.0 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.5.0 Release Notes

发布日期: 2023 年 8 月 4 日

TiDB Operator 版本：1.5.0

## 滚动升级改动

由于 [#5075](https://github.com/pingcap/tidb-operator/pull/5075) 的改动，如果 TiDB v7.1.0 或以上版本的集群中部署了 TiFlash，升级 TiDB Operator 到 v1.5.0 之后 TiFlash 组件会滚动升级。

## 新功能

- 新增 BR Federation Manager 组件，支持跨多个 Kubernetes 集群编排 `Backup` 和 `Restore` custom resources (CR) ([#4996](https://github.com/pingcap/tidb-operator/pull/4996), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持使用 `VolumeBackup` CR 对跨多个 Kubernetes 部署的 TiDB 集群进行基于 EBS 快照的备份 ([#5013](https://github.com/pingcap/tidb-operator/pull/5013), [@WangLe1321](https://github.com/WangLe1321))
- 支持使用 `VolumeRestore` CR 对跨多个 Kubernetes 部署的 TiDB 集群进行基于 EBS 快照的恢复 ([#5039](https://github.com/pingcap/tidb-operator/pull/5039), [@WangLe1321](https://github.com/WangLe1321))
- 支持使用 `VolumeBackupSchedule` CR 对跨多个 Kubernetes 部署的 TiDB 集群进行基于 EBS 快照的自动备份 ([#5036](https://github.com/pingcap/tidb-operator/pull/5036), [@BornChanger](https://github.com/BornChanger))
- 当对跨多个 Kubernetes 部署的 TiDB 集群进行基于 EBS 快照的备份时，支持备份与 `TidbCluster` 相关的 CR 数据 ([#5207](https://github.com/pingcap/tidb-operator/pull/5207), [@WangLe1321](https://github.com/WangLe1321))

## 优化提升

- 为 DM master 添加 `startUpScriptVersion` 字段，支持设置启动脚本的版本 ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))
- 为 DmCluster、TidbDashboard、TidbMonitor 以及 TidbNGMonitoring 增加 `spec.preferIPv6` 支持 ([#4977](https://github.com/pingcap/tidb-operator/pull/4977), [@KanShiori](https://github.com/KanShiori))
- 支持为 TiKV 驱逐 leader 和 PD 转移 leader 设置过期时间 ([#4997](https://github.com/pingcap/tidb-operator/pull/4997), [@Tema](https://github.com/Tema))
- 支持为 `TidbInitializer` 设置 tolerations  ([#5047](https://github.com/pingcap/tidb-operator/pull/5047), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 PD 设置启动超时时间 ([#5071](https://github.com/pingcap/tidb-operator/pull/5071), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- 当 TiKV 在扩展 PVC 的大小时，不再执行驱逐 leader 操作，避免因磁盘容量不足而造成驱逐卡住 ([#5101](https://github.com/pingcap/tidb-operator/pull/5101), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持更新 PD、TiKV、TiFlash、TiProxy、DM-Master 与 DM-worker 组件 Service 的 annotation 与 label ([#4973](https://github.com/pingcap/tidb-operator/pull/4973), [@wxiaomou](https://github.com/wxiaomou))
- 默认启用 volume resize，支持对 PV 的扩容 ([#5167](https://github.com/pingcap/tidb-operator/pull/5167), [@liubog2008](https://github.com/liubog2008))

## Bug 修复

- 修复升级 TiKV 时由于部分 store 下线而造成 quorum 丢失的问题 ([#4979](https://github.com/pingcap/tidb-operator/pull/4979), [@Tema](https://github.com/Tema))
- 修复升级 PD 时由于部分 member 下线而造成 quorum 丢失的问题 ([#4995](https://github.com/pingcap/tidb-operator/pull/4995), [@Tema](https://github.com/Tema))
- 修复 TiDB Operator 在未配置任何 Kubernetes 集群级别权限时 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- 修复在 `TidbCluster` CR 中设置 `AdditionalVolumeMounts` 时 TiDB Operator 可能 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- 修复 `TidbDashboard` CR 在使用自定义的 image registry 时解析 `baseImage` 错误的问题 ([#5014](https://github.com/pingcap/tidb-operator/pull/5014), [@linkinghack](https://github.com/linkinghack))
