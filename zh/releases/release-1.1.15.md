---
title: TiDB Operator 1.1.15 Release Notes
summary: TiDB Operator 1.1.15 发布日期为 2022 年 2 月 17 日。此版本修复了 TiDB Operator 计算 TiKV Region leader 数量时可能会造成 goroutine 泄露的问题。
aliases: ['/zh/tidb-in-kubernetes/dev/release-1.1.15/','/zh/tidb-in-kubernetes/v1.3/release-1.1.15/','/zh/tidb-in-kubernetes/v1.4/release-1.1.15/','/zh/tidb-in-kubernetes/v1.5/release-1.1.15/','/zh/tidb-in-kubernetes/v1.6/release-1.1.15/','/zh/tidb-in-kubernetes/v2.0/release-1.1.15/']
---

# TiDB Operator 1.1.15 Release Notes

发布日期：2022 年 2 月 17 日

TiDB Operator 版本：1.1.15

## Bug 修复

- 修复 TiDB Operator 计算 TiKV Region leader 数量时可能会造成 goroutine 泄露的问题 ([#4291](https://github.com/pingcap/tidb-operator/pull/4291), [@DanielZhangQD](https://github.com/DanielZhangQD))