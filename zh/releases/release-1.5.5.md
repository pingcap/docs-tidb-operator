---
title: TiDB Operator 1.5.5 Release Notes
summary: 了解 TiDB Operator 1.5.5 版本的新功能和优化提升。
---

# TiDB Operator 1.5.5 Release Notes

发布日期：2025 年 1 月 21 日

TiDB Operator 版本：1.5.5

## 新功能

- 日志备份功能新增一个更直观的接口，支持暂停和恢复日志备份任务 ([#5710](https://github.com/pingcap/tidb-operator/pull/5710), [@RidRisR](https://github.com/RidRisR))
- 日志备份功能支持通过直接删除 CR 停止备份任务 ([#5754](https://github.com/pingcap/tidb-operator/pull/5754), [@RidRisR](https://github.com/RidRisR))

## 优化提升

- VolumeModify 功能不再对 TiKV 执行 evict leader 操作以缩短变更所需的时间 ([#5826](https://github.com/pingcap/tidb-operator/pull/5826), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持通过 annotation 指定 PD Pod 滚动更新过程中的最小等待时间 ([#5827](https://github.com/pingcap/tidb-operator/pull/5827), [@csuzhangxc](https://github.com/csuzhangxc))
