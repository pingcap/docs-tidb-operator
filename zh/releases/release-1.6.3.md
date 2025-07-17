---
title: TiDB Operator 1.6.3 Release Notes
summary: 了解 TiDB Operator 1.6.3 版本的 Bug 修复。
---

# TiDB Operator 1.6.3 Release Notes

发布日期：2025 年 7 月 18 日

TiDB Operator 版本：1.6.3

## Bug 修复

- 修复 Operator 在线升级后会因为已经存在的 Backup Schedule 中的 Log Backup 而崩溃的问题 ([#6300](https://github.com/pingcap/tidb-operator/pull/6300), [@RidRisR](https://github.com/RidRisR))
