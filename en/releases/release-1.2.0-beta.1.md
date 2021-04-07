---
title: TiDB Operator 1.2.0-beta.1 Release Notes
---

# TiDB Operator 1.2.0-beta.1 Release Notes

## Changes

- Fix PVC resize for TiDB. ([#3891](https://github.com/pingcap/tidb-operator/pull/3891), [@dragonly](https://github.com/dragonly))
- Add retry for DNS lookup failure exception in TiDBInitializer. ([#3884](https://github.com/pingcap/tidb-operator/pull/3884), [@handlerww](https://github.com/handlerww))
- Fix the issue that multiple PVC is treated wrong in PVC resizer. ([#3858](https://github.com/pingcap/tidb-operator/pull/3858), [@dragonly](https://github.com/dragonly))
- TidbMonitor add additional volume and volumeMount configurations. ([#3855](https://github.com/pingcap/tidb-operator/pull/3855), [@mikechengwei](https://github.com/mikechengwei))
- Fix the issue that when TidbCluster's `.spec.tidb` is unset. ([#3852](https://github.com/pingcap/tidb-operator/pull/3852), [@dragonly](https://github.com/dragonly))
- Support setting customized envs for backup and restore jobs ([#3833](https://github.com/pingcap/tidb-operator/pull/3833), [@dragonly](https://github.com/dragonly))
- Support affinity and tolerations in backup/restore jobs. ([#3835](https://github.com/pingcap/tidb-operator/pull/3835), [@dragonly](https://github.com/dragonly))
- Fix `UnjoinedMembers` in PD and DM cluster status. ([#3836](https://github.com/pingcap/tidb-operator/pull/3836), [@dragonly](https://github.com/dragonly))
- Fix support for multiple PVC for PD. ([#3820](https://github.com/pingcap/tidb-operator/pull/3820), [@dragonly](https://github.com/dragonly))
- Fix support for multiple PVC for TiKV. ([#3816](https://github.com/pingcap/tidb-operator/pull/3816), [@dragonly](https://github.com/dragonly))
- The resources in the tidb-operator chart use the new service account when `appendReleaseSuffix` is set to `true` ([#3819](https://github.com/pingcap/tidb-operator/pull/3819), [@DanielZhangQD](https://github.com/DanielZhangQD))
- Fix tidbmonitor externallabels unrecognized environment variables bug. ([#3785](https://github.com/pingcap/tidb-operator/pull/3785), [@mikechengwei](https://github.com/mikechengwei))
- Support setting customized store labels according to the node labels ([#3784](https://github.com/pingcap/tidb-operator/pull/3784), [@L3T](https://github.com/L3T))
- Add TiFlash rolling upgrade logic to avoid all TiFlash stores unavailable. ([#3789](https://github.com/pingcap/tidb-operator/pull/3789), [@handlerww](https://github.com/handlerww))
- Retrieve the region leader count from TiKV Pod directly instead of from PD to get the accurate count ([#3801](https://github.com/pingcap/tidb-operator/pull/3801), [@DanielZhangQD](https://github.com/DanielZhangQD))
- Support user configuration about LeaderLease ([#3794](https://github.com/pingcap/tidb-operator/pull/3794), [@july2993](https://github.com/july2993))
- Print RocksDB and Raft log to stdout to support them be collected and queried in the grafana ([#3768](https://github.com/pingcap/tidb-operator/pull/3768), [@baurine](https://github.com/baurine))
- Optimze thanos example yaml files. ([#3726](https://github.com/pingcap/tidb-operator/pull/3726), [@mikechengwei](https://github.com/mikechengwei))
- Add `tidb_cluster` label for the scrape jobs in TidbMonitor to support multiple clusters monitoring ([#3750](https://github.com/pingcap/tidb-operator/pull/3750), [@mikechengwei](https://github.com/mikechengwei))
- Support customizing the storage config for TiDB slow log ([#3731](https://github.com/pingcap/tidb-operator/pull/3731), [@BinChenn](https://github.com/BinChenn))
- Delete evict leader scheduler after TiKV Pod is recreated during upgrade ([#3724](https://github.com/pingcap/tidb-operator/pull/3724), [@handlerww](https://github.com/handlerww))
- `NONE` ([#3738](https://github.com/pingcap/tidb-operator/pull/3738), [@CaitinChen](https://github.com/CaitinChen))
- TidbMonitor support  `remotewrite` configuration ([#3679](https://github.com/pingcap/tidb-operator/pull/3679), [@mikechengwei](https://github.com/mikechengwei))
- Fix the issue that the status of backup or restore is not `Failed` after the pod has been evicted or killed. ([#3696](https://github.com/pingcap/tidb-operator/pull/3696), [@csuzhangxc](https://github.com/csuzhangxc))
- Fix the bug that when upgrade TidbCluster with `delete-slots` annotations, the Pods whose ordinal bigger than `replicaton numbers - 1` will be terminated directly without any pre-delete operations such as evicting leaders. ([#3702](https://github.com/pingcap/tidb-operator/pull/3702), [@cvvz](https://github.com/cvvz))
- Support configuring init containers for components in TiDB cluster ([#3713](https://github.com/pingcap/tidb-operator/pull/3713), [@handlerww](https://github.com/handlerww))
- Fix the issue that backup and restore jobs with BR fail without configuring `spec.from` or `spec.to` ([#3707](https://github.com/pingcap/tidb-operator/pull/3707), [@BinChenn](https://github.com/BinChenn))
- Fix the issue that when TiKV cluster is not bootstrapped, the following updates of TiKV component are not able to be synced. ([#3694](https://github.com/pingcap/tidb-operator/pull/3694), [@cvvz](https://github.com/cvvz))
