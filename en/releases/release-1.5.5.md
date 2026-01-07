---
title: TiDB Operator 1.5.5 Release Notes
summary: Learn about new features and improvements in TiDB Operator 1.5.5.
---

# TiDB Operator 1.5.5 Release Notes

Release date: January 21, 2025

TiDB Operator version: 1.5.5

## New features

- Add a more straightforward interface for Log Backup that supports pausing and resuming backup tasks ([#5710](https://github.com/pingcap/tidb-operator/pull/5710), [@RidRisR](https://github.com/RidRisR))
- Support deleting Log Backup tasks by removing their associated Backup custom resource (CR) ([#5754](https://github.com/pingcap/tidb-operator/pull/5754), [@RidRisR](https://github.com/RidRisR))

## Improvements

- The VolumeModify feature no longer performs leader eviction for TiKV, reducing modification time ([#5826](https://github.com/pingcap/tidb-operator/pull/5826), [@csuzhangxc](https://github.com/csuzhangxc))
- Support specifying the minimum wait time during PD Pod rolling updates by using annotations ([#5827](https://github.com/pingcap/tidb-operator/pull/5827), [@csuzhangxc](https://github.com/csuzhangxc))
