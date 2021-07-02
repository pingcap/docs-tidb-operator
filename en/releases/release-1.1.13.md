---
title: TiDB Operator 1.1.13 Release Notes
---

# TiDB Operator 1.1.13 Release Notes

Release date: July 2, 2021

TiDB Operator version: 1.1.13

## Improvements

- Support using the TiKV version as the tag for BR `toolImage` if no tag is contained ([#4048](https://github.com/pingcap/tidb-operator/pull/4048), [@KanShiori](https://github.com/KanShiori))
- Support handling PVC during scaling of TiDB ([#4033](https://github.com/pingcap/tidb-operator/pull/4033), [@csuzhangxc](https://github.com/csuzhangxc))
- Masks the backup password in logging ([#3979](https://github.com/pingcap/tidb-operator/pull/3979), [@dveeden](https://github.com/dveeden))

## Bug Fixes

- Fix the issue that TiDB Operator may panic when heterogeneous clusters are deployed ([#4054](https://github.com/pingcap/tidb-operator/pull/4054), [@KanShiori](https://github.com/KanShiori))
- Fix the issue that TiDB instances still exist in TiDB Dashboard after scaled in ([#3929](https://github.com/pingcap/tidb-operator/pull/3929), [@july2993](https://github.com/july2993))
