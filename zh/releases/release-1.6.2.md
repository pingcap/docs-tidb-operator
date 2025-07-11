---
title: TiDB Operator 1.6.2 Release Notes
summary: 了解 TiDB Operator 1.6.2 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.2 Release Notes

发布日期：2025 年 7 月 14 日

TiDB Operator 版本：1.6.2

## 新功能

- 支持压缩备份日志，并支持配置相应的定时任务，有助于优化存储空间管理 ([#6033](https://github.com/pingcap/tidb-operator/pull/6033), [@RidRisR](https://github.com/RidRisR))
- 支持 `abort restore` 命令，用于清理恢复作业残留的元数据 ([#6288](https://github.com/pingcap/tidb-operator/pull/6288), [@RidRisR](https://github.com/RidRisR))

## 优化提升

- 在缩容 TiKV 节点时，支持先驱逐 leader 再删除 store ([#6239](https://github.com/pingcap/tidb-operator/pull/6239), [@liubog2008](https://github.com/liubog2008))
- 在升级 PD 时，TiDB Operator 使用 PD 新的 `pd/api/v2/ready` API 检测 PD 就绪状态 ([#6243](https://github.com/pingcap/tidb-operator/pull/6243), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持在优雅重启 TiKV 之前强制将备份日志文件写入磁盘，以防止数据丢失 ([#6057](https://github.com/pingcap/tidb-operator/pull/6057), [@YuJuncen](https://github.com/YuJuncen))
- 支持基于策略自动重试失败的恢复任务 ([#6092](https://github.com/pingcap/tidb-operator/pull/6092), [@RidRisR](https://github.com/RidRisR))
- 将恢复任务的 `--pitrRestoredTs` 参数修改为可选项 ([#6135](https://github.com/pingcap/tidb-operator/pull/6135), [@RidRisR](https://github.com/RidRisR))
- 支持 namespace 级别的备份跟踪 ([#6160](https://github.com/pingcap/tidb-operator/pull/6160), [@WangLe1321](https://github.com/WangLe1321))
- 支持为 FIPS 备份指定强制路径样式的 URL ([#6250](https://github.com/pingcap/tidb-operator/pull/6250), [@3pointer](https://github.com/3pointer))
- 支持在 backup manager 中使用自定义 S3 endpoint ([#6268](https://github.com/pingcap/tidb-operator/pull/6268), [@3pointer](https://github.com/3pointer))

## Bug 修复

- 修复当 TiProxy Pods 不健康时，TidbCluster CR 被错误地标记为 `Ready` 的问题 ([#6151](https://github.com/pingcap/tidb-operator/pull/6151), [@ideascf](https://github.com/ideascf))
- 修复在使用 EBS 磁盘快照备份时，由于某个 TC 格式无效导致备份任务无法正常退出的问题 ([#6087](https://github.com/pingcap/tidb-operator/pull/6087), [@BornChanger](https://github.com/BornChanger))
- 修复 PITR 恢复过程中，由于 TiKV 重启后 `gc.ratio-threshold` 参数被重置导致数据错误的问题 ([#6267](https://github.com/pingcap/tidb-operator/pull/6267), [@YuJuncen](https://github.com/YuJuncen))
