---
title: TiDB Operator 1.4.0-beta.1 Release Notes
---

# TiDB Operator 1.4.0-beta.1 Release Notes

Release date: October 26, 2022

TiDB Operator version: 1.4.0-beta.1

## New Feature

- TiDB Operator supports AWS EBS snapshot Backup and Restore ([#4698](https://github.com/pingcap/tidb-operator/pull/4698), [@gozssky](https://github.com/gozssky))

## Bug fixes

- Fix the issue that the log backup checkpoint ts will not be updated when the tidb operator restarts. ([#4746](https://github.com/pingcap/tidb-operator/pull/4746), [@WizardXiao](https://github.com/WizardXiao))

- Fix the issue that log backup checkpoint ts will not be updated when tidb cluster supports TLS. ([#4716](https://github.com/pingcap/tidb-operator/pull/4716), [@WizardXiao](https://github.com/WizardXiao))
