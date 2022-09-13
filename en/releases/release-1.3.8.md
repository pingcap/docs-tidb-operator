---
title: TiDB Operator 1.3.8 Release Notes
---

# TiDB Operator 1.3.8 Release Notes

Release date: September 13, 2022

TiDB Operator version: 1.3.8

## New Features

- Add some special annotaions for TidbCluster to configure min ready duration for TiDB, TiKV and TiFlash, it specifies that the minimum number of seconds for which a newly created Pod should be ready during rolling upgrade ([#4675](https://github.com/pingcap/tidb-operator/pull/4675), [@liubog2008](https://github.com/liubog2008))

## Improvement

- Support graceful upgrade TiCDC pods if pod version is equal or larger than 6.3.0 ([#4697](https://github.com/pingcap/tidb-operator/pull/4697), [@overvenus](https://github.com/overvenus))
