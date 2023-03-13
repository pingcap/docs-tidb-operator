---
title: TiDB Operator 1.4.4 Release Notes
---

# TiDB Operator 1.4.4 Release Notes

发布日期: 2023 年 3 月 13 日

TiDB Operator 版本：1.4.4

## 新功能

- 支持在已部署 TiFlash 的集群上使用卷快照备份和恢复 ([#4812](https://github.com/pingcap/tidb-operator/pull/4812), [@fengou1](https://github.com/fengou1))

- 支持在卷快照备份中准确显示备份大小，数据根据快照存储的使用情况计算得出 ([#4819](https://github.com/pingcap/tidb-operator/pull/4819), [@fengou1](https://github.com/fengou1))

- 在 Kubernetes 导致 Job 或 Pod 意外失败时，支持重试快照备份 ([#4895](https://github.com/pingcap/tidb-operator/pull/4895), [@WizardXiao](https://github.com/WizardXiao))

- 支持在 `BackupSchedule` CR 中集成管理日志备份和快照备份 ([#4904](https://github.com/pingcap/tidb-operator/pull/4904), [@WizardXiao](https://github.com/WizardXiao))

## Bug 修复

- 修复在使用用户自定义构建的非语义版本格式的 TiDB 镜像时，同步失败的问题 ([#4920](https://github.com/pingcap/tidb-operator/pull/4920), [@sunxiaoguang](https://github.com/sunxiaoguang))

- 通过确保 PVC 名称的连续性，修复了在使用卷快照来备份一个已缩容的集群后，无法恢复数据的问题 ([#4888](https://github.com/pingcap/tidb-operator/pull/4888), [@WangLe1321](https://github.com/WangLe1321))

- 修复当两个快照之间没有块变更时，卷快照备份可能崩溃的问题 ([#4922](https://github.com/pingcap/tidb-operator/pull/4922), [@fengou1](https://github.com/fengou1))

- 通过在卷快照恢复时增加加密检查，修复了卷快照可能在恢复最后阶段失败的问题 ([#4914](https://github.com/pingcap/tidb-operator/pull/4914), [@fengou1](https://github.com/fengou1))
