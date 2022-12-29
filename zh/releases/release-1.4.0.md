---
title: TiDB Operator 1.4.0 Release Notes
---

# TiDB Operator 1.4.0 Release Notes

发布日期: 2022 年 12 月 29 日

TiDB Operator 版本：1.4.0

## 新功能

- 支持使用新的 `TidbDashboard` CRD 独立管理 [TiDB Dashboard](https://github.com/pingcap/tidb-dashboard) ([#4787](https://github.com/pingcap/tidb-operator/pull/4787), [@SabaPing](https://github.com/SabaPing))
- 支持为 TiKV 与 PD 配置 Liveness Probe ([#4763](https://github.com/pingcap/tidb-operator/pull/4763), [@mikechengwei](https://github.com/mikechengwei))
- 支持基于 Amazon EBS 的 TiDB 集群 volume-snapshot 的备份和恢复 ([#4698](https://github.com/pingcap/tidb-operator/pull/4698)，[@gozssky] (https://github.com/gozssky)

## 优化提升

- 适配新的 TiProxy 版本 ([#4802](https://github.com/pingcap/tidb-operator/pull/4802), [@xhebox](https://github.com/xhebox))

## Bug 修复

- 修复基于 EBS 快照备份无法恢复到不同 namespace 的问题 ([#4795](https://github.com/pingcap/tidb-operator/pull/4795), [@fengou1](https://github.com/fengou1))
- 修复日志备份停止占用 Complete 状态，导致调用方误认为日志备份 CR 已完成，从而无法继续对日志备份进行 Truncate 操作的问题 ([#4810](https://github.com/pingcap/tidb-operator/pull/4810), [@WizardXiao](https://github.com/WizardXiao))
