---
title: TiDB Operator 1.3.3 Release Notes
---

# TiDB Operator 1.3.3 Release Notes

Release date: May 16, 2022

TiDB Operator version: 1.3.3

## New Feature

- Add a new field `spec.tidb.service.port` to customize tidb service port ([#4512](https://github.com/pingcap/tidb-operator/pull/4512), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue evict leader scheduler may leak when upgrading cluster ([#4522](https://github.com/pingcap/tidb-operator/pull/4522), [@KanShiori](https://github.com/KanShiori))
