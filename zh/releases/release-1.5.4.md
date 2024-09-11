---
title: TiDB Operator 1.5.4 Release Notes
summary: 了解 TiDB Operator 1.5.4 版本的新功能和 Bug 修复。
---

# TiDB Operator 1.5.4 Release Notes

发布日期：2024 年 9 月 13 日

TiDB Operator 版本：1.5.4

## 优化提升

- VolumeReplace 功能支持为 PD 和 TiKV 自定义备用副本数量 ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- VolumeReplace 功能支持仅为特定 TiDB 集群开启 ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- EBS 快照恢复支持设定某个卷 warmup 失败是否立刻整个恢复作业 ([#5635](https://github.com/pingcap/tidb-operator/pull/5635), [@michealdeng](https://github.com/[michaelmdeng](https://github.com/michaelmdeng)))
- EBS 快照恢复在使用 `check-wal-only` 策略时，warmup 失败会将整个 restore 失败 ([#5636](https://github.com/pingcap/tidb-operator/pull/5636), [@michealdeng](https://github.com/[michaelmdeng](https://github.com/michaelmdeng)))
## Bug 修复

- 修复 tidb-backup-manager 无法解析 BR backupmeta v2 中备份文件存储大小的问题 ([#5411](https://github.com/pingcap/tidb-operator/pull/5411), [@Leavrth](https://github.com/Leavrth))
- 支持 EBS snapshot volume 恢复失败时，清理 EBS 卷的能力 ([#5639](https://github.com/pingcap/tidb-operator/pull/5639), [@WangLe1321](https://github.com/WangLe1321))
- federated manager 重启后，重置相关的 metrics 指标 ([#5648](https://github.com/pingcap/tidb-operator/pull/5648), [@wxiaomou](https://github.com/wxiaomou))
- EBS Snapshot 备份增强对 TC 检查，如果集群没有配置 TiKV 节点或者 TiKV replica 为0的时候，让备份失败 ([#5662](https://github.com/pingcap/tidb-operator/pull/5662), [@BornChanger ](https://github.com/BornChanger))
