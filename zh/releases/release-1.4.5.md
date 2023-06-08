---
title: TiDB Operator 1.4.5 Release Notes
---

# TiDB Operator 1.4.5 Release Notes

发布日期: 2023 年 6 月 TODO 日

TiDB Operator 版本：1.4.5

## 优化提升

- 为 TidbCluster 增加细粒度的调协处理错误相关的 metrics ([#4952](https://github.com/pingcap/tidb-operator/pull/4952), [@coderplay](https://github.com/coderplay))
- 增加调协处理与 worker 队列相关的 metrics 以提升可观测性 ([#4882](https://github.com/pingcap/tidb-operator/pull/4882), [@hanlins](https://github.com/hanlins))
- 为 DM master 组件增加 `startUpScriptVersion` 字段以用于指定启动脚本的版本 ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))

## Bug 修复

- 在新创建的计划备份中取消 gc ([#4940](https://github.com/pingcap/tidb-operator/pull/4940), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- 让 Backup CR 字段里的 LogBackupTemplate 字段变成可选值 ([#4956](https://github.com/pingcap/tidb-operator/pull/4956), [@Ehco1996](https://github.com/Ehco1996))
