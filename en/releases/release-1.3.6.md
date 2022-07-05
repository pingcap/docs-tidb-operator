---
title: TiDB Operator 1.3.6 Release Notes
---

# TiDB Operator 1.3.6 Release Notes

Release date: July 5, 2022

TiDB Operator version: 1.3.6

## Improvement

- To reduce the impact on cluster performance when PVCs scale-up, scale up PVCs pod by pod and evict TiKV leader before resize PVCs of TiKV ([#4609](https://github.com/pingcap/tidb-operator/pull/4609), [#4604](https://github.com/pingcap/tidb-operator/pull/4604), [@KanShiori](https://github.com/KanShiori))
