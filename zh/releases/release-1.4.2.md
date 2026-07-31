---
title: TiDB Operator 1.4.2 Release Notes
summary: TiDB Operator 1.4.2 发布，修复了开启 `preferIPv6` 时 TiFlash 没有监听 IPv6 地址的问题。
aliases: ['/zh/tidb-in-kubernetes/dev/release-1.4.2/','/zh/tidb-in-kubernetes/v1.3/release-1.4.2/','/zh/tidb-in-kubernetes/v1.4/release-1.4.2/','/zh/tidb-in-kubernetes/v1.5/release-1.4.2/','/zh/tidb-in-kubernetes/v1.6/release-1.4.2/','/zh/tidb-in-kubernetes/v2.0/release-1.4.2/']
---

# TiDB Operator 1.4.2 Release Notes

发布日期: 2023 年 2 月 3 日

TiDB Operator 版本：1.4.2

## Bug 修复

- 修复开启 `preferIPv6` 的情况下，TiFlash 没有监听 IPv6 地址的问题 ([#4850](https://github.com/pingcap/tidb-operator/pull/4850), [@KanShiori](https://github.com/KanShiori))
