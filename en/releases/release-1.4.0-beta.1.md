---
title: TiDB Operator 1.4.0-beta.1 Release Notes
summary: TiDB Operator 1.4.0-beta.1 was released on October 27, 2022. The new feature includes support for snapshot backup and restore based on Amazon EBS, with benefits such as reducing the impact of backup on QPS to less than 5% and shortening the backup and restore time. Bug fixes include updating the log backup checkpoint ts after TiDB Operator restarts and when TLS is enabled for the TiDB cluster.
---

# TiDB Operator 1.4.0-beta.1 Release Notes

Release date: October 27, 2022

TiDB Operator version: 1.4.0-beta.1

## New Feature

- TiDB Operator supports snapshot backup and restore based on Amazon EBS (experimental) ([#4698](https://github.com/pingcap/tidb-operator/pull/4698), [@gozssky](https://github.com/gozssky)). This feature has the following benefits:

    - Reduce the impact of backup on QPS to less than 5%
    - Shorten the backup and restore time

## Bug fixes

- Fix the issue that the log backup checkpoint ts will not be updated after TiDB Operator restarts ([#4746](https://github.com/pingcap/tidb-operator/pull/4746), [@WizardXiao](https://github.com/WizardXiao))

- Fix the issue that log backup checkpoint ts will not be updated when TLS is enabled for the TiDB cluster ([#4716](https://github.com/pingcap/tidb-operator/pull/4716), [@WizardXiao](https://github.com/WizardXiao))
