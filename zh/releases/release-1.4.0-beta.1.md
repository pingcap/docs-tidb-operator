---
title: TiDB Operator 1.4.0-beta.1 Release Notes
summary: TiDB Operator 1.4.0-beta.1 发布，新增支持基于 Amazon EBS 的 TiDB 集群 volume-snapshot 备份和恢复（实验特性），修复了日志备份的 checkpoint ts 无法更新的问题。
aliases: ['/zh/tidb-in-kubernetes/dev/release-1.4.0-beta.1/','/zh/tidb-in-kubernetes/v1.3/release-1.4.0-beta.1/','/zh/tidb-in-kubernetes/v1.4/release-1.4.0-beta.1/','/zh/tidb-in-kubernetes/v1.5/release-1.4.0-beta.1/','/zh/tidb-in-kubernetes/v1.6/release-1.4.0-beta.1/','/zh/tidb-in-kubernetes/v2.0/release-1.4.0-beta.1/']
---

# TiDB Operator 1.4.0-beta.1 Release Notes

发布日期：2022 年 10 月 27 日

TiDB Operator 版本：1.4.0-beta.1

## 新功能

- 支持基于 Amazon EBS 的 TiDB 集群 volume-snapshot 的备份和恢复（实验特性） ([#4698](https://github.com/pingcap/tidb-operator/pull/4698), [@gozssky](https://github.com/gozssky))，此功能有以下特点：

    - 将备份对 QPS 的影响降至小于 5%
    - 缩短备份和恢复时间

## 错误修复

- 修复 TiDB Operator 重启后，日志备份的 checkpoint ts 无法更新的问题 ([#4746](https://github.com/pingcap/tidb-operator/pull/4746), [@WizardXiao](https://github.com/WizardXiao))

- 修复 TiDB 集群开启 TLS 认证时，日志备份的 checkpoint ts 无法更新的问题 ([#4716](https://github.com/pingcap/tidb-operator/pull/4716), [@WizardXiao](https://github.com/WizardXiao))
