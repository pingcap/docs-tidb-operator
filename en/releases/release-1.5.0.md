---
title: TiDB Operator 1.5.0 Release Notes
---

# TiDB Operator 1.5.0 Release Notes

Release date: August 4, 2023

TiDB Operator version: 1.5.0

## Rolling Update Changes

- If TiFlash is deployed in a v7.1.0+ cluster, the TiFlash component will be rolling updated after upgrading TiDB Operator to v1.5.0 due to [#5075](https://github.com/pingcap/tidb-operator/pull/5075).

## New Feature

- Add a component of BR Federation Manager to support orchestrate `Backup` and `Restore` CR across multiple Kubernetes ([#4996](https://github.com/pingcap/tidb-operator/pull/4996), [@csuzhangxc](https://github.com/csuzhangxc))
- Support backup TiDB cluster deployed across multiple Kubernetes base on EBS snapshot using `VolumeBackup` CR ([#5013](https://github.com/pingcap/tidb-operator/pull/5013), [@WangLe1321](https://github.com/WangLe1321))
- Support restore TiDB cluster deployed across multiple Kubernetes base on EBS snapshot using `VolumeRestore` CR ([#5039](https://github.com/pingcap/tidb-operator/pull/5039), [@WangLe1321](https://github.com/WangLe1321))
- Support automatically backup TiDB cluster deployed across multiple Kubernetes base on EBS snapshot using `VolumeBackupSchedule` CR ([#5036](https://github.com/pingcap/tidb-operator/pull/5036), [@BornChanger](https://github.com/BornChanger))
- Support backup manifests related to `TidbCluster` when backup TiDB cluster deployed across multiple Kubernetes base on EBS snapshot ([#5207](https://github.com/pingcap/tidb-operator/pull/5207), [@WangLe1321](https://github.com/WangLe1321))

## Improvements

- Introduce `startUpScriptVersion` field for DM master to specify startup script version ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))
- Add `spec.preferIPv6` support for DmCluster, TidbDashboard, TidbMonitor and TidbNGMonitoring ([#4977](https://github.com/pingcap/tidb-operator/pull/4977), [@KanShiori](https://github.com/KanShiori))
- Support setting expiration time for TiKV leader eviction and PD leader transfer ([#4997](https://github.com/pingcap/tidb-operator/pull/4997), [@Tema](https://github.com/Tema))
- Add tolerations support for TidbInitializer ([#5047](https://github.com/pingcap/tidb-operator/pull/5047), [@csuzhangxc](https://github.com/csuzhangxc))
- Support configuring PD start timeout ([#5071](https://github.com/pingcap/tidb-operator/pull/5071), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- Skip evicting leader for TiKV when changing PVC size ([#5101](https://github.com/pingcap/tidb-operator/pull/5101), [@csuzhangxc](https://github.com/csuzhangxc))
- Support updating annotations and labels in services for PD, TiKV, TiFlash, TiProxy, DM-master and DM-worker ([#4973](https://github.com/pingcap/tidb-operator/pull/4973), [@wxiaomou](https://github.com/wxiaomou))
- Enable volume resizing by default ([#5167](https://github.com/pingcap/tidb-operator/pull/5167), [@liubog2008](https://github.com/liubog2008))

## Bug fixes

- Fix the issue that TiKV briefly looses quorum when starting upgrade while some of TiKV stores are down ([#4979](https://github.com/pingcap/tidb-operator/pull/4979), [@Tema](https://github.com/Tema))
- Fix the issue that PD briefly looses quorum when starting upgrade while some of PD members are down ([#4995](https://github.com/pingcap/tidb-operator/pull/4995), [@Tema](https://github.com/Tema))
- Fix the issue that TiDB Operator panics if no Kubernetes cluster-level permission is configured ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- Fix the issue that TiDB Operator might panic if `AdditionalVolumeMounts` is set for TidbCluster ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- Fix the issue that `baseImage` for TidbDashboard parsed wrongly when using custom image registry ([#5014](https://github.com/pingcap/tidb-operator/pull/5014), [@linkinghack](https://github.com/linkinghack))
