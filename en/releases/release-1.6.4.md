---
title: TiDB Operator 1.6.4 Release Notes
summary: Learn about new features in TiDB Operator 1.6.2.
---

# TiDB Operator 1.6.3 Release Notes

Release date: Oct 18, 2025

TiDB Operator version: 1.6.4

## New features

- Add a periodical sync to kernel. If the operator state is inconsistent with the kernel, operator will change the status of logBackup CR, and try to sync with kernel ( eventually make kernel reach the desired state) in the future reconcile. ([#6033](https://github.com/pingcap/tidb-operator/pull/6147), [@RidRisR](https://github.com/RidRisR))
