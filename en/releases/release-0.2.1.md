---
title: TiDB Operator 0.2.1 Release Notes
summary: TiDB Operator 0.2.1 was released on September 20, 2018. This version includes bug fixes for retry on conflict logic, TiDB timezone configuration, failover, and repeated updating of pod and pd/tidb StatefulSet.
---

# TiDB Operator 0.2.1 Release Notes

Release date: September 20, 2018

TiDB Operator version: 0.2.1

## Bug Fixes

- Fix retry on conflict logic ([#87](https://github.com/pingcap/tidb-operator/pull/87))
- Fix TiDB timezone configuration by setting TZ environment variable ([#96](https://github.com/pingcap/tidb-operator/pull/96))
- Fix failover by keeping spec replicas unchanged ([#95](https://github.com/pingcap/tidb-operator/pull/95))
- Fix repeated updating pod and pd/tidb StatefulSet ([#101](https://github.com/pingcap/tidb-operator/pull/101))
