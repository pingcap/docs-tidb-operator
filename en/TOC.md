# TiDB in Kubernetes Documentation

<!-- markdownlint-disable MD007 -->
<!-- markdownlint-disable MD032 -->

## TOC

- [About TiDB Operator](tidb-operator-overview.md)
+ Get Started
  - [kind](deploy-tidb-from-kubernetes-kind.md)
  - [GKE](deploy-tidb-from-kubernetes-gke.md)
  - [Minikube](deploy-tidb-from-kubernetes-minikube.md)
+ Deploy
  - [Prerequisites](prerequisites.md)
  - [TiDB Operator](deploy-tidb-operator.md)
  - [TiDB in General Kubernetes](deploy-on-general-kubernetes.md)
  - [TiDB in AWS EKS](deploy-on-aws-eks.md)
  - [TiDB in GCP GKE](deploy-on-gcp-gke.md)
  - [TiDB in Alibaba Cloud ACK](deploy-on-alibaba-cloud.md)
  - [Access TiDB in Kubernetes](access-tidb.md)
+ Configure
  - [Configure Storage Class](configure-storage-class.md)
  - [Configure Resource and Disaster Recovery](configure-a-tidb-cluster.md)
  - [Initialize a Cluster](initialize-a-cluster.md)
  - [Configure TiDB Binlog Drainer](configure-tidb-binlog-drainer.md)
  - [Configure tidb-cluster Chart](tidb-cluster-chart-config.md)
  - [Configure tidb-backup Chart](configure-backup.md)
- [Monitor](monitor-a-tidb-cluster.md)
+ Maintain
  - [Destroy a TiDB cluster](destroy-a-tidb-cluster.md)
  - [Restart a TiDB Cluster](restart-a-tidb-cluster.md)
  - [Maintain a Hosting Kubernetes Node](maintain-a-kubernetes-node.md)
  - [Collect TiDB Logs](collect-tidb-logs.md)
  - [Maintain TiDB Binlog](maintain-tidb-binlog.md)
  - [Enable Automatic Failover](use-auto-failover.md)
- [Scale](scale-a-tidb-cluster.md)
+ Backup and Restore
  - [Use Helm Charts](backup-and-restore-using-helm-charts.md)
  + Use CRDs
    - [Back up Data to GCS](backup-to-gcs.md)
    - [Restore Data from GCS](restore-from-gcs.md)
    - [Back up Data to S3-Compatible Storage using Mydumper](backup-to-s3.md)
    - [Restore Data from S3-Compatible Storage using Loader](restore-from-s3.md)
    - [Back up Data to S3-Compatible Storage using BR](backup-to-aws-s3-using-br.md)
    - [Restore Data from S3-Compatible Storage using BR](restore-from-aws-s3-using-br.md)
  - [Restore Data with TiDB Lightning](restore-data-using-tidb-lightning.md)
+ Upgrade
  - [TiDB Cluster](upgrade-a-tidb-cluster.md)
  - [TiDB Operator](upgrade-tidb-operator.md)
+ Tools
  - [tkctl](use-tkctl.md)
  - [TiDB Toolkit](tidb-toolkit.md)
- [Troubleshoot](troubleshoot.md)
- [FAQs](faq.md)
