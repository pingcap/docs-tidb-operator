---
title: TiDB Operator 1.6.5 Release Notes
summary: 了解 TiDB Operator 1.6.5 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.5 Release Notes

发布日期：2026 年 1 月 28 日

TiDB Operator 版本：1.6.5

## 新功能

- 支持为 TiDBCluster 组件配置 `VolumeAttributesClass`，从而能够动态管理卷属性（如 IOPS 和吞吐量） ([#6568](https://github.com/pingcap/tidb-operator/pull/6568), [@WangLe1321](https://github.com/WangLe1321))

## 优化提升

- 将备份相关脚本的 shell 解释器从 `sh` 修改为 `bash`，以更好地支持 bash 特有语法 ([#6618](https://github.com/pingcap/tidb-operator/pull/6618), [@liubog2008](https://github.com/liubog2008))

## Bug 修复

- 修复当 etcd 中找不到日志备份任务时控制器无限重试的问题，在此情况下会将 Backup CR 状态更新为 `Failed` ([#6630](https://github.com/pingcap/tidb-operator/pull/6630), [@RidRisR](https://github.com/RidRisR))
- 修复与部分 Kubernetes 版本（如 v1.33）的兼容性问题，避免 TiDB Operator 在每个同步周期内重复尝试创建已存在的资源 ([#6653](https://github.com/pingcap/tidb-operator/pull/6653), [@cicada-lewis](https://github.com/cicada-lewis))
