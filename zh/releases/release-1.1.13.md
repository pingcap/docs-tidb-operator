---
title: TiDB Operator 1.1.13 Release Notes
---

# TiDB Operator 1.1.13 Release Notes

发布日期：2021 年 7 月 2 日

TiDB Operator 版本：1.1.13

## 优化提升

- 支持在未为 BR `toolImage` 指定 tag 时将 TiKV 版本作为 tag ([#4048](https://github.com/pingcap/tidb-operator/pull/4048), [@KanShiori](https://github.com/KanShiori))
- 支持在扩缩容 TiDB 过程中协调 PVCSupport handling PVC during scaling of TiDB ([#4033](https://github.com/pingcap/tidb-operator/pull/4033), [@csuzhangxc](https://github.com/csuzhangxc))
- 在日志中隐藏执行备份操作时的密码 ([#3979](https://github.com/pingcap/tidb-operator/pull/3979), [@dveeden](https://github.com/dveeden))

## Bug 修复

- 修复部署异构集群时 TiDB Operator 可能 panic 的问题 ([#4054](https://github.com/pingcap/tidb-operator/pull/4054), [@KanShiori](https://github.com/KanShiori))
- 修复 TiDB 实例在缩容后在 TiDB Dashboard 中仍然存在的问题 ([#3929](https://github.com/pingcap/tidb-operator/pull/3929), [@july2993](https://github.com/july2993))
