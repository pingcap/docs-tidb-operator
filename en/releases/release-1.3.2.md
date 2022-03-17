---
title: TiDB Operator 1.3.2 Release Notes
---

# TiDB Operator 1.3.2 Release Notes

Release date: March 17, 2022

TiDB Operator version: 1.3.2

## Improvements

- Support for TiDB to run on Istio-enabled kubernetes clusters ([#4445](https://github.com/pingcap/tidb-operator/pull/4445), [@rahilsh](https://github.com/rahilsh))
- Support multi-arch docker image ([#4469](https://github.com/pingcap/tidb-operator/pull/4469), [@better0332](https://github.com/better0332))

## Bug fixes

- Fix the issue that TiDB cluster's PD components failed to start due to discovery service errors ([#4440](https://github.com/pingcap/tidb-operator/pull/4440), [@liubog2008](https://github.com/liubog2008))