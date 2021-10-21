---
title: TiDB Operator 1.2.4 Release Notes
---

# TiDB Operator 1.2.4 Release Notes

Release date: October 21, 2021

TiDB Operator version: 1.2.4

## Rolling update changes

- Upgrading TiDB Operator will cause the recreation of the TiDBMonitor Pod due to [#4180](https://github.com/pingcap/tidb-operator/pull/4180)

## New features

- TidbMonitor support that user can custom prometheus rules mount and reload configuration dynamically ([#4180](https://github.com/pingcap/tidb-operator/pull/4180), [@mikechengwei](https://github.com/mikechengwei))
- TidbMonitor support `enableRules` field. If AlertManager isn't configured, it can add Prometheus rule configuration through setting this field `true` ([#4115](https://github.com/pingcap/tidb-operator/pull/4115), [@mikechengwei](https://github.com/mikechengwei))

## Improvements

- Optimize `TiFlash` rolling upgrade ([#4193](https://github.com/pingcap/tidb-operator/pull/4193), [@KanShiori](https://github.com/KanShiori))
- Support deleting backup data in batches ([#4095](https://github.com/pingcap/tidb-operator/pull/4095), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the security vulnerabilities in the images `tidb-backup-manager` and `tidb-operator` ([#4217](https://github.com/pingcap/tidb-operator/pull/4217), [@KanShiori](https://github.com/KanShiori))
- Fix the issue that backup data maybe remain after deleting running `Backup` ([#4133](https://github.com/pingcap/tidb-operator/pull/4133), [@KanShiori](https://github.com/KanShiori))
