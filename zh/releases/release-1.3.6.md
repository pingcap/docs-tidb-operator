---
title: TiDB Operator 1.3.6 Release Notes
---

# TiDB Operator 1.3.6 Release Notes

发布日期: 2022 年 7 月 5 日

TiDB Operator 版本：1.3.6

## 优化提升

- 为了减少扩容 PVC 对集群性能的影响，扩容 PVC 时按照 Pod 一个个扩容，并且在扩容 TiKV 的 PVC 前会先驱逐该 TiKV 上的 leader ([#4609](https://github.com/pingcap/tidb-operator/pull/4609), [#4604](https://github.com/pingcap/tidb-operator/pull/4604), [@KanShiori](https://github.com/KanShiori))
