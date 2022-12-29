---
title: TiDB Operator 1.4.0 Release Notes
---

# TiDB Operator 1.4.0 Release Notes

Release date: December 29, 2022

TiDB Operator version: 1.4.0

## New features

- Support managing [TiDB Dashboard](https://github.com/pingcap/tidb-dashboard) in a separate `TidbDashboard` CRD ([#4787](https://github.com/pingcap/tidb-operator/pull/4787), [@SabaPing](https://github.com/SabaPing))
- Support configuring Liveness Probe for TiKV and PD ([#4763](https://github.com/pingcap/tidb-operator/pull/4763), [@mikechengwei](https://github.com/mikechengwei))
- Support backup and restore based on Amazon EBS volume-snapshot ([#4698](https://github.com/pingcap/tidb-operator/pull/4698)，[@gozssky](https://github.com/gozssky)

## Improvements

- Support configuring `.spec.preferIPv6: true` for compatibility with IPv6 network environments ([#4811](https://github.com/pingcap/tidb-operator/pull/4811)，[@KanShiori](https://github.com/KanShiori)

## Bug fixes

- Fix the issue that the backup based on EBS snapshot cannot be restored to a different namespace ([#4795](https://github.com/pingcap/tidb-operator/pull/4795), [@fengou1](https://github.com/fengou1))
- Fix the issue that when the log backup stops occupying the Complete state, the caller mistakenly believes that the log backup CR has been completed, so that the log backup cannot be truncated ([#4810](https://github.com/pingcap/tidb-operator/pull/4810), [@WizardXiao](https://github.com/WizardXiao))
