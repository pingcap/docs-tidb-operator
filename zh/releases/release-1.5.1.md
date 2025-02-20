---
title: TiDB Operator 1.5.1 Release Notes
summary: TiDB Operator 1.5.1 发布，新增支持替换 PD、TiKV 和 TiDB 所使用的 volume。修复了多个 Bug，包括手动触发 TiKV eviction 时 PVC Modifier 报错的问题，替换 TiKV volume 过程中再触发 TiKV eviction 时可能造成 TiDB Operator reconcile 死锁的问题，TidbCluster 在 Upgrade 过程中可能无法回滚的问题，以及 MaxReservedTime 选项没有被 backup schedule gc 使用的问题。
---

# TiDB Operator 1.5.1 Release Notes

发布日期: 2023 年 10 月 20 日

TiDB Operator 版本：1.5.1

## 新功能

- 支持替换 PD、TiKV 以及 TiDB 所使用的 volume ([#5150](https://github.com/pingcap/tidb-operator/pull/5150), [@anish-db](https://github.com/anish-db))

## 优化提升

## Bug 修复

- 修复手动触发 TiKV eviction 时 PVC Modifier 报错的问题 ([#5302](https://github.com/pingcap/tidb-operator/pull/5302), [@anish-db](https://github.com/anish-db))
- 修复替换 TiKV volume 过程中再触发 TiKV eviction 时可能造成 TiDB Operator reconcile 死锁的问题 ([#5301](https://github.com/pingcap/tidb-operator/pull/5301), [@anish-db](https://github.com/anish-db))
- 修复 TidbCluster 在 Upgrade 过程中可能无法回滚的问题 ([#5345](https://github.com/pingcap/tidb-operator/pull/5345), [@anish-db](https://github.com/anish-db))
- 修复 MaxReservedTime 选项没有被 backup schedule gc 使用的问题 [#5148](https://github.com/pingcap/tidb-operator/pull/5148), [@BornChanger](https://github.com/BornChanger))
