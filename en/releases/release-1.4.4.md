---
title: TiDB Operator 1.4.4 Release Notes
---

# TiDB Operator 1.4.4 Release Notes

Release date: March 13, 2023

TiDB Operator version: 1.4.4

## New features

- Support use volume-snapshot backup and restore when cluster has TiFlash ([#4812](https://github.com/pingcap/tidb-operator/pull/4812), [@fengou1](https://github.com/fengou1))

- Support show a accurate backup size in volume-snapshot backup by calculate the backup size from snapshot storage usage ([#4819](https://github.com/pingcap/tidb-operator/pull/4819), [@fengou1](https://github.com/fengou1))

- Support retry snapshot backup when its job or pod unexpected failure caused by kubernetes ([#4895](https://github.com/pingcap/tidb-operator/pull/4895), [@WizardXiao](https://github.com/WizardXiao))

- Support integrated management log backup and snapshot backup in backup schedule ([#4904](https://github.com/pingcap/tidb-operator/pull/4904), [@WizardXiao](https://github.com/WizardXiao))

## Bug fixes

- Fix the issue that sync failed when using custom build of TiDB with image version which is not in semantic version format ([#4920](https://github.com/pingcap/tidb-operator/pull/4920), [@sunxiaoguang](https://github.com/sunxiaoguang))

- Fix the issue that volume-snapshot can not restore when backup a scale-in cluster by ensuring pvc names sequential ([#4888](https://github.com/pingcap/tidb-operator/pull/4888), [@WangLe1321](https://github.com/WangLe1321))

- Fix the issue that volume-snapshot may lead to a panic when there is no block change between two snapshot ([#4922](https://github.com/pingcap/tidb-operator/pull/4922), [@fengou1](https://github.com/fengou1))

- Fix the issue that volume-snapshot may failed at the end of restore stage by add a new check for encryption during the volume snapshot restore ([#4914](https://github.com/pingcap/tidb-operator/pull/4914), [@fengou1](https://github.com/fengou1))