---
title: TiDB Operator 1.5.0 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.5.0.
---

# TiDB Operator 1.5.0 Release Notes

Release date: August 4, 2023

TiDB Operator version: 1.5.0

## Rolling update changes

If TiFlash is deployed in a TiDB cluster that is v7.1.0 or later, the TiFlash component will be rolling updated after TiDB Operator is upgraded to v1.5.0 due to [#5075](https://github.com/pingcap/tidb-operator/pull/5075).

## New features

- Add the BR Federation Manager component to orchestrate `Backup` and `Restore` custom resources (CR) across multiple Kubernetes clusters ([#4996](https://github.com/pingcap/tidb-operator/pull/4996), [@csuzhangxc](https://github.com/csuzhangxc))
- Support using the `VolumeBackup` CR to back up a TiDB cluster deployed across multiple Kubernetes clusters based on EBS snapshots ([#5013](https://github.com/pingcap/tidb-operator/pull/5013), [@WangLe1321](https://github.com/WangLe1321))
- Support using the `VolumeRestore` CR to restore a TiDB cluster deployed across multiple Kubernetes clusters based on EBS snapshots ([#5039](https://github.com/pingcap/tidb-operator/pull/5039), [@WangLe1321](https://github.com/WangLe1321))
- Support using the `VolumeBackupSchedule` CR to automatically back up a TiDB cluster deployed across multiple Kubernetes clusters based on EBS snapshots ([#5036](https://github.com/pingcap/tidb-operator/pull/5036), [@BornChanger](https://github.com/BornChanger))
- Support backing up CRs related to `TidbCluster` when backing up a TiDB cluster deployed across multiple Kubernetes based on EBS snapshots ([#5207](https://github.com/pingcap/tidb-operator/pull/5207), [@WangLe1321](https://github.com/WangLe1321))

## Improvements

- Add the `startUpScriptVersion` field for DM master to specify the version of the startup script ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))
- Support `spec.preferIPv6` for DmCluster, TidbDashboard, TidbMonitor, and TidbNGMonitoring ([#4977](https://github.com/pingcap/tidb-operator/pull/4977), [@KanShiori](https://github.com/KanShiori))
- Support setting expiration time for TiKV leader eviction and PD leader transfer ([#4997](https://github.com/pingcap/tidb-operator/pull/4997), [@Tema](https://github.com/Tema))
- Support setting toleration for `TidbInitializer` ([#5047](https://github.com/pingcap/tidb-operator/pull/5047), [@csuzhangxc](https://github.com/csuzhangxc))
- Support configuring the timeout for PD start ([#5071](https://github.com/pingcap/tidb-operator/pull/5071), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- Skip evicting leaders for TiKV when changing PVC size to avoid leader eviction blocked caused by low disk space ([#5101](https://github.com/pingcap/tidb-operator/pull/5101), [@csuzhangxc](https://github.com/csuzhangxc))
- Support updating annotations and labels in services for PD, TiKV, TiFlash, TiProxy, DM-master, and DM-worker ([#4973](https://github.com/pingcap/tidb-operator/pull/4973), [@wxiaomou](https://github.com/wxiaomou))
- Enable volume resizing by default for PV expansion ([#5167](https://github.com/pingcap/tidb-operator/pull/5167), [@liubog2008](https://github.com/liubog2008))

## Bug fixes

- Fix the quorum loss issue during TiKV upgrade due to some TiKV stores going down ([#4979](https://github.com/pingcap/tidb-operator/pull/4979), [@Tema](https://github.com/Tema))
- Fix the quorum loss issue during PD upgrade due to some members going down ([#4995](https://github.com/pingcap/tidb-operator/pull/4995), [@Tema](https://github.com/Tema))
- Fix the issue that TiDB Operator panics when no Kubernetes cluster-level permission is configured ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- Fix the issue that TiDB Operator might panic when `AdditionalVolumeMounts` is set for the `TidbCluster` CR ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- Fix the issue that `baseImage` for the `TidbDashboard` CR is parsed incorrectly when custom image registry is used ([#5014](https://github.com/pingcap/tidb-operator/pull/5014), [@linkinghack](https://github.com/linkinghack))
