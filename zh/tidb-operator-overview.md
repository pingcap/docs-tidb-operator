---
title: TiDB Operator 简介
summary: 介绍 TiDB Operator 的整体架构及使用方式。
---

# TiDB Operator 简介

[TiDB Operator](https://github.com/pingcap/tidb-operator) 是 Kubernetes 上的 TiDB 集群自动运维系统，提供包括部署、升级、扩缩容、备份恢复、配置变更的 TiDB 全生命周期管理。借助 TiDB Operator，TiDB 可以无缝运行在公有云或自托管的 Kubernetes 集群上。

## TiDB Operator 与 TiDB 的版本兼容性

TiDB Operator 与适用的 TiDB 版本的对应关系如下：

| TiDB 版本 | 适用的 TiDB Operator 版本 |
|:---|:---|
| dev               | dev                 |
| TiDB >= 8.0       | 2.0，1.6（推荐），1.5 |
| 7.1 <= TiDB < 8.0 | 1.5（推荐），1.4 |
| 6.5 <= TiDB < 7.1 | 1.5，1.4（推荐），1.3     |
| 5.4 <= TiDB < 6.5 | 1.4，1.3（推荐）   |
| 5.1 <= TiDB < 5.4 | 1.4，1.3（推荐），1.2（停止维护）      |
| 3.0 <= TiDB < 5.1 | 1.4，1.3（推荐），1.2（停止维护），1.1（停止维护） |
| 2.1 <= TiDB < v3.0| 1.0（停止维护）       |

## TiDB Operator v2 与 v1 的区别

随着 TiDB 和 Kubernetes 生态的快速发展，TiDB Operator 发布了与 v1 不兼容的 v2 版本。关于 v2 与 v1 的详细差异，请参考 [TiDB Operator v2 与 v1 版本对比](v2-vs-v1.md)。

## 使用 TiDB Operator 管理 TiDB 集群

在 Kubernetes 环境中，TiDB Operator 可用于高效部署和管理 TiDB 集群。你可以根据不同需求选择以下部署方式：

- 如需在测试环境中快速部署 TiDB Operator 并搭建一个 TiDB 集群，请参考[快速开始](get-started.md)。
- 如需自定义部署 TiDB Operator，请参阅[部署 TiDB Operator](deploy-tidb-operator.md)。

在任何环境上部署前，都可以参考下面的文档来自定义 TiDB 配置：

+ [存储卷配置](volume-configuration.md)
+ [自定义 Pod](overlay.md)

部署完成后，你可以参考下面的文档进行 Kubernetes 上 TiDB 集群的使用和运维：

+ [部署 TiDB 集群](deploy-tidb-cluster.md)
+ [访问 TiDB 集群](access-tidb.md)
+ [TiDB 集群扩缩容](scale-a-tidb-cluster.md)
+ [查看 TiDB 日志](view-logs.md)

当集群出现问题需要进行诊断时，你可以：

+ 查阅 [Kubernetes 上的 TiDB FAQ](faq.md) 寻找是否存在现成的解决办法；
+ 参考 [Kubernetes 上的 TiDB 故障诊断](tips.md)解决故障。

在 Kubernetes 上，TiDB 的部分生态工具的使用方法也有所不同，你可以参考 [Kubernetes 上的 TiDB 相关工具使用指南](tidb-toolkit.md)来了解 TiDB 生态工具在 Kubernetes 上的使用方法。

最后，当 TiDB Operator 发布新版本时，你可以参考[升级 TiDB Operator](upgrade-tidb-operator.md) 进行版本更新。
