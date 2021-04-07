---
title: TiDB Operator 1.2.0-beta.1 Release Notes
---

# TiDB Operator 1.2.0-beta.1 Release Notes

Release date: April 7, 2021

TiDB Operator version: 1.2.0-beta.1

## New Features

- Support setting customized envs for backup and restore jobs ([#3833](https://github.com/pingcap/tidb-operator/pull/3833), [@dragonly](https://github.com/dragonly))
- TidbMonitor add additional volume and volumeMount configurations. ([#3855](https://github.com/pingcap/tidb-operator/pull/3855), [@mikechengwei](https://github.com/mikechengwei))
- Support affinity and tolerations in backup/restore jobs. ([#3835](https://github.com/pingcap/tidb-operator/pull/3835), [@dragonly](https://github.com/dragonly))

## Improvements

- Add retry for DNS lookup failure exception in TiDBInitializer. ([#3884](https://github.com/pingcap/tidb-operator/pull/3884), [@handlerww](https://github.com/handlerww))
- The resources in the tidb-operator chart use the new service account when `appendReleaseSuffix` is set to `true` ([#3819](https://github.com/pingcap/tidb-operator/pull/3819), [@DanielZhangQD](https://github.com/DanielZhangQD))
- Optimze thanos example yaml files. ([#3726](https://github.com/pingcap/tidb-operator/pull/3726), [@mikechengwei](https://github.com/mikechengwei))
- Delete evict leader scheduler after TiKV Pod is recreated during upgrade ([#3724](https://github.com/pingcap/tidb-operator/pull/3724), [@handlerww](https://github.com/handlerww))
- Support multiple PVC for PD. ([#3820](https://github.com/pingcap/tidb-operator/pull/3820), [@dragonly](https://github.com/dragonly))
- Support multiple PVC for TiKV. ([#3816](https://github.com/pingcap/tidb-operator/pull/3816), [@dragonly](https://github.com/dragonly))

## Bug Fixes

- Fix PVC resize for TiDB. ([#3891](https://github.com/pingcap/tidb-operator/pull/3891), [@dragonly](https://github.com/dragonly))
- Fix the issue that multiple PVC is treated wrong in PVC resizer. ([#3858](https://github.com/pingcap/tidb-operator/pull/3858), [@dragonly](https://github.com/dragonly))
- Fix the issue when TidbCluster's `.spec.tidb` is unset. ([#3852](https://github.com/pingcap/tidb-operator/pull/3852), [@dragonly](https://github.com/dragonly))
- Fix `UnjoinedMembers` in PD and DM cluster status. ([#3836](https://github.com/pingcap/tidb-operator/pull/3836), [@dragonly](https://github.com/dragonly))
- Fix tidbmonitor externallabels unrecognized environment variables bug. ([#3785](https://github.com/pingcap/tidb-operator/pull/3785), [@mikechengwei](https://github.com/mikechengwei))
