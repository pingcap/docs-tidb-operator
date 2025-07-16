---
title: TiDB Operator 1.6.3 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.3.
---

# TiDB Operator 1.6.3 Release Notes

Release date: July 18, 2025

TiDB Operator version: 1.6.3

## Improvements

- Support evicting TiKV leaders before deleting a store when scaling in TiKV nodes ([#6239](https://github.com/pingcap/tidb-operator/pull/6239), [@liubog2008](https://github.com/liubog2008))


## Bug fixes

- Fix the issue that the TidbCluster CR is incorrectly marked as `Ready` when some Tiproxy Pods are unhealthy ([#6151](https://github.com/pingcap/tidb-operator/pull/6151), [@ideascf](https://github.com/ideascf))

