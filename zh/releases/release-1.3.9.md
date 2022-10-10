---
title: TiDB Operator 1.3.9 Release Notes
---

# TiDB Operator 1.3.9 Release Notes

发布日期：2022 年 10 月 10 日

TiDB Operator 版本：1.3.9

## 错误修复

- 修复了在已设置 `acrossK8s` 字段但未设置 `clusterDomain` 的情况下，PD 升级流程会卡住的问题 ([#4522](https://github.com/pingcap/tidb-operator/pull/4721), [@liubog2008](https://github.com/liubog2008))
