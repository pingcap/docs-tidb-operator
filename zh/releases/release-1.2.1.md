---
title: TiDB Operator 1.2.1 Release Notes
---

# TiDB Operator 1.2.1 Release Notes

发布日期：2021 年 8 月 18 日

TiDB Operator 版本：1.2.1

## Rolling update changes

- 由于 [#4141](https://github.com/pingcap/tidb-operator/pull/4141) 的改动，如果你部署 TiCDC 配置了 `hostNetwork`，那么升级 TiDB Operator 后会导致 TiCDC Pod 删除重建

## Improvements

- 所有组件都支持配置 `hostNetwork` ([#4141](https://github.com/pingcap/tidb-operator/pull/4141), [@DanielZhangQD](https://github.com/DanielZhangQD)
