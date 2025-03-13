---
title: TiDB Operator 1.6.1 Release Notes
summary: 了解 TiDB Operator 1.6.1 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.1 Release Notes

发布日期: 2024 年 12 月 25 日

TiDB Operator 版本：1.6.1

## 新功能

- 备份与恢复功能支持使用 Azure Blob Storage 的共享访问签名 (SAS) 令牌 ([#5720](https://github.com/pingcap/tidb-operator/pull/5720), [@tennix](https://github.com/tennix))
- VolumeReplace 功能支持 TiFlash 组件 ([#5685](https://github.com/pingcap/tidb-operator/pull/5685), [@rajsuvariya](https://github.com/rajsuvariya))
- 日志备份功能新增一个更直观的接口，支持暂停和恢复日志备份任务 ([#5710](https://github.com/pingcap/tidb-operator/pull/5710), [@RidRisR](https://github.com/RidRisR))
- 日志备份功能支持通过直接删除 CR 停止备份任务 ([#5754](https://github.com/pingcap/tidb-operator/pull/5754), [@RidRisR](https://github.com/RidRisR))
- VolumeModify 功能支持修改 Azure Premium SSD v2 磁盘。使用该功能时需要通过 node 或 Pod 授予 tidb-controller-manager 操作 Azure Disk 的权限 ([#5958](https://github.com/pingcap/tidb-operator/pull/5958), [@handlerww](https://github.com/handlerww))

## 优化提升

- VolumeModify 功能不再对 TiKV 执行 evict leader 操作以缩短变更所需的时间 ([#5826](https://github.com/pingcap/tidb-operator/pull/5826), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持通过 annotation 指定 PD Pod 滚动更新过程中的最小等待时间 ([#5827](https://github.com/pingcap/tidb-operator/pull/5827), [@csuzhangxc](https://github.com/csuzhangxc))
- VolumeReplace 功能支持为 PD 和 TiKV 自定义备用副本数量 ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- VolumeReplace 功能支持仅为特定 TiDB 集群开启 ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- 优化 PD 微服务 transfer primary 逻辑，减少组件更新时 transfer primary 的次数 ([#5643](https://github.com/pingcap/tidb-operator/pull/5643), [@HuSharp](https://github.com/HuSharp))
- 支持为 TiDB 的 service 设置 `LoadBalancerClass` ([#5964](https://github.com/pingcap/tidb-operator/pull/5964), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug 修复

- 修复在没有配置 TiKV 节点或者 TiKV 副本数为 0 时，EBS 快照恢复错误地显示为成功的问题 ([#5659](https://github.com/pingcap/tidb-operator/pull/5659), [@BornChanger](https://github.com/BornChanger))
- 修复在跨命名空间监控多个 TiDB 集群时，删除 `TidbMonitor` 后，相关的 ClusterRole 和 ClusterRolebinding 未被正确清理的问题 ([#5956](https://github.com/pingcap/tidb-operator/pull/5956), [@csuzhangxc](https://github.com/csuzhangxc))
- 修复 `TidbMonitor` 中 `.spec.prometheus.remoteWrite.remoteTimeout` 类型不匹配的问题 ([#5734](https://github.com/pingcap/tidb-operator/pull/5734), [@IMMORTALxJO](https://github.com/IMMORTALxJO))
