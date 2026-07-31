---
title: TiDB Operator 1.6.3 Release Notes
summary: Learn about bug fixes in TiDB Operator 1.6.3.
aliases: ['/tidb-in-kubernetes/dev/release-1.6.3/','/tidb-in-kubernetes/v1.3/release-1.6.3/','/tidb-in-kubernetes/v1.4/release-1.6.3/','/tidb-in-kubernetes/v1.5/release-1.6.3/','/tidb-in-kubernetes/v1.6/release-1.6.3/','/tidb-in-kubernetes/v2.0/release-1.6.3/']
---

# TiDB Operator 1.6.3 Release Notes

Release date: July 18, 2025

TiDB Operator version: 1.6.3

## Bug fixes

- Fix the issue that TiDB Operator might panic after online upgrade due to existing log backup tasks in the backup schedule ([#6300](https://github.com/pingcap/tidb-operator/pull/6300), [@RidRisR](https://github.com/RidRisR))
