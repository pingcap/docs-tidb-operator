---
title: TiDB Operator 1.1.12 Release Notes
---

# TiDB Operator 1.1.12 Release Notes

Release date: April 15, 2021

TiDB Operator version: 1.1.12

## New Features

- 支持为 `Backup` 和 `Restore` 的 job 自定义 `ENV` ([#3833](https://github.com/pingcap/tidb-operator/pull/3833), [@dragonly](https://github.com/dragonly))
- 支持在 `Backup` 和 `Restore` 中使用 `affinity` 和 `tolerations` ([#3835](https://github.com/pingcap/tidb-operator/pull/3835), [@dragonly](https://github.com/dragonly))
- 支持基于 node label 为 TiKV store 设置自定义 label ([#3784](https://github.com/pingcap/tidb-operator/pull/3784), [@L3T](https://github.com/L3T))

## Improvements

- 在 `TidbInitializer` 中增加 DNS lookup 重试 ([#3884](https://github.com/pingcap/tidb-operator/pull/3884), [@handlerww](https://github.com/handlerww))
- 当在 Helm chart 中设置 `appendReleaseSuffix` 为 `true` 时，TiDB Operator 相关资源使用新的 service account ([#3819](https://github.com/pingcap/tidb-operator/pull/3819), [@DanielZhangQD](https://github.com/DanielZhangQD))
- 优化 `PodsAreChanged` 函数 ([#3901](https://github.com/pingcap/tidb-operator/pull/3901), [@shonge](https://github.com/shonge))
- 增加 "Canary Deploy Operator from 1.1.10 to latest" E2E serial 测试 case ([#3764](https://github.com/pingcap/tidb-operator/pull/3764), [@shonge](https://github.com/shonge))

## Bug Fixes

- 修复存在多个 PVC 时错误地尝试对 PVC 进行扩缩容的问题 ([#3858](https://github.com/pingcap/tidb-operator/pull/3858) [#3891](https://github.com/pingcap/tidb-operator/pull/3891), [@dragonly](https://github.com/dragonly))
- 修复 `TidbCluster` 中 `spec.tidb` 为设置时 panic 的问题 ([#3852](https://github.com/pingcap/tidb-operator/pull/3852), [@dragonly](https://github.com/dragonly))
- 修复 PD 与 DM 的 `UnjoinedMembers` 中 PVC 状态异常的问题 ([#3836](https://github.com/pingcap/tidb-operator/pull/3836), [@dragonly](https://github.com/dragonly))
- 修复 PD 与 TiKV 的多 PVC 支持 ([#3820](https://github.com/pingcap/tidb-operator/pull/3820) [#3816](https://github.com/pingcap/tidb-operator/pull/3816), [@dragonly](https://github.com/dragonly))
