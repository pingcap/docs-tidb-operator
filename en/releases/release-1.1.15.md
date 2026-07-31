---
title: TiDB Operator 1.1.15 Release Notes
summary: TiDB Operator 1.1.15 was released on February 17, 2022. This version includes a bug fix for a potential goroutine leak when TiDB Operator checks the Region leader count of TiKV.
aliases: ['/tidb-in-kubernetes/dev/release-1.1.15/','/tidb-in-kubernetes/v1.3/release-1.1.15/','/tidb-in-kubernetes/v1.4/release-1.1.15/','/tidb-in-kubernetes/v1.5/release-1.1.15/','/tidb-in-kubernetes/v1.6/release-1.1.15/','/tidb-in-kubernetes/v2.0/release-1.1.15/']
---

# TiDB Operator 1.1.15 Release Notes

Release date: February 17, 2022

TiDB Operator version: 1.1.15

## Bug Fixes

- Fix a potential goroutine leak when TiDB Operator checks the Region leader count of TiKV ([#4291](https://github.com/pingcap/tidb-operator/pull/4291), [@DanielZhangQD](https://github.com/DanielZhangQD))
