---
title: TiDB Operator 1.3.6 Release Notes
summary: TiDB Operator 1.3.6 was released on July 5, 2022. The improvement in this version includes reducing the impact of PVC scale-up on cluster performance by scaling up PVCs pod by pod and evicting TiKV leader before resizing PVCs of TiKV.
---

# TiDB Operator 1.3.6 Release Notes

Release date: July 5, 2022

TiDB Operator version: 1.3.6

## Improvement

- To reduce the impact of PVC scale-up on cluster performance, scale up PVCs pod by pod and evict TiKV leader before resizing PVCs of TiKV ([#4609](https://github.com/pingcap/tidb-operator/pull/4609), [#4604](https://github.com/pingcap/tidb-operator/pull/4604), [@KanShiori](https://github.com/KanShiori))
