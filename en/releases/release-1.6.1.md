---
title: TiDB Operator 1.6.1 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.1.
---

# TiDB Operator 1.6.1 Release Notes

Release date: Dec 6, 2024

TiDB Operator version: 1.6.1

## New features

- Support Backup & Restore using Azure blob storage SAS token authentication ([#5720](https://github.com/pingcap/tidb-operator/pull/5720), [@tennix](https://github.com/tennix))
- VolumeReplace feature supports TiFlash ([#5685](https://github.com/pingcap/tidb-operator/pull/5685), [@rajsuvariya](https://github.com/rajsuvariya))

## Improvements

- VolumeModify feature no longer performs evict leader operations for TiKV to shorten the modification time ([#5826](https://github.com/pingcap/tidb-operator/pull/5826), [@csuzhangxc](https://github.com/csuzhangxc))
- Support specifying the minimum wait time during the rolling update of PD Pods through annotations ([#5827](https://github.com/pingcap/tidb-operator/pull/5827), [@csuzhangxc](https://github.com/csuzhangxc))
- The VolumeReplace feature supports customizing the number of spare replicas for PD and TiKV ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- The VolumeReplace feature can be enabled for specific TiDB clusters ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- Optimized the PD microservice transfer primary logic to reduce the number of transfer primary operations during component updates ([#5643](https://github.com/pingcap/tidb-operator/pull/5643), [@HuSharp](https://github.com/HuSharp))

## Bug fixes

- Fix the issue that EBS snapshot restore incorrectly succeeds when no TiKV instances are configured or TiKV replica is set to 0 ([#5659](https://github.com/pingcap/tidb-operator/pull/5659), [@BornChanger](https://github.com/BornChanger))
- Fix the issue that the ClusterRole/ClusterRoleBinding corresponding to TidbMonitor monitoring multiple TiDB clusters across namespaces was not properly cleaned up after deletion ([#5956](https://github.com/pingcap/tidb-operator/pull/5956), [@csuzhangxc](https://github.com/csuzhangxc))
