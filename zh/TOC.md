# TiDB in Kubernetes 文档

<!-- markdownlint-disable MD007 -->
<!-- markdownlint-disable MD032 -->

## 文档目录

- [TiDB Operator 简介](tidb-operator-overview.md)
+ Benchmark
  - [Sysbench](benchmark-sysbench.md)
+ 快速上手
  - [kind](deploy-tidb-from-kubernetes-kind.md)
  - [GKE](deploy-tidb-from-kubernetes-gke.md)
  - [Minikube](deploy-tidb-from-kubernetes-minikube.md)
+ 部署
  - [集群环境要求](prerequisites.md)
  - [部署 TiDB Operator](deploy-tidb-operator.md)
  - [标准 Kubernetes 上的 TiDB 集群](deploy-on-general-kubernetes.md)
  - [AWS EKS 上的 TiDB 集群](deploy-on-aws-eks.md)
  - [GCP 上的 TiDB 集群](deploy-on-gcp-gke.md)
  - [阿里云上的 TiDB 集群](deploy-on-alibaba-cloud.md)
  - [访问 Kubernetes 上的 TiDB 集群](access-tidb.md)
  - [部署 TiDB Binlog](deploy-tidb-binlog.md)
+ 配置
  - [初始化集群](initialize-a-cluster.md)
  - [配置集群](configure-a-tidb-cluster.md)
  - [配置备份](configure-backup.md)
  - [配置 Storage Class](configure-storage-class.md)
  - [配置 TiDB Binlog Drainer](configure-tidb-binlog-drainer.md)
- [监控](monitor-a-tidb-cluster.md)
+ 运维
  - [销毁 TiDB 集群](destroy-a-tidb-cluster.md)
  - [重启 TiDB 集群](restart-a-tidb-cluster.md)
  - [维护 TiDB 集群所在节点](maintain-a-kubernetes-node.md)
  + 备份与恢复
    - [基于 Helm Charts 的备份恢复](backup-and-restore-using-helm-charts.md)
    - [使用 TiDB Lightning 恢复集群数据](restore-data-using-tidb-lightning.md)
  - [收集日志](collect-tidb-logs.md)
  - [集群故障自动转移](use-auto-failover.md)
- [扩缩容](scale-a-tidb-cluster.md)
+ 升级
  - [TiDB 集群](upgrade-a-tidb-cluster.md)
  - [TiDB Operator](upgrade-tidb-operator.md)
+ 工具
  - [tkctl](use-tkctl.md)
  - [TiDB Toolkit](tidb-toolkit.md)
+ 组件
    - [TiDB Scheduler 扩展调度器](tidb-scheduler.md)
- [故障诊断](troubleshoot.md)
- [常见问题](faq.md)
