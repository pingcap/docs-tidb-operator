---
title: TiDB Operator 1.6.0 Release Notes
summary: 了解 TiDB Operator 1.6.0 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.0 Release Notes

发布日期: 2024 年 5 月 28 日

TiDB Operator 版本：1.6.0

## 新功能

- 支持为 TiDB 集群各组件的 `topologySpreadConstraints` 设置 `maxSkew`、`minDomains` 与 `nodeAffinityPolicy` ([#5617](https://github.com/pingcap/tidb-operator/pull/5617), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TiDB 组件设置额外的命令行参数 ([#5624](https://github.com/pingcap/tidb-operator/pull/5624), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TidbInitializer 组件设置 `nodeSelector` ([#5594](https://github.com/pingcap/tidb-operator/pull/5594), [@csuzhangxc](https://github.com/csuzhangxc))

## 优化提升

- 支持自动为 TiProxy 设置 location labels ([#5649](https://github.com/pingcap/tidb-operator/pull/5649), [@djshow832](https://github.com/djshow832))
- 支持在滚动重启 TiKV 时，对 evict leader 执行重试 ([#5613](https://github.com/pingcap/tidb-operator/pull/5613), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TiProxy 组件设置 `advertise-addr` 参数 ([#5608](https://github.com/pingcap/tidb-operator/pull/5608), [@djshow832](https://github.com/djshow832))

## Bug 修复

- 修复 `configUpdateStrategy` 设置为 `InPlace` 时，调整组件 Storage Size 可能导致组件重启的问题 ([#5602](https://github.com/pingcap/tidb-operator/pull/5602), [@ideascf](https://github.com/ideascf))
- 修复重建 TiKV StatefulSet 时 TiDB Operator 可能误将 TiKV 状态识别为 `Upgrading` 从而导致非预期的升级的问题 ([#5551](https://github.com/pingcap/tidb-operator/pull/5551), [@ideascf](https://github.com/ideascf))
