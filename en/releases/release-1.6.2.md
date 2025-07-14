---
title: TiDB Operator 1.6.2 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.2.
---

# TiDB Operator 1.6.2 Release Notes

Release date: July 14, 2025

TiDB Operator version: 1.6.2

## New features

- Support compressing backup logs and configuring scheduled tasks to optimize storage usage ([#6033](https://github.com/pingcap/tidb-operator/pull/6033), [@RidRisR](https://github.com/RidRisR))
-Support the new `abort restore` command to clean up restore related meta data ([#6288](https://github.com/pingcap/tidb-operator/pull/6288), [@RidRisR](https://github.com/RidRisR))

## Improvements

- Support evicting TiKV leaders before deleting a store when scaling in TiKV nodes ([#6239](https://github.com/pingcap/tidb-operator/pull/6239), [@liubog2008](https://github.com/liubog2008))
- When upgrading PD, TiDB Operator uses the new `pd/api/v2/ready` API to check member readiness ([#6243](https://github.com/pingcap/tidb-operator/pull/6243), [@csuzhangxc](https://github.com/csuzhangxc))
- Before gracefully restarting TiKV, TiDB Operator flushes backup log files to disk to prevent data loss ([#6057](https://github.com/pingcap/tidb-operator/pull/6057), [@YuJuncen](https://github.com/YuJuncen))
- Support automatic retries of failed restore tasks based on policies ([#6092](https://github.com/pingcap/tidb-operator/pull/6092), [@RidRisR](https://github.com/RidRisR))
- Make the `--pitrRestoredTs` parameter optional in the restore custom resource (CR) ([#6135](https://github.com/pingcap/tidb-operator/pull/6135), [@RidRisR](https://github.com/RidRisR))
- Support namespace-level log backup tracking ([#6160](https://github.com/pingcap/tidb-operator/pull/6160), [@WangLe1321](https://github.com/WangLe1321))
- Support specifying forced path-style URLs for FIPS backups ([#6250](https://github.com/pingcap/tidb-operator/pull/6250), [@3pointer](https://github.com/3pointer))
- Support using a custom S3 endpoint in the backup manager ([#6268](https://github.com/pingcap/tidb-operator/pull/6268), [@3pointer](https://github.com/3pointer))

## Bug fixes

- Fix the issue that the TidbCluster CR is incorrectly marked as `Ready` when some Tiproxy Pods are unhealthy ([#6151](https://github.com/pingcap/tidb-operator/pull/6151), [@ideascf](https://github.com/ideascf))
- Fix the issue that EBS volume snapshot backup tasks cannot exit normally due to invalid TC format([#6087](https://github.com/pingcap/tidb-operator/pull/6087), [@BornChanger](https://github.com/BornChanger))
- Fix the issue that incorrect data is restored during PITR due to the `gc.ratio-threshold` parameter being reset after a TiKV restart ([#6267](https://github.com/pingcap/tidb-operator/pull/6267), [@YuJuncen](https://github.com/YuJuncen))
