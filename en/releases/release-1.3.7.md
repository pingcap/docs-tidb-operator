---
title: TiDB Operator 1.3.7 Release Notes
---

# TiDB Operator 1.3.7 Release Notes

Release date: August 1, 2022

TiDB Operator version: 1.3.7

## New Features

- Add the `suspendAction` field to suspend any component. If a component is suspended, the `StatefulSet` of the component will be deleted. ([#4640](https://github.com/pingcap/tidb-operator/pull/4640), [@KanShiori](https://github.com/KanShiori))

## Improvement

- After all PVCs are scaled up, recreate the `StatefulSet` of a component so that new PVCs use the desired storage size ([#4620](https://github.com/pingcap/tidb-operator/pull/4620), [@KanShiori](https://github.com/KanShiori))

- To avoid the TiKV PVC scale-up process getting stuck, continue scale-up if a leader eviction times out ([#4625](https://github.com/pingcap/tidb-operator/pull/4625), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue that TiKV cannot be upgraded when using local storage ([#4615](https://github.com/pingcap/tidb-operator/pull/4615), [@KanShiori](https://github.com/KanShiori))

- Fix the issue that backup files may leak after cleanup ([#4617](https://github.com/pingcap/tidb-operator/pull/4617), [@KanShiori](https://github.com/KanShiori))
