---
title: What's New in TiDB Operator 1.5
summary: Learn about new features in TiDB Operator 1.5.0.
---

# What's New in TiDB Operator 1.5

TiDB Operator 1.5 introduces the following key features, which helps you manage TiDB clusters and the tools more easily in terms of extensibility and usability.

## Compatibility changes

To use the `PreferDualStack` feature (enabled with `spec.preferIPv6: true`) introduced in [#4959](https://github.com/pingcap/tidb-operator/pull/4959), Kubernetes version >= v1.20 is required.

## Rolling update changes

If TiFlash is deployed in a TiDB cluster that is v7.1.0 or later, the TiFlash component will be rolling updated after TiDB Operator is upgraded to v1.5.0 due to [#5075](https://github.com/pingcap/tidb-operator/pull/5075).

## Extensibility

- Support specifying an initialization SQL file to be executed during the first bootstrap of TiDB with the `bootstrapSQLConfigMapName` field.
- Support setting `PreferDualStack` for all Service's `ipFamilyPolicy` with `spec.preferIPv6: true`.
- Support managing TiCDC and TiProxy with [Advanced StatefulSet](advanced-statefulset.md).
- Add the BR Federation Manager component to support the backup and restore of a TiDB cluster deployed across multiple Kubernetes clusters based on EBS snapshots.

## Usability

- Support using the `tidb.pingcap.com/pd-transfer-leader` annotation to restart PD Pods gracefully.
- Support using the `tidb.pingcap.com/tidb-graceful-shutdown` annotation to restart TiDB Pods gracefully.
- Allow users to define a strategy to restart failed backup jobs, enhancing backup stability.
- Add metrics for the reconciler and worker queue to improve observability.
- Add metrics for counting errors that occur during the reconciliation to improve observability.
