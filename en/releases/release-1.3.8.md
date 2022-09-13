---
title: TiDB Operator 1.3.8 Release Notes
---

# TiDB Operator 1.3.8 Release Notes

Release date: September 13, 2022

TiDB Operator version: 1.3.8

## New Feature

- Add some special annotaions for TidbCluster to configure the minimum ready duration for TiDB, TiKV, and TiFlash. The minimum ready duration specifies the minimum number of seconds that a newly created Pod takes to be ready during a rolling upgrade ([#4675](https://github.com/pingcap/tidb-operator/pull/4675), [@liubog2008](https://github.com/liubog2008))

## Improvement

- Support graceful upgrade of a TiCDC Pod if the Pod version is v6.3.0 or later versions ([#4697](https://github.com/pingcap/tidb-operator/pull/4697), [@overvenus](https://github.com/overvenus))
