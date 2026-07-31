---
title: TiDB Operator 1.3.6 Release Notes
summary: TiDB Operator 1.3.6 版本发布日期为 2022 年 7 月 5 日。此版本优化了扩容 PVC 对集群性能的影响，现在扩容 PVC 时按照 Pod 一个个扩容，并且在扩容 TiKV 的 PVC 前会先驱逐该 TiKV 上的 leader。
aliases: ['/zh/tidb-in-kubernetes/dev/release-1.3.6/','/zh/tidb-in-kubernetes/v1.3/release-1.3.6/','/zh/tidb-in-kubernetes/v1.4/release-1.3.6/','/zh/tidb-in-kubernetes/v1.5/release-1.3.6/','/zh/tidb-in-kubernetes/v1.6/release-1.3.6/','/zh/tidb-in-kubernetes/v2.0/release-1.3.6/']
---

# TiDB Operator 1.3.6 Release Notes

发布日期: 2022 年 7 月 5 日

TiDB Operator 版本：1.3.6

## 优化提升

- 为了减少扩容 PVC 对集群性能的影响，扩容 PVC 时按照 Pod 一个个扩容，并且在扩容 TiKV 的 PVC 前会先驱逐该 TiKV 上的 leader ([#4609](https://github.com/pingcap/tidb-operator/pull/4609), [#4604](https://github.com/pingcap/tidb-operator/pull/4604), [@KanShiori](https://github.com/KanShiori))
