---
title: TiDB Operator 1.3.3 Release Notes
---

# TiDB Operator 1.3.3 Release Notes

发布日期: 2022 年 5 月 16 日

TiDB Operator 版本：1.3.3

## 新功能

- 添加新的 `spec.tidb.service.port` 字段，以支持配置 tidb 服务端口 ([#4512](https://github.com/pingcap/tidb-operator/pull/4512), [@KanShiori](https://github.com/KanShiori))

## Bug 修复

- 修复集群升级过程中，evict leader scheduler 可能泄漏的问题 ([#4522](https://github.com/pingcap/tidb-operator/pull/4522), [@KanShiori](https://github.com/KanShiori))
