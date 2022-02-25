---
title: TiDB in Kubernetes 用户文档
summary: 了解 TiDB in Kubernetes 的用户文档。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/']
---

<!-- markdownlint-disable MD046 -->

# TiDB in Kubernetes 用户文档

你可以使用 [TiDB Operator](https://github.com/pingcap/tidb-operator) 在 Kubernetes 上部署 TiDB。TiDB Operator 是 Kubernetes 上的 TiDB 集群自动运维系统，提供包括部署、升级、扩缩容、备份恢复、配置变更的 TiDB 全生命周期管理。借助 TiDB Operator，TiDB 可以无缝运行在公有云或私有部署的 Kubernetes 集群上。

TiDB 与 TiDB Operator 版本的对应关系如下：

| TiDB 版本 | 适用的 TiDB Operator 版本 |
|:---|:---|
| dev               | dev                 |
| TiDB >= 5.4       | 1.3                 |
| 5.1 <= TiDB < 5.4 | 1.3（推荐），1.2      |
| 3.0 <= TiDB < 5.1 | 1.3（推荐），1.2，1.1 |
| 2.1 <= TiDB < v3.0| 1.0（停止维护）       |

<NavColumns>
<NavColumn>
<ColumnTitle>关于 TiDB Operator</ColumnTitle>

- [TiDB Operator 简介](tidb-operator-overview.md)
- [TiDB Operator v1.3 新特性](whats-new-in-v1.3.md)

</NavColumn>

<NavColumn>
<ColumnTitle>快速上手</ColumnTitle>

- [kind](get-started.md#使用-kind-创建-kubernetes-集群)
- [Minikube](get-started.md#使用-minikube-创建-kubernetes-集群)
- [Google Cloud Shell](https://console.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/pingcap/docs-tidb-operator&cloudshell_tutorial=zh/deploy-tidb-from-kubernetes-gke.md)

</NavColumn>

<NavColumn>
<ColumnTitle>部署集群</ColumnTitle>

- [部署到 Amazon EKS](deploy-on-aws-eks.md)
- [部署到 GCP GKE](deploy-on-gcp-gke.md)
- [部署到 Azure AKS](deploy-on-azure-aks.md)
- [部署到阿里云 ACK](deploy-on-alibaba-cloud.md)
- [部署到自托管的 Kubernetes](prerequisites.md)
- [部署 TiDB HTAP 存储引擎 TiFlash](deploy-tiflash.md)

</NavColumn>

<NavColumn>
<ColumnTitle>安全</ColumnTitle>

- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)
- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 TiDB DM 组件开启 TLS](enable-tls-for-dm.md)
- [同步数据到开启 TLS 的下游服务](enable-tls-for-ticdc-sink.md)
- [更新和替换 TLS 证书](renew-tls-certificate.md)
- [以非 root 用户运行容器](containers-run-as-non-root-user.md)

</NavColumn>

<NavColumn>
<ColumnTitle>管理</ColumnTitle>

- [升级 TiDB 集群](upgrade-a-tidb-cluster.md)
- [升级 TiDB Operator](upgrade-tidb-operator.md)
- [水平扩缩容 TiDB 集群](scale-a-tidb-cluster.md)
- [备份与恢复数据](backup-restore-overview.md)
- [部署 TiDB 集群监控与告警](monitor-a-tidb-cluster.md)
- [维护 TiDB 集群所在节点](maintain-a-kubernetes-node.md)
- [集群故障自动转移](use-auto-failover.md)

</NavColumn>

<NavColumn>
<ColumnTitle>参考</ColumnTitle>

- [架构](tidb-scheduler.md)
- [API 参考文档](https://github.com/pingcap/tidb-operator/blob/master/docs/api-references/docs.md)
- [工具](use-tkctl.md)
- [配置](configure-tidb-binlog-drainer.md)

</NavColumn>

</NavColumns>
