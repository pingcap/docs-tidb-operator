---
title: TiDB in Kubernetes Documentation
summary: Learn about TiDB in Kubernetes documentation.
---

# TiDB in Kubernetes Documentation

[TiDB Operator](https://github.com/pingcap/tidb-operator) is an automatic operation system for TiDB clusters in Kubernetes. It provides a full management life-cycle for TiDB including deployment, upgrades, scaling, backup, fail-over, and configuration changes. With TiDB Operator, TiDB can run seamlessly in the Kubernetes clusters deployed on a public or private cloud.

TiDB Operator provides several ways to deploy TiDB clusters in Kubernetes:

+ For test environment:

    - [kind](deploy-tidb-from-kubernetes-kind.md): Deploy TiDB clusters in local Kubernetes using kind
    - [Minikube](deploy-tidb-from-kubernetes-minikube.md): Deploy TiDB clusters in a local Minikube environment using TiDB Operator
    - [GKE](deploy-tidb-from-kubernetes-gke.md): Deploy TiDB clusters on GKE using TiDB Operator

+ For production environment:

    + On public cloud:
        - [Deploy TiDB on AWS EKS](deploy-on-aws-eks.md)
        - [Deploy TiDB on GCP GKE (beta)](deploy-on-gcp-gke.md)
        - [Deploy TiDB on Alibaba Cloud ACK](deploy-on-alibaba-cloud.md)

    - In an existing Kubernetes cluster:

        First install TiDB Operator in a Kubernetes cluster according to [Deploy TiDB Operator in Kubernetes](deploy-tidb-operator.md), then deploy your TiDB clusters according to [Deploy TiDB in General Kubernetes](deploy-on-general-kubernetes.md).

        You also need to adjust the configuration of the Kubernetes cluster based on [Prerequisites for TiDB in Kubernetes](prerequisites.md) and configure the local PV for your Kubernetes cluster to achieve low latency of local storage for TiKV according to [Local PV Configuration](configure-storage-class.md#local-pv-configuration).

Before deploying TiDB on any of the above two environments, you can always refer to [TiDB Cluster Configuration Document](configure-a-tidb-cluster.md) to customize TiDB configurations.

After the deployment is complete, see the following documents to use, operate, and maintain TiDB clusters in Kubernetes:

+ [Access the TiDB Cluster](access-tidb.md)
+ [Scale TiDB Cluster](scale-a-tidb-cluster.md)
+ [Upgrade TiDB Cluster](upgrade-a-tidb-cluster.md#upgrade-the-version-of-tidb-cluster)
+ [Change the Configuration of TiDB Cluster](upgrade-a-tidb-cluster.md#change-the-configuration-of-tidb-cluster)
+ [Backup and Restore](backup-and-restore.md)
+ [Automatic Failover](use-auto-failover.md)
+ [Monitor a TiDB Cluster in Kubernetes](monitor.md)
+ [Collect TiDB Logs in Kubernetes](collect-tidb-logs.md)
+ [Maintain Kubernetes Nodes that Hold the TiDB Cluster](maintain-a-kubernetes-node.md)

When a problem occurs and the cluster needs diagnosis, you can:

+ See [TiDB FAQs in Kubernetes](faq.md) for any available solution;
+ See [Troubleshoot TiDB in Kubernetes](troubleshoot.md) to shoot troubles.

TiDB in Kubernetes provides a dedicated command-line tool `tkctl` for cluster management and auxiliary diagnostics. Meanwhile, some of TiDB's tools are used differently in Kubernetes. You can:

+ Use `tkctl` according to [`tkctl` Guide](use-tkctl.md );
+ See [Tools in Kubernetes](tidb-toolkit.md) to understand how TiDB tools are used in Kubernetes.

Finally, when a new version of TiDB Operator is released, you can refer to [Upgrade TiDB Operator](upgrade-tidb-operator.md) to upgrade to the latest version.
