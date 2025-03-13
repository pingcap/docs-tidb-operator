---
title: TiDB Operator 1.4.6 Release Notes
summary: TiDB Operator 1.4.6 发布，优化默认启用 volume resize 支持，修复备份恢复时报错问题，修复 TiCDC image tag 不符合语义化版本时无法 Graceful Drain TiCDC 的问题。
---

# TiDB Operator 1.4.6 Release Notes

发布日期: 2023 年 7 月 19 日

TiDB Operator 版本：1.4.6

## 优化提升

- 默认启用 volume resize 支持 ([#5167](https://github.com/pingcap/tidb-operator/pull/5167), [@liubog2008](https://github.com/liubog2008))

## 错误修复

- 修复使用 v6.6.0 及以上版本的 BR 执行备份恢复时报 `Error loading shared library libresolv.so.2` 的错误的问题 ([#4935](https://github.com/pingcap/tidb-operator/pull/4935), [@Ehco1996](https://github.com/Ehco1996))
- 修复使用的 TiCDC image tag 不符合语义化版本时无法 Graceful Drain TiCDC 的问题 ([#5173](https://github.com/pingcap/tidb-operator/pull/5173), [@csuzhangxc](https://github.com/csuzhangxc))
