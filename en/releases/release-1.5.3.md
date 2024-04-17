---
title: TiDB Operator 1.5.3 Release Notes
summary: Learn about new features and bug fixes in TiDB Operator 1.5.3.
---

# TiDB Operator 1.5.3 Release Notes

Release date: April 18, 2024

TiDB Operator version: 1.5.3

## New features

- Support setting `livenessProbe` and `readinessProbe` for the Discovery component ([#5565](https://github.com/pingcap/tidb-operator/pull/5565), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting `nodeSelector` for the TidbInitializer component ([#5594](https://github.com/pingcap/tidb-operator/pull/5594), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug fixes

- Fix the issue that modifying the storage size of components might cause them to restart when `configUpdateStrategy` is set to `InPlace` ([#5602](https://github.com/pingcap/tidb-operator/pull/5602), [@ideascf](https://github.com/ideascf))
- Fix the issue that the `tikv-min-ready-seconds` check is not performed on the last TiKV Pod during a rolling restart of TiKV ([#5544](https://github.com/pingcap/tidb-operator/pull/5544), [@wangz1x](https://github.com/wangz1x))
- Fix the issue that the TiDB cluster cannot start when only non-`cluster.local` clusterDomain TLS certificates are available ([#5560](https://github.com/pingcap/tidb-operator/pull/5560), [@csuzhangxc](https://github.com/csuzhangxc))
