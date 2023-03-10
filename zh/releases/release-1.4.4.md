---
title: TiDB Operator 1.4.4 Release Notes
---

# TiDB Operator 1.4.4 Release Notes

发布日期: 2023 年 3 月 13 日

TiDB Operator 版本：1.4.4

## 新功能

- 支持在集群有 TiFlash 时使用卷快照备份和恢复 ([#4812](https://github.com/pingcap/tidb-operator/pull/4812), [@fengou1](https://github.com/fengou1))

- 支持在卷快照备份中显示通过根据快照存储使用情况准确计算的备份大小 ([#4819](https://github.com/pingcap/tidb-operator/pull/4819), [@fengou1](https://github.com/fengou1))

- 支持在 kubernetes 导致 job 或 pod 意外失败时重试快照备份 ([#4895](https://github.com/pingcap/tidb-operator/pull/4895), [@WizardXiao](https://github.com/WizardXiao))

- 支持在 backup schedule 中集成管理日志备份和快照备份 ([#4904](https://github.com/pingcap/tidb-operator/pull/4904), [@WizardXiao](https://github.com/WizardXiao))

## Bug 修复

- 修复使用用户自定义构建的非语义版本格式的 TiDB 镜像造成同步失败的问题 ([#4920](https://github.com/pingcap/tidb-operator/pull/4920), [@sunxiaoguang](https://github.com/sunxiaoguang))

- 通过在保证 pvc 名称连续性，修复了卷快照在备份一个缩容集群时无法恢复的问题 ([#4888](https://github.com/pingcap/tidb-operator/pull/4888), [@WangLe1321](https://github.com/WangLe1321))

- 修复卷快照在两个快照之间没有块变更时可能倒是崩溃的问题 ([#4922](https://github.com/pingcap/tidb-operator/pull/4922), [@fengou1](https://github.com/fengou1))

- 通过在卷快照恢复时增加加密检查，修复了卷快照可能在恢复最后阶段失败的问题 ([#4914](https://github.com/pingcap/tidb-operator/pull/4914), [@fengou1](https://github.com/fengou1))
