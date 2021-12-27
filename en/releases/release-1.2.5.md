---
title: TiDB Operator 1.2.5 Release Notes
---

# TiDB Operator 1.2.5 Release Notes

Release date: December 27, 2021

TiDB Operator version: 1.2.5

## Improvements

- Support configuring all fields in `ComponentSpec` for DM to control component behavior more finely ([#4313](https://github.com/pingcap/tidb-operator/pull/4313), [@csuzhangxc](https://github.com/csuzhangxc))
- Support configuring init container `resources` for TiFlash ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- Support configuring the `ssl-ca` parameter for TiDB via `TiDBTLSClient` to disable client authentication ([#4270](https://github.com/pingcap/tidb-operator/pull/4270), [@just1900](https://github.com/just1900))
- Add a `ready` field to TiCDC captures to show its readiness status ([#4273](https://github.com/pingcap/tidb-operator/pull/4273), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue that PD, TiKV, and TiDB cannot roll update after the component startup script is updated ([#4248](https://github.com/pingcap/tidb-operator/pull/4248), [@KanShiori](https://github.com/KanShiori))
- Fix the issue that the TidbCluster spec is updated automatically after TLS is enabled ([#4306](https://github.com/pingcap/tidb-operator/pull/4306), [@KanShiori](https://github.com/KanShiori))
- Fix a potential goroutine leak when TiDB Operator checks the Region leader count of TiKV ([#4291](https://github.com/pingcap/tidb-operator/pull/4291), [@DanielZhangQD](https://github.com/DanielZhangQD))
- Fix some high-level security issues ([#4240](https://github.com/pingcap/tidb-operator/pull/4240), [@KanShiori](https://github.com/KanShiori))
