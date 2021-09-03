---
title: TiDB Operator 1.2.2 Release Notes
---

# TiDB Operator 1.2.2 Release Notes

发布日期：2021 年 9 月 3 日

TiDB Operator 版本：1.2.2

## 新功能

- TiDBMonitor 支持动态重新加载配置 ([#4158](https://github.com/pingcap/tidb-operator/pull/4158), [@mikechengwei](https://github.com/mikechengwei))

## Bug 修复

- 在协调 TiDB 之后协调 TiCDC，以修复 TiCDC 无法升级到 v5.2.0 的问题 ([#4171](https://github.com/pingcap/tidb-operator/pull/4171), [@KanShiori](https://github.com/KanShiori))
