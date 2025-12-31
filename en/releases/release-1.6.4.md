---
title: TiDB Operator 1.6.4 Release Notes
summary: Learn about new features in TiDB Operator 1.6.4.
---

# TiDB Operator 1.6.4 Release Notes

Release date: December 2, 2025

TiDB Operator version: 1.6.4

## New features

- Add a periodic status synchronization mechanism for log backups. If the status of TiDB Operator is inconsistent with the actual status of the underlying backup task in the TiDB cluster, TiDB Operator updates the `logBackup` CR status and attempts to synchronize with the underlying task during subsequent reconcile processes until the status reaches the expected state. ([#6147](https://github.com/pingcap/tidb-operator/pull/6147), [@RidRisR](https://github.com/RidRisR))
