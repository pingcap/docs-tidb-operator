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

## Bug 修复

- 修复 tidb-backup-manager 无法解析 BR backupmeta v2 中备份文件存储大小的问题 ([#5411](https://github.com/pingcap/tidb-operator/pull/5411), [@Leavrth](https://github.com/Leavrth))
