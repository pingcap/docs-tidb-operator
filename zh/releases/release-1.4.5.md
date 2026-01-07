---
title: TiDB Operator 1.4.5 Release Notes
summary: TiDB Operator 1.4.5 版本发布，优化了 TidbCluster 的错误处理相关 metrics 和 worker 队列相关 metrics，增加了 DM master 组件的 `startUpScriptVersion` 字段，以及跨 Kubernetes 集群滚动重启或缩容 TiCDC 集群的能力。同时修复了定时备份中取消 GC、Backup CR 字段可选值、TiDB Operator 未配置权限时的 panic 问题，以及 TidbCluster 中设置 `AdditionalVolumeMounts` 时可能的 panic 问题。
---

# TiDB Operator 1.4.5 Release Notes

发布日期: 2023 年 6 月 26 日

TiDB Operator 版本：1.4.5

## 优化提升

- 为 TidbCluster 增加细粒度的调协处理错误相关的 metrics ([#4952](https://github.com/pingcap/tidb-operator/pull/4952), [@coderplay](https://github.com/coderplay))
- 增加调协处理与 worker 队列相关的 metrics 以提升可观测性 ([#4882](https://github.com/pingcap/tidb-operator/pull/4882), [@hanlins](https://github.com/hanlins))
- 为 DM master 组件增加 `startUpScriptVersion` 字段以用于指定启动脚本的版本 ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))
- 增加跨 Kubernetes 集群滚动重启或缩容 TiCDC 集群的能力 ([#5040](https://github.com/pingcap/tidb-operator/pull/5040), [@charleszheng44](https://github.com/charleszheng44))

## 错误修复

- 在新创建的定时备份中取消 GC ([#4940](https://github.com/pingcap/tidb-operator/pull/4940), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- 让 Backup CR 字段里的 `backupTemplate` 字段变成可选值 ([#4956](https://github.com/pingcap/tidb-operator/pull/4956), [@Ehco1996](https://github.com/Ehco1996))
- 修复 TiDB Operator 在未配置任何 Kubernetes 集群级别权限时 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- 修复在 TidbCluster 中设置 `AdditionalVolumeMounts` 时 TiDB Operator 可能 panic 的问题 ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
