---
title: TiDB Operator 1.6.2 Release Notes
summary: 了解 TiDB Operator 1.6.2 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.2 Release Notes

发布日期: 2025 年 7 月 4 日

TiDB Operator 版本：1.6.2

## 新功能


## 优化提升

- 在 scale in TiKV 时，支持先 evict leader 再删除 store ([#6239](https://github.com/pingcap/tidb-operator/pull/6239), [@liubog2008](https://github.com/liubog2008))
- 在升级 PD 时，支持使用 PD 新的 `ready` API 检测 PD 是否 ready ([#6243](https://github.com/pingcap/tidb-operator/pull/6243), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持在优雅重启 TiKV 之前强制将 backup log 文件落盘 ([#6057](https://github.com/pingcap/tidb-operator/pull/6057), [@YuJuncen](https://github.com/YuJuncen))
- 支持基于策略的自动重试失败的恢复任务 ([#6092](https://github.com/pingcap/tidb-operator/pull/6092), [@RidRisR](https://github.com/RidRisR))
- 支持对 backup log 的压缩以及设置对应的定时任务 ([#6033](https://github.com/pingcap/tidb-operator/pull/6033), [@RidRisR](https://github.com/RidRisR))
- 将恢复任务的 `--pitrRestoredTs` 参数从必选变为可选 ([#6135](https://github.com/pingcap/tidb-operator/pull/6135), [@RidRisR](https://github.com/RidRisR))
- 支持 namespace 级别的 backup tracker ([#6160](https://github.com/pingcap/tidb-operator/pull/6160), [@WangLe1321](https://github.com/WangLe1321))
- 针对 FIPS 备份，支持指定强制路径样式的 URL ([#6250](https://github.com/pingcap/tidb-operator/pull/6250), [@3pointer](https://github.com/3pointer))
- 支持在 backup manager 使用定制 S3 endpoint ([#6268](https://github.com/pingcap/tidb-operator/pull/6268), [@3pointer](https://github.com/3pointer))

## Bug 修复

- 修复在 TiProxy Pods 不健康时 TidbCluster CR 错误地被标记为 `Ready` 的问题 ([#6151](https://github.com/pingcap/tidb-operator/pull/6151), [@ideascf](https://github.com/ideascf))
- 修复 EBS 磁盘快照备份在遇到某个 TC 格式无效导致的无法退出的问题 ([#6087](https://github.com/pingcap/tidb-operator/pull/6087), [@BornChanger](https://github.com/BornChanger))
- 修复 PITR 恢复中，因为 TiKV 重启后，`gc.ratio-threshold` 参数被重置，导致数据出错问题 ([#6267](https://github.com/pingcap/tidb-operator/pull/6267), [@YuJuncen](https://github.com/YuJuncen))
