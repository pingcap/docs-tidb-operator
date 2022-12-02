---
title: TiDB Operator 1.4.0-beta.3 Release Notes
---

# TiDB Operator 1.4.0-beta.3 Release Notes

Release date: December 2, 2022

TiDB Operator version: 1.4.0-beta.3

## New Feature

- Experimental support for TiProxy ([#4693](https://github.com/pingcap/tidb-operator/pull/4693)), [@xhebox](https://github.com/xhebox)

## Bug fixes

- Fix typo in error messages ([#4773](https://github.com/pingcap/tidb-operator/pull/4773), [@dveeden](https://github.com/dveeden))

- Fix volume-snapshot backup cleanup failure ([#4783](https://github.com/pingcap/tidb-operator/pull/4783), [@fengou1](https://github.com/fengou1))

- Fix backup failure on tidb cluster has massive tikv nodes (40+) ([#4784](https://github.com/pingcap/tidb-operator/pull/4784), [@fengou1](https://github.com/fengou1))
