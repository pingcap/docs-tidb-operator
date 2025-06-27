---
title: TiDB Operator 1.6.2 Release Notes
summary: 了解 TiDB Operator 1.6.2 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.2 Release Notes

发布日期: 2025 年 7 月 4 日

TiDB Operator 版本：1.6.2

## 新功能


## 优化提升

- 在 scale in TiKV 时，支持先 evict leader 再删除 store ([#6239](https://github.com/pingcap/tidb-operator/pull/6239), [@liubog2008](https://github.com/liubog2008))
- 在升级 PD 时，支持使用 PD 新的 `ready` API 检测 PD 是否 ready ([#6243](https://github.com/pingcap/tidb-operator/pull/6243), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug 修复

- 修复在 TiProxy Pods 不健康时 TidbCluster CR 错误地被标记为 `Ready` 的问题 ([#6151](https://github.com/pingcap/tidb-operator/pull/6151), [@ideascf](https://github.com/ideascf))
