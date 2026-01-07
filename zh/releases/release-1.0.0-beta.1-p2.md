---
title: TiDB Operator 1.0 Beta.1 P2 Release Notes
summary: TiDB Operator 1.0 Beta.1 P2 was released on February 21, 2019. Notable changes include a new algorithm for scheduler HA predicate, addition of TiDB discovery service, serial scheduling, change in tolerations type to an array, direct start when there is a join file, addition of code coverage icon, omission of just the empty leaves in `values.yml`, backup to ceph object storage in charts, and addition of `ClusterIDLabelKey` label to TidbCluster.
---

# TiDB Operator 1.0 Beta.1 P2 Release Notes

Release date: February 21, 2019

TiDB Operator version: 1.0.0-beta.1-p2

## Notable Changes

- New algorithm for scheduler HA predicate ([#260](https://github.com/pingcap/tidb-operator/pull/260))
- Add TiDB discovery service ([#262](https://github.com/pingcap/tidb-operator/pull/262))
- Serial scheduling ([#266](https://github.com/pingcap/tidb-operator/pull/266))
- Change tolerations type to an array ([#271](https://github.com/pingcap/tidb-operator/pull/271))
- Start directly when where is join file ([#275](https://github.com/pingcap/tidb-operator/pull/275))
- Add code coverage icon ([#272](https://github.com/pingcap/tidb-operator/pull/272))
- In `values.yml`, omit just the empty leaves ([#273](https://github.com/pingcap/tidb-operator/pull/273))
- Charts: backup to ceph object storage ([#280](https://github.com/pingcap/tidb-operator/pull/280))
- Add `ClusterIDLabelKey` label to TidbCluster ([#279](https://github.com/pingcap/tidb-operator/pull/279))
