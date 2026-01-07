---
title: TiDB Operator 1.5.4 Release Notes
summary: 了解 TiDB Operator 1.5.4 版本的优化提升和 Bug 修复。
---

# TiDB Operator 1.5.4 Release Notes

发布日期：2024 年 9 月 13 日

TiDB Operator 版本：1.5.4

## 优化提升

- VolumeReplace 功能支持为 PD 和 TiKV 自定义备用副本数量 ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- VolumeReplace 功能支持仅为特定 TiDB 集群开启 ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- EBS 快照恢复支持设定某个卷 warmup 失败时是否立即终止整个恢复任务 ([#5622](https://github.com/pingcap/tidb-operator/pull/5622), [@michaelmdeng](https://github.com/michaelmdeng))
- EBS 快照恢复在使用 `check-wal-only` 策略时，如果 warmup 失败，整个恢复任务将被设置为失败 ([#5621](https://github.com/pingcap/tidb-operator/pull/5621), [@michaelmdeng](https://github.com/michaelmdeng))

## Bug 修复

- 修复 `tidb-backup-manager` 无法解析 BR backupmeta v2 中备份文件大小的问题 ([#5411](https://github.com/pingcap/tidb-operator/pull/5411), [@Leavrth](https://github.com/Leavrth))
- 修复 EBS 快照恢复失败时，EBS 卷可能泄露的问题 ([#5634](https://github.com/pingcap/tidb-operator/pull/5634), [@WangLe1321](https://github.com/WangLe1321))
- 修复 Federated manager 重启后未正确初始化相关指标的问题 ([#5637](https://github.com/pingcap/tidb-operator/pull/5637), [@wxiaomou](https://github.com/wxiaomou))
- 修复在没有配置 TiKV 节点或者 TiKV 副本数为 0 时，EBS 快照恢复错误地显示为成功的问题 ([#5659](https://github.com/pingcap/tidb-operator/pull/5659), [@BornChanger](https://github.com/BornChanger))
