---
title: TiDB Operator 1.6.2 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.2.
---

# TiDB Operator 1.6.2 Release Notes

Release date: July 4, 2025

TiDB Operator version: 1.6.2

## New features


## Improvements

- Support evicting TiKV leaders before deleting a store when scaling in TiKV ([#6239](https://github.com/pingcap/tidb-operator/pull/6239), [@liubog2008](https://github.com/liubog2008))
- Support checking if PD members are ready with the new PD `ready` API when upgrading PD ([#6243](https://github.com/pingcap/tidb-operator/pull/6243), [@csuzhangxc](https://github.com/csuzhangxc))
- Support force flush backup log before shutdown TiKV ([#6074](https://github.com/pingcap/tidb-operator/pull/6074), [@YuJuncen](https://github.com/YuJuncen))
- Support policy based retry to failed restore task ([#6092](https://github.com/pingcap/tidb-operator/pull/6092), [@RidRisR](https://github.com/RidRisR))
- Support backup log compaction and its scheduler ([#6033](https://github.com/pingcap/tidb-operator/pull/6033), [@RidRisR](https://github.com/RidRisR))
- Make `--pitrRestoredTs` optional in restore CR([#6138](https://github.com/pingcap/tidb-operator/pull/6138), [@RidRisR](https://github.com/RidRisR))
- Support namespace scope log backup tracker ([#6162](https://github.com/pingcap/tidb-operator/pull/6162), [@WangLe1321](https://github.com/WangLe1321))
- Support force path style url for fips backup ([#6256](https://github.com/pingcap/tidb-operator/pull/6256), [@3pointer](https://github.com/3pointer))
- Support custom S3 endpoint for backup manager  ([#6269](https://github.com/pingcap/tidb-operator/pull/6269), [@3pointer](https://github.com/3pointer))

## Bug fixes

- Fix the issue that TidbCluster CR is marked as `Ready` but there are some tiproxy pods are unhealthy ([#6151](https://github.com/pingcap/tidb-operator/pull/6151), [@ideascf](https://github.com/ideascf))
- fix the issue that ebs volume backup stucks when some backup member has invalid tc ([#6104](https://github.com/pingcap/tidb-operator/pull/6104), [@BornChanger](https://github.com/BornChanger))
- fix the issue that `gc.ratio-threshold` is reset when tikv restarts and restore could fall into data loss during pitr restore ([#6283](https://github.com/pingcap/tidb-operator/pull/6283), [@YuJuncen](https://github.com/YuJuncen))
