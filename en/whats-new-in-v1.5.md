---
title: What's New in TiDB Operator 1.5
---

# What's New in TiDB Operator 1.5

TiDB Operator 1.5 introduces the following key features, which helps you manage TiDB clusters and the tools more easily in terms of extensibility and usability.

## Compatibility changes

When using the `PreferDualStack` feature introduced in [#4959](https://github.com/pingcap/tidb-operator/pull/4959), Kubernetes version >= v1.20 is required.

## Extensibility

- Support specifying an initialization SQL file on TiDB's first bootstrap with the `bootstrapSQLConfigMapName` field.
- Support setting `PreferDualStack` for all Service's `ipFamilyPolicy` with `spec.preferIPv6: true`.
- Support managing TiCDC and TiProxy with Advanced StatefulSet.
- Add a component of BR Federation Manager to support backup/restore TiDB cluster deployed across multiple Kubernetes using EBS snapshot.

## Usability

- Support using the `tidb.pingcap.com/pd-transfer-leader` annotation to restart PD Pod gracefully.
- Support using the `tidb.pingcap.com/tidb-graceful-shutdown` annotation to restart TiDB Pod gracefully.
- Allow users to define a strategy to restart failed backup jobs, enhancing backup stability.
- Add the metrics for the reconciler and worker queue to improve observability.
- Add the metrics for counting errors about the reconciliation to improve observability.
