---
title: TiDB Operator 1.6.1 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.1.
---

# TiDB Operator 1.6.1 Release Notes

Release date: December 25, 2024

TiDB Operator version: 1.6.1

## New features

- Support authentication for backup and restore operations using Azure Blob Storage Shared Access Signature (SAS) tokens ([#5720](https://github.com/pingcap/tidb-operator/pull/5720), [@tennix](https://github.com/tennix))
- The VolumeReplace feature supports the TiFlash component ([#5685](https://github.com/pingcap/tidb-operator/pull/5685), [@rajsuvariya](https://github.com/rajsuvariya))
- Add a more straightforward interface for Log Backup that supports pausing and resuming backup tasks ([#5710](https://github.com/pingcap/tidb-operator/pull/5710), [@RidRisR](https://github.com/RidRisR))
- Support deleting Log Backup tasks by removing their associated Backup custom resource (CR) ([#5754](https://github.com/pingcap/tidb-operator/pull/5754), [@RidRisR](https://github.com/RidRisR))
- The VolumeModify feature supports modifying Azure Premium SSD v2 disks. To use this feature, you need to grant the tidb-controller-manager permission to operate Azure disk through a node or Pod. ([#5958](https://github.com/pingcap/tidb-operator/pull/5958), [@handlerww](https://github.com/handlerww))

## Improvements

- The VolumeModify feature no longer performs leader eviction for TiKV, reducing modification time ([#5826](https://github.com/pingcap/tidb-operator/pull/5826), [@csuzhangxc](https://github.com/csuzhangxc))
- Support specifying the minimum wait time during PD Pod rolling updates by using annotations ([#5827](https://github.com/pingcap/tidb-operator/pull/5827), [@csuzhangxc](https://github.com/csuzhangxc))
- The VolumeReplace feature supports customizing the number of spare replicas for PD and TiKV ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- The VolumeReplace feature can be enabled for specific TiDB clusters ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- Optimize the primary transfer logic of the PD microservice to reduce the number of primary transfer operations during component updates ([#5643](https://github.com/pingcap/tidb-operator/pull/5643), [@HuSharp](https://github.com/HuSharp))
- Support setting `LoadBalancerClass` for the TiDB service ([#5964](https://github.com/pingcap/tidb-operator/pull/5964), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug fixes

- Fix the issue that EBS snapshot restore incorrectly succeeds when no TiKV instances are configured or TiKV replica is set to 0 ([#5659](https://github.com/pingcap/tidb-operator/pull/5659), [@BornChanger](https://github.com/BornChanger))
- Fix the issue that ClusterRole and ClusterRoleBinding resources are not properly cleaned up when you delete a `TidbMonitor` that monitors multiple TiDB clusters across namespaces ([#5956](https://github.com/pingcap/tidb-operator/pull/5956), [@csuzhangxc](https://github.com/csuzhangxc))
- Fix a type mismatch issue in the `.spec.prometheus.remoteWrite.remoteTimeout` field of `TidbMonitor`  ([#5734](https://github.com/pingcap/tidb-operator/pull/5734), [@IMMORTALxJO](https://github.com/IMMORTALxJO))
