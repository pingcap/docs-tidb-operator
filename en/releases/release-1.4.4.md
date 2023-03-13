---
title: TiDB Operator 1.4.4 Release Notes
---

# TiDB Operator 1.4.4 Release Notes

Release date: March 13, 2023

TiDB Operator version: 1.4.4

## New features

- Support using volume-snapshot backup and restore on a TiDB cluster with TiFlash ([#4812](https://github.com/pingcap/tidb-operator/pull/4812), [@fengou1](https://github.com/fengou1))

- Show an accurate backup size in the volume-snapshot backup by calculating the backup size from snapshot storage usage ([#4819](https://github.com/pingcap/tidb-operator/pull/4819), [@fengou1](https://github.com/fengou1))

- Support retries for snapshot backups in case of unexpected failures caused by Kubernetes job or pod issues ([#4895](https://github.com/pingcap/tidb-operator/pull/4895), [@WizardXiao](https://github.com/WizardXiao))

- Support integrated management of log backup and snapshot backup in the `BackupSchedule` CR ([#4904](https://github.com/pingcap/tidb-operator/pull/4904), [@WizardXiao](https://github.com/WizardXiao))

## Bug fixes

- Fix the issue that sync fails when using a custom build of TiDB with image version which is not in semantic version format ([#4920](https://github.com/pingcap/tidb-operator/pull/4920), [@sunxiaoguang](https://github.com/sunxiaoguang))

- Fix the issue that TiDB Operator cannot restore the volume-snapshot backup data for scale-in clusters by ensuring sequential PVC names ([#4888](https://github.com/pingcap/tidb-operator/pull/4888), [@WangLe1321](https://github.com/WangLe1321))

- Fix the issue that volume-snapshot backup might lead to a panic when there is no block change between two snapshots ([#4922](https://github.com/pingcap/tidb-operator/pull/4922), [@fengou1](https://github.com/fengou1))

- Fix the potential issue of volume-snapshot failure during the final stage of restore by adding a new check for encryption ([#4914](https://github.com/pingcap/tidb-operator/pull/4914), [@fengou1](https://github.com/fengou1))