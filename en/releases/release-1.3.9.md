---
title: TiDB Operator 1.3.9 Release Notes
---

# TiDB Operator 1.3.9 Release Notes

Release date: October 10, 2022

TiDB Operator version: 1.3.9

## Bug fix

- Fix the issue that PD upgrade will stucks if the `acrossK8s` field is set but the `clusterDomain` is not set ([#4522](https://github.com/pingcap/tidb-operator/pull/4721), [@liubog2008](https://github.com/liubog2008))
