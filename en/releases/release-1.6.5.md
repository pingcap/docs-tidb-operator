---
title: TiDB Operator 1.6.5 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.5.
---

# TiDB Operator 1.6.5 Release Notes

Release date: January 28, 2026

TiDB Operator version: 1.6.5

## New features

- Support `VolumeAttributesClass` for TiDBCluster components to dynamically manage volume attributes such as IOPS and throughput ([#6568](https://github.com/pingcap/tidb-operator/pull/6568), [@WangLe1321](https://github.com/WangLe1321))

## Improvements

- Change the shell interpreter of backup-related scripts from `sh` to `bash` for better compatibility with bash-specific features ([#6618](https://github.com/pingcap/tidb-operator/pull/6618), [@liubog2008](https://github.com/liubog2008))

## Bug fixes

- Fix the issue that the controller retries indefinitely when a log backup task is not found in etcd by updating the Backup CR status to `Failed` ([#6630](https://github.com/pingcap/tidb-operator/pull/6630), [@RidRisR](https://github.com/RidRisR))
- Fix the compatibility issue with some Kubernetes versions (e.g. v1.33) where the operator incorrectly attempts to recreate existing resources in every sync cycle ([#6653](https://github.com/pingcap/tidb-operator/pull/6653), [@cicada-lewis](https://github.com/cicada-lewis))
