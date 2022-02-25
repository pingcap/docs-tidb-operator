---
title: TiDB in Kubernetes Documentation
summary: Learn about TiDB in Kubernetes documentation.
aliases: ['/docs/tidb-in-kubernetes/dev/']
---

# TiDB in Kubernetes Documentation

You can use [TiDB Operator](https://github.com/pingcap/tidb-operator) to deploy TiDB clusters in Kubernetes. TiDB Operator is an automatic operation system for TiDB clusters in Kubernetes. It provides full life-cycle management for TiDB including deployment, upgrades, scaling, backup, fail-over, and configuration changes. With TiDB Operator, TiDB can run seamlessly in the Kubernetes clusters deployed on a public or private cloud.

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
- [TiDB Operator Architecture](architecture.md)
- [What's New in v1.3](whats-new-in-v1.3.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Quick Start</ColumnTitle>

- [kind](get-started.md#create-a-kubernetes-cluster-using-kind)
- [Minikube](get-started.md#minikube)
- [GKE](deploy-tidb-from-kubernetes-gke.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Deploy TiDB</ColumnTitle>

- [On Amazon EKS](deploy-on-aws-eks.md)
- [On GCP GKE](deploy-on-gcp-gke.md)
- [On Azure AKS](deploy-on-azure-aks.md)
- [On Alibaba ACK](deploy-on-alibaba-cloud.md)
- [On Self-managed Kubernetes](deploy-on-general-kubernetes.md)
- [Deploy TiFlash to Explore TiDB HTAP](deploy-tiflash.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Secure</ColumnTitle>

- [Enable TLS for the MySQL Client](enable-tls-for-mysql-client.md)
- [Enable TLS between TiDB Components](enable-tls-between-components.md)
- [Enable TLS for TiDB Data Migration](enable-tls-for-dm.md)
- [Replicate Data to TLS-enabled Downstream Services](enable-tls-for-ticdc-sink.md)
- [Renew and Replace the TLS Certificate](renew-tls-certificate.md)
- [Run Containers as a Non-root User](containers-run-as-non-root-user.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Manage</ColumnTitle>

- [Upgrade a TiDB Cluster](upgrade-a-tidb-cluster.md)
- [Upgrade TiDB Operator](upgrade-tidb-operator.md)
- [Scale a TiDB Cluster](scale-a-tidb-cluster.md)
- [Backup and Restore Data](backup-restore-overview.md)
- [Deploy Monitoring and Alerts](monitor-a-tidb-cluster.md)
- [Maintain Kubernetes Nodes](maintain-a-kubernetes-node.md)
- [Use Automatic Failover](use-auto-failover.md)

</NavColumn>

<NavColumn>
<ColumnTitle>Reference</ColumnTitle>

- [TiDB Scheduler](tidb-scheduler.md)
- [API Docs](https://github.com/pingcap/tidb-operator/blob/master/docs/api-references/docs.md)
- [Configure TiDB Binlog Drainer](configure-tidb-binlog-drainer.md)

</NavColumn>

</NavColumns>
