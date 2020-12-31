---
title: TiDB 集群备份与恢复简介
summary: 介绍如何使用 BR、Dumpling、TiDB Lightning 工具对 Kubernetes 上的 TiDB 集群进行数据备份和数据恢复。
---

# TiDB 集群备份与恢复简介

本文档介绍如何使用 [`BR`](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool)、[`Dumpling`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview)、[TiDB Lightning](https://pingcap.com/docs/stable/how-to/get-started/tidb-lightning/#tidb-lightning-tutorial) 工具对 Kubernetes 上的 TiDB 集群进行数据备份和数据恢复。关于 BR、Dumpling、TiDB Lightning 工具分别适用的备份恢复场景，请参考以上链接。

TiDB Operator 1.1 及以上版本推荐使用基于 CustomResourceDefinition (CRD) 实现的备份恢复方式实现：

+ 如果 TiDB 集群版本 < v3.1，可以参考以下文档：

    - [使用 Dumpling 备份 TiDB 集群数据](backup-using-dumpling.md)
    - [使用 TiDB Lightning 恢复 TiDB 集群数据](restore-using-lightning.md)

+ 如果 TiDB 集群版本 >= v3.1，可以参考以下文档：

    - [使用 BR 备份 TiDB 集群数据](backup-using-br.md)
    - [使用 BR 工具恢复备份数据到 TiDB 集群](restore-using-br.md)

Kubernetes 上的 TiDB 集群支持两种备份策略：

* [全量备份](#全量备份)（定时执行或 Ad-hoc）：使用 [`mydumper`](https://pingcap.com/docs-cn/stable/mydumper-overview/) 获取集群的逻辑备份；
* [增量备份](#增量备份)：使用 [`TiDB Binlog`](https://pingcap.com/docs-cn/stable/tidb-binlog/tidb-binlog-overview/) 将 TiDB 集群的数据实时复制到其它数据库中或实时获得增量数据备份；

目前，Kubernetes 上的 TiDB 集群只对 `mydumper` 获取的全量备份数据提供自动化的数据恢复操作。恢复 `TiDB-Binlog` 获取的增量数据需要手动进行。