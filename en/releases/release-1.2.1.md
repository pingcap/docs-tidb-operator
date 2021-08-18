---
title: TiDB Operator 1.2.1 Release Notes
---

# TiDB Operator 1.2.1 Release Notes

Release date: August 18, 2021

TiDB Operator version: 1.2.1

## Rolling update changes

- If you have enabled `hostNetwork` for TiCDC, after upgrading the TiDB Operator, the TiCDC Pod will roll update due to [#4141](https://github.com/pingcap/tidb-operator/pull/4141)

## Improvements

- Support `hostNetwork` for all components in TidbCluster ([#4141](https://github.com/pingcap/tidb-operator/pull/4141), [@DanielZhangQD](https://github.com/DanielZhangQD)
