---
title: TiDB Operator 1.5.1 Release Notes
---

# TiDB Operator 1.5.1 Release Notes

Release date: October 20, 2023

TiDB Operator version: 1.5.1

## New features

- Support replacing volumes for PD, TiKV and TiDB ([#5150](https://github.com/pingcap/tidb-operator/pull/5150), [@anish-db](https://github.com/anish-db))

## Improvements

## Bug fixes

- Fix errors from PVC modifier when a manual TiKV eviction is requested ([#5302](https://github.com/pingcap/tidb-operator/pull/5302), [@anish-db](https://github.com/anish-db))
- Fix a deadlock in TiDB Operator casued by the TiKV eviction when a volume replacement is ongoing ([#5301](https://github.com/pingcap/tidb-operator/pull/5301), [@anish-db](https://github.com/anish-db))
