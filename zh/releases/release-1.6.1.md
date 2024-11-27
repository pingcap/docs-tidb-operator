---
title: TiDB Operator 1.6.1 Release Notes
summary: 了解 TiDB Operator 1.6.1 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.1 Release Notes

发布日期: 2024 年 12 月 6 日

TiDB Operator 版本：1.6.1

## 新功能

- 备份和恢复支持使用 Azure Blob 存储 SAS 令牌认证 ([#5720](https://github.com/pingcap/tidb-operator/pull/5720), [@tennix](https://github.com/tennix))
- VolumeReplace 功能支持 TiFlash 组件 ([#5685](https://github.com/pingcap/tidb-operator/pull/5685), [@rajsuvariya](https://github.com/rajsuvariya))

## 优化提升

- VolumeModify 功能不再对 TiKV 执行 evict leader 操作以缩短变更时间 ([#5826](https://github.com/pingcap/tidb-operator/pull/5826), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持通过 annotation 指定滚动更新 PD Pod 过程中的最小等待时间 ([#5827](https://github.com/pingcap/tidb-operator/pull/5827), [@csuzhangxc](https://github.com/csuzhangxc))
- VolumeReplace 功能支持为 PD 和 TiKV 自定义备用副本数量 ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- VolumeReplace 功能支持仅为特定 TiDB 集群开启 ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- 优化 PD 微服务 transfer primary 逻辑，减少组件更新时 transfer primary 的次数 ([#5643](https://github.com/pingcap/tidb-operator/pull/5643), [@HuSharp](https://github.com/HuSharp))

## Bug 修复

- 修复在没有配置 TiKV 节点或者 TiKV 副本数为 0 时，EBS 快照恢复错误地显示为成功的问题 ([#5659](https://github.com/pingcap/tidb-operator/pull/5659), [@BornChanger](https://github.com/BornChanger))
- 修复跨 namespace 监控多套 TiDB 集群的 TidbMonitor 在删除后对应的 ClusterRole/ClusterRolebinding 未被正常清理的问题 ([#5956](https://github.com/pingcap/tidb-operator/pull/5956), [@csuzhangxc](https://github.com/csuzhangxc))
