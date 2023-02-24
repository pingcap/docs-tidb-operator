---
title: TiDB Operator 1.4.3 Release Notes
---

# TiDB Operator 1.4.3 Release Notes

Release date: February 24, 2023

TiDB Operator version: 1.4.3

## Bug fixes

- Fix the issue that the TiFlash metric server does not listen on correct IPv6 addresses when the `preferIPv6` configuration is enabled ([#4850](https://github.com/pingcap/tidb-operator/pull/4889), [@KanShiori](https://github.com/KanShiori))

- Fix the issue that TiDB Operator keeps modifying EBS disks in AWS when the feature gate `VolumeModifying` is enabled and EBS parameters are missing in `StorageClass` ([#4850](https://github.com/pingcap/tidb-operator/pull/4892), [@liubog2008](https://github.com/liubog2008))