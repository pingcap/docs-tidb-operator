---
title: TiDB Operator 1.2.2 Release Notes
summary: TiDB Operator 1.2.2 版本发布日期为 2021 年 9 月 3 日。滚动升级改动包括升级 TiDB Operator 会导致 TiDBMonitor Pod 和 TiFlash Pod 删除重建。新功能包括 TiDBMonitor 支持动态重新加载配置。Bug 修复包括修复 TiCDC 无法从低版本升级到 v5.2.0 的问题。
---

# TiDB Operator 1.2.2 Release Notes

发布日期：2021 年 9 月 3 日

TiDB Operator 版本：1.2.2

## 滚动升级改动

- 由于 [#4158](https://github.com/pingcap/tidb-operator/pull/4158) 的改动，升级 TiDB Operator 会导致 TiDBMonitor Pod 删除重建
- 由于 [#4152](https://github.com/pingcap/tidb-operator/pull/4152) 的改动，升级 TiDB Operator 会导致 TiFlash Pod 删除重建

## 新功能

- TiDBMonitor 支持动态重新加载配置 ([#4158](https://github.com/pingcap/tidb-operator/pull/4158), [@mikechengwei](https://github.com/mikechengwei))

## Bug 修复

- 修复 TiCDC 无法从低版本升级到 v5.2.0 的问题 ([#4171](https://github.com/pingcap/tidb-operator/pull/4171), [@KanShiori](https://github.com/KanShiori))
