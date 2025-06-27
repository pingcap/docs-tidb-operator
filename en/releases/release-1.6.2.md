---
title: TiDB Operator 1.6.2 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.2.
---

# TiDB Operator 1.6.2 Release Notes

Release date: July 4, 2025

TiDB Operator version: 1.6.2

## New features


## Improvements

- Support evicting TiKV leaders before deleting a store when scaling in TiKV ([#6239](https://github.com/pingcap/tidb-operator/pull/6239), [@liubog2008](https://github.com/liubog2008))
- Support checking if PD members are ready with the new PD `ready` API when upgrading PD ([#6243](https://github.com/pingcap/tidb-operator/pull/6243), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug fixes

- Fix the issue that TidbCluster CR is marked as `Ready` but there are some tiproxy pods are unhealthy ([#6151](https://github.com/pingcap/tidb-operator/pull/6151), [@ideascf](https://github.com/ideascf))
