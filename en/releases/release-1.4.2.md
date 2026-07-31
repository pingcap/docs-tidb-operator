---
title: TiDB Operator 1.4.2 Release Notes
summary: TiDB Operator 1.4.2 was released on February 3, 2023. This version fixed the issue where TiFlash does not listen on IPv6 addresses when the `preferIPv6` configuration is enabled.
aliases: ['/tidb-in-kubernetes/dev/release-1.4.2/','/tidb-in-kubernetes/v1.3/release-1.4.2/','/tidb-in-kubernetes/v1.4/release-1.4.2/','/tidb-in-kubernetes/v1.5/release-1.4.2/','/tidb-in-kubernetes/v1.6/release-1.4.2/','/tidb-in-kubernetes/v2.0/release-1.4.2/']
---

# TiDB Operator 1.4.2 Release Notes

Release date: February 3, 2023

TiDB Operator version: 1.4.2

## Bug fix

- Fix the issue that TiFlash does not listen on IPv6 addresses when the `preferIPv6` configuration is enabled ([#4850](https://github.com/pingcap/tidb-operator/pull/4850), [@KanShiori](https://github.com/KanShiori))
