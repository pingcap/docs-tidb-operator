---
title: TiDB Operator 1.2.0 Release Notes
---

# TiDB Operator 1.2.0 Release Notes

Release date: July 29, 2021

TiDB Operator version: 1.2.0

## Rolling update changes

- Upgrading TiDB Operator will cause the recreation of the TidbMonitor Pod due to [#4085](https://github.com/pingcap/tidb-operator/pull/4085)

## New features

- Support setting Prometheus `retentionTime`, which is more fine-grained than `reserveDays`, and only use `retentionTime` if both are configured ([#4085](https://github.com/pingcap/tidb-operator/pull/4085), [@better0332](https://github.com/better0332))
- Support setting `priorityClassName` of `Backup` Job ([#4078](https://github.com/pingcap/tidb-operator/pull/4078), [@mikechengwei](https://github.com/mikechengwei))

## Improvements

- Set the default region leader eviction timeout of TiKV to 1500 min ([#4071](https://github.com/pingcap/tidb-operator/pull/4071), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue that it may fail to parse the URL in `Prometheus.RemoteWrite` in `TiDBMonitor` ([#4087](https://github.com/pingcap/tidb-operator/pull/4087), [@better0332](https://github.com/better0332))
