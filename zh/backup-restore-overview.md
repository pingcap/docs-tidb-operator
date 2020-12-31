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