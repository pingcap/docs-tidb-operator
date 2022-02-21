---
title: TiDB in Kubernetes Documentation
summary: Learn about TiDB in Kubernetes documentation.
aliases: ['/docs/tidb-in-kubernetes/','/docs/tidb-in-kubernetes/stable/','/docs/tidb-in-kubernetes/v1.1/']
---

# TiDB in Kubernetes Documentation

[TiDB Operator](https://github.com/pingcap/tidb-operator) is an automatic operation system for TiDB clusters in Kubernetes. It provides a full management life-cycle for TiDB including deployment, upgrades, scaling, backup, fail-over, and configuration changes. With TiDB Operator, TiDB can run seamlessly in the Kubernetes clusters deployed on a public or private cloud.

The corresponding relationship between TiDB Operator and TiDB versions is as follows:

| TiDB versions | Compatible TiDB Operator versions |
|:---|:---|
| dev               | dev                 |
| TiDB >= 5.4       | 1.3                 |
| 5.1 <= TiDB < 5.4 | 1.3 (Recommended), 1.2      |
| 3.0 <= TiDB < 5.1 | 1.3 (Recommended), 1.2, 1.1 |
| 2.1 <= TiDB < v3.0| 1.0 (End of support)       |

<NavColumns>
<NavColumn>
<ColumnTitle>About TiDB Operator</ColumnTitle>

- [TiDB Operator Overview](tidb-operator-overview.md)
- [What's New in v1.1](whats-new-in-v1.1.md)
- [v1.1 Important Notes](notes-tidb-operator-v1.1.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Quick Start</ColumnTitle>

- [kind](get-started.md#create-a-kubernetes-cluster-using-kind)
- [Minikube](get-started.md#create-a-kubernetes-cluster-using-minikube)
- [GKE](deploy-tidb-from-kubernetes-gke.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Deploy TiDB</ColumnTitle>

- [On AWS EKS](deploy-on-aws-eks.md)
- [On GCP GKE](deploy-on-gcp-gke.md)
- [On Alibaba ACK](deploy-on-alibaba-cloud.md)
- [On Self-managed Kubernetes](deploy-on-general-kubernetes.md)
- [Deploy TiFlash](deploy-tiflash.md)
- [Deploy Monitoring Services](monitor-a-tidb-cluster.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Secure</ColumnTitle>

- [Enable TLS for the MySQL Client](enable-tls-for-mysql-client.md)
- [Enable TLS between TiDB Components](enable-tls-between-components.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Maintain</ColumnTitle>

- [Upgrade a TiDB Cluster](upgrade-a-tidb-cluster.md)
- [Upgrade TiDB Operator](upgrade-tidb-operator.md)
- [Scale a TiDB Cluster](scale-a-tidb-cluster.md)
- [Backup and Restore](backup-restore-overview.md)
- [Maintain Kubernetes Nodes](maintain-a-kubernetes-node.md)
- [Use Automatic Failover](use-auto-failover.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Reference</ColumnTitle>

- [TiDB Scheduler](tidb-scheduler.md)
- [API Docs](https://github.com/pingcap/tidb-operator/blob/master/docs/api-references/docs.md)
- [Use tkctl](use-tkctl.md)
- [Configure TiDB Binlog Drainer](configure-tidb-binlog-drainer.md)

</NavColumn>

</NavColumns>
