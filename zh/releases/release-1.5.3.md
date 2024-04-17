---
title: TiDB Operator 1.5.3 Release Notes
summary: 了解 TiDB Operator 1.5.3 版本的新功能和 Bug 修复。
---

# TiDB Operator 1.5.3 Release Notes

发布日期：2024 年 4 月 18 日

TiDB Operator 版本：1.5.3

## 新功能

- 支持为 Discovery 组件设置 `livenessProbe` 与 `readinessProbe` ([#5565](https://github.com/pingcap/tidb-operator/pull/5565), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TidbInitializer 组件设置 `nodeSelector` ([#5594](https://github.com/pingcap/tidb-operator/pull/5594), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug 修复

- 修复 `configUpdateStrategy` 设置为 `InPlace` 时，调整组件 Storage Size 可能导致组件重启的问题 ([#5602](https://github.com/pingcap/tidb-operator/pull/5602), [@ideascf](https://github.com/ideascf))
- 修复滚动重启 TiKV 时，没有对最后一个 TiKV Pod 执行 `tikv-min-ready-seconds` 检查的问题 ([#5544](https://github.com/pingcap/tidb-operator/pull/5544), [@wangz1x](https://github.com/wangz1x))
- 修复仅能使用非 `cluster.local` clusterDomain 的 TLS 证书时 TiDB 集群无法启动的问题 ([#5560](https://github.com/pingcap/tidb-operator/pull/5560), [@csuzhangxc](https://github.com/csuzhangxc))
