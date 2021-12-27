---
title: TiDB Operator 1.2.5 Release Notes
---

# TiDB Operator 1.2.5 Release Notes

Release date: December 27, 2021

TiDB Operator version: 1.2.5

## Improvements

- Support all component spec fields for DM ([#4313](https://github.com/pingcap/tidb-operator/pull/4313), [@csuzhangxc](https://github.com/csuzhangxc))
- Support configuring init container `resources` for TiFlash ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- Support configure TiDB `ssl-ca` parameter via `TiDBTLSClient` ([#4270](https://github.com/pingcap/tidb-operator/pull/4270), [@just1900](https://github.com/just1900))
- Add `ready` status for TiCDC captures ([#4273](https://github.com/pingcap/tidb-operator/pull/4273), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue that PD, TiKV and TiDB can't roll update when startup script have been updated ([#4248](https://github.com/pingcap/tidb-operator/pull/4248), [@KanShiori](https://github.com/KanShiori))
- Fix the issue that TidbCluster spec is updated automatically if TLS enabled ([#4306](https://github.com/pingcap/tidb-operator/pull/4306), [@KanShiori](https://github.com/KanShiori))
- Fix a potential goroutine leak when checking the region leader count of TiKV ([#4291](https://github.com/pingcap/tidb-operator/pull/4291), [@DanielZhangQD](https://github.com/DanielZhangQD))
- Fix some high security issues ([#4240](https://github.com/pingcap/tidb-operator/pull/4240), [@KanShiori](https://github.com/KanShiori))
