---
title: TiDB Operator 1.6.5 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.5.
---

# TiDB Operator 1.6.5 Release Notes

Release date: February 6, 2026

TiDB Operator version: 1.6.5

## New features

- Support configuring `VolumeAttributesClass` for TiDBCluster components, which enables dynamic management of volume attributes such as IOPS and throughput ([#6568](https://github.com/pingcap/tidb-operator/pull/6568), [@WangLe1321](https://github.com/WangLe1321))

## Improvements

- Change the shell interpreter for backup-related scripts from `sh` to `bash` to improve script compatibility and support Bash-specific syntax ([#6618](https://github.com/pingcap/tidb-operator/pull/6618), [@liubog2008](https://github.com/liubog2008))

## Bug fixes

- Fix the issue that the controller retries indefinitely when a log backup task cannot be found in etcd. The controller now updates the `Backup` CR status to `Failed` in this case ([#6630](https://github.com/pingcap/tidb-operator/pull/6630), [@RidRisR](https://github.com/RidRisR))
- Fix the compatibility issue with certain Kubernetes versions (such as v1.33) that causes TiDB Operator to repeatedly attempt creating existing resources during each sync cycle ([#6653](https://github.com/pingcap/tidb-operator/pull/6653), [@cicada-lewis](https://github.com/cicada-lewis))
