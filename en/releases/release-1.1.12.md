---
title: TiDB Operator 1.1.12 Release Notes
summary: TiDB Operator 1.1.12 was released on April 15, 2021. New features include support for customized environment variables for backup and restore job containers, additional volume and volumeMount configurations for TidbMonitor, and the use of new service account resources in the tidb-operator chart. Improvements include DNS lookup failure exception retry, support for multiple PVCs for PD during scaling and failover, and optimization of the PodsAreChanged function. Bug fixes address issues with PVC size configuration, panic issue with TLS enabled TidbCluster CR, and wrong PVC status in UnjoinedMembers for PD and DM.
---

# TiDB Operator 1.1.12 Release Notes

Release date: April 15, 2021

TiDB Operator version: 1.1.12

## New Features

- Support setting customized environment variables for backup and restore job containers ([#3833](https://github.com/pingcap/tidb-operator/pull/3833), [@dragonly](https://github.com/dragonly))
- Add additional volume and volumeMount configurations to TidbMonitor ([#3855](https://github.com/pingcap/tidb-operator/pull/3855), [@mikechengwei](https://github.com/mikechengwei))
- The resources in the tidb-operator chart use the new service account when `appendReleaseSuffix` is set to `true` ([#3819](https://github.com/pingcap/tidb-operator/pull/3819), [@DanielZhangQD](https://github.com/DanielZhangQD))

## Improvements

- Add retry for DNS lookup failure exception in TiDBInitializer ([#3884](https://github.com/pingcap/tidb-operator/pull/3884), [@handlerww](https://github.com/handlerww))
- Support multiple PVCs for PD during scaling and failover ([#3820](https://github.com/pingcap/tidb-operator/pull/3820), [@dragonly](https://github.com/dragonly))
- Optimize the `PodsAreChanged` function ([#3901](https://github.com/pingcap/tidb-operator/pull/3901), [@shonge](https://github.com/shonge))

## Bug Fixes

- Fix the issue that PVCs will be set to incorrect size if multiple PVCs are configured for PD/TiKV ([#3858](https://github.com/pingcap/tidb-operator/pull/3858), [@dragonly](https://github.com/dragonly))
- Fix the panic issue when `.spec.tidb` is not set in the TidbCluster CR with TLS enabled ([#3852](https://github.com/pingcap/tidb-operator/pull/3852), [@dragonly](https://github.com/dragonly))
- Fix the wrong PVC status in `UnjoinedMembers` for PD and DM ([#3836](https://github.com/pingcap/tidb-operator/pull/3836), [@dragonly](https://github.com/dragonly))
