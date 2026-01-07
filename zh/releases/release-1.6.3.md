---
title: TiDB Operator 1.6.3 Release Notes
summary: 了解 TiDB Operator 1.6.3 版本的 Bug 修复。
---

# TiDB Operator 1.6.3 Release Notes

发布日期：2025 年 7 月 18 日

TiDB Operator 版本：1.6.3

## Bug 修复

- 修复在线升级 TiDB Operator 后，由于 backup schedule 中已经存在日志备份任务，导致 TiDB Operator 崩溃的问题 ([#6300](https://github.com/pingcap/tidb-operator/pull/6300), [@RidRisR](https://github.com/RidRisR))
