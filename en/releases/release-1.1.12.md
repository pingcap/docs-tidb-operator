---
title: TiDB Operator 1.1.12 Release Notes
---

# TiDB Operator 1.1.12 Release Notes

Release date: April 15, 2021

TiDB Operator version: 1.1.12

## New Features

- Support setting customized `ENV` for `Backup` and `Restore` jobs ([#3833](https://github.com/pingcap/tidb-operator/pull/3833), [@dragonly](https://github.com/dragonly))
- Support `affinity` and `tolerations` in `Backup` and `Restore` jobs ([#3835](https://github.com/pingcap/tidb-operator/pull/3835), [@dragonly](https://github.com/dragonly))
- Support setting customized TiKV store labels according to the node labels ([#3784](https://github.com/pingcap/tidb-operator/pull/3784), [@L3T](https://github.com/L3T))

## Improvements

- Add retry for DNS lookup failure exception in `TidbInitializer` ([#3884](https://github.com/pingcap/tidb-operator/pull/3884), [@handlerww](https://github.com/handlerww))
- The resources in the TiDB Operator Helm chart use the new service account when `appendReleaseSuffix` is set to `true` ([#3819](https://github.com/pingcap/tidb-operator/pull/3819), [@DanielZhangQD](https://github.com/DanielZhangQD))
- Optimize `PodsAreChanged` function ([#3901](https://github.com/pingcap/tidb-operator/pull/3901), [@shonge](https://github.com/shonge))
- Add E2E serial test case "Canary Deploy Operator from 1.1.10 to latest" ([#3764](https://github.com/pingcap/tidb-operator/pull/3764), [@shonge](https://github.com/shonge))

## Bug Fixes

- Fix the issue that multiple PVC is treated wrong in PVC resizer ([#3858](https://github.com/pingcap/tidb-operator/pull/3858) [#3891](https://github.com/pingcap/tidb-operator/pull/3891), [@dragonly](https://github.com/dragonly))
- Fix the panic issue that when `TidbCluster`'s `.spec.tidb` is unset ([#3852](https://github.com/pingcap/tidb-operator/pull/3852), [@dragonly](https://github.com/dragonly))
- Fix the wrong PVC status in `UnjoinedMembers` for PD and DM ([#3836](https://github.com/pingcap/tidb-operator/pull/3836), [@dragonly](https://github.com/dragonly))
- Fix support for multiple PVC for PD and TiKV ([#3820](https://github.com/pingcap/tidb-operator/pull/3820) [#3816](https://github.com/pingcap/tidb-operator/pull/3816), [@dragonly](https://github.com/dragonly))
