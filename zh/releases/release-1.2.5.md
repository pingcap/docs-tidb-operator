---
title: TiDB Operator 1.2.5 Release Notes
---

# TiDB Operator 1.2.5 Release Notes

发布日期：2021 年 12 月 27 日

TiDB Operator 版本：1.2.5

## 优化提升

- 支持为 DM 配置所有组件级字段 ([#4313](https://github.com/pingcap/tidb-operator/pull/4313), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TiFlash init container 配置 `resources` ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- 支持通过 `TiDBTLSClient` 为 TiDB 配置 `ssl-ca` 参数 ([#4270](https://github.com/pingcap/tidb-operator/pull/4270), [@just1900](https://github.com/just1900))
- 为 TiCDC captures 增加 `ready` 状态 ([#4273](https://github.com/pingcap/tidb-operator/pull/4273), [@KanShiori](https://github.com/KanShiori))

## Bug 修复

- 修复组件启动脚本更新后，PD、TiKV 及 TiDB 不会滚动更新的问题 ([#4248](https://github.com/pingcap/tidb-operator/pull/4248), [@KanShiori](https://github.com/KanShiori))
- 修复启用 TLS 后 TidbCluster spec 被自动更新的问题 ([#4306](https://github.com/pingcap/tidb-operator/pull/4306), [@KanShiori](https://github.com/KanShiori))
- 修复计算 TiKV region leader 数量时会造成 goroutine 泄露的问题 ([#4291](https://github.com/pingcap/tidb-operator/pull/4291), [@DanielZhangQD](https://github.com/DanielZhangQD))
- 修复一些高级别的安全问题 ([#4240](https://github.com/pingcap/tidb-operator/pull/4240), [@KanShiori](https://github.com/KanShiori))
