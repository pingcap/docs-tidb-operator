---
title: TiDB Operator 1.4.0-beta.3 Release Notes
---

# TiDB Operator 1.4.0-beta.3 Release Notes

Release date: December 2, 2022

TiDB Operator version: 1.4.0-beta.3

## New Feature

- Add experimental support for TiProxy ([#4693](https://github.com/pingcap/tidb-operator/pull/4693)), [@xhebox](https://github.com/xhebox)

- Snapshot backup and restore based on Amazon EBS becomes GA ([#4784](https://github.com/pingcap/tidb-operator/pull/4784), [@fengou1](https://github.com/fengou1)). This feature has the following benefits:

    - Reduce the impact of backup on QPS to less than 5%
    - Shorten the backup and restore time

## Bug fixes

- Fix typo in error messages ([#4773](https://github.com/pingcap/tidb-operator/pull/4773), [@dveeden](https://github.com/dveeden))

- Fix the issue of volume-snapshot backup cleanup failure ([#4783](https://github.com/pingcap/tidb-operator/pull/4783), [@fengou1](https://github.com/fengou1))

- Fix backup failure when the TiDB cluster has massive TiKV nodes (40+) ([#4784](https://github.com/pingcap/tidb-operator/pull/4784), [@fengou1](https://github.com/fengou1))
