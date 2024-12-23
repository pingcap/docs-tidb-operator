---
title: TiDB Operator 简介
summary: 介绍 TiDB Operator 的整体架构及使用方式。
---

# TiDB Operator 简介

[TiDB Operator](https://github.com/pingcap/tidb-operator) 是 Kubernetes 上的 TiDB 集群自动运维系统，提供包括部署、升级、扩缩容、备份恢复、配置变更的 TiDB 全生命周期管理。借助 TiDB Operator，TiDB 可以无缝运行在公有云或自托管的 Kubernetes 集群上。

TiDB Operator 与适用的 TiDB 版本的对应关系如下：

| TiDB 版本 | 适用的 TiDB Operator 版本 |
|:---|:---|
| dev               | dev                 |
| TiDB >= 8.0       | 1.6（推荐），1.5 |
| 7.1 <= TiDB < 8.0 | 1.5（推荐），1.4 |
| 6.5 <= TiDB < 7.1 | 1.5, 1.4（推荐），1.3     |
| 5.4 <= TiDB < 6.5 | 1.4, 1.3（推荐）   |
| 5.1 <= TiDB < 5.4 | 1.4，1.3（推荐），1.2（停止维护）      |
| 3.0 <= TiDB < 5.1 | 1.4，1.3（推荐），1.2（停止维护），1.1（停止维护） |
| 2.1 <= TiDB < v3.0| 1.0（停止维护）       |

## 使用 TiDB Operator 管理 TiDB 集群

TiDB Operator 提供了多种方式来部署 Kubernetes 上的 TiDB 集群：

+ 测试环境：

    - [kind](get-started.md#方法一使用-kind-创建-kubernetes-集群)
    - [Minikube](get-started.md#方法二使用-minikube-创建-kubernetes-集群)
    - [Google Cloud Shell](https://console.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/pingcap/docs-tidb-operator&cloudshell_tutorial=zh/deploy-tidb-from-kubernetes-gke.md)

+ 生产环境：

    - 在公有云上部署生产可用的 TiDB 集群并进行后续的运维管理；

        - [在 AWS EKS 上部署 TiDB 集群](deploy-on-aws-eks.md)
        - [在 Google Cloud GKE 上部署 TiDB 集群](deploy-on-gcp-gke.md)
        - [在 Azure AKS 上部署 TiDB 集群](deploy-on-azure-aks.md)

    - 在自托管的 Kubernetes 集群中部署 TiDB 集群：

        首先按照[部署 TiDB Operator](deploy-tidb-operator.md)在集群中安装 TiDB Operator，再根据[在标准 Kubernetes 集群上部署 TiDB 集群](deploy-on-general-kubernetes.md)来部署你的 TiDB 集群。对于生产级 TiDB 集群，你还需要参考 [TiDB 集群环境要求](prerequisites.md)调整 Kubernetes 集群配置并根据[本地 PV 配置](configure-storage-class.md#本地-pv-配置)为你的 Kubernetes 集群配置本地 PV，以满足 TiKV 的低延迟本地存储需求。

在任何环境上部署前，都可以参考 [TiDB 集群配置](configure-a-tidb-cluster.md)来自定义 TiDB 配置。

部署完成后，你可以参考下面的文档进行 Kubernetes 上 TiDB 集群的使用和运维：

+ [部署 TiDB 集群](deploy-on-general-kubernetes.md)
+ [访问 TiDB 集群](access-tidb.md)
+ [TiDB 集群扩缩容](scale-a-tidb-cluster.md)
+ [TiDB 集群升级](upgrade-a-tidb-cluster.md)
+ [TiDB 集群配置变更](configure-a-tidb-cluster.md)
+ [TiDB 集群备份与恢复](backup-restore-overview.md)
+ [配置 TiDB 集群故障自动转移](use-auto-failover.md)
+ [监控 TiDB 集群](monitor-a-tidb-cluster.md)
+ [查看 TiDB 日志](view-logs.md)
+ [维护 TiDB 所在的 Kubernetes 节点](maintain-a-kubernetes-node.md)

当集群出现问题需要进行诊断时，你可以：

+ 查阅 [Kubernetes 上的 TiDB FAQ](faq.md) 寻找是否存在现成的解决办法；
+ 参考 [Kubernetes 上的 TiDB 故障诊断](tips.md)解决故障。

在 Kubernetes 上，TiDB 的部分生态工具的使用方法也有所不同，你可以参考 [Kubernetes 上的 TiDB 相关工具使用指南](tidb-toolkit.md)来了解 TiDB 生态工具在 Kubernetes 上的使用方法。

最后，当 TiDB Operator 发布新版本时，你可以参考[升级 TiDB Operator](upgrade-tidb-operator.md) 进行版本更新。
