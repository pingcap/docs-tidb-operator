# TiDB in Kubernetes Documentation

<!-- markdownlint-disable MD007 -->
<!-- markdownlint-disable MD032 -->

## TOC

- [About TiDB Operator](tidb-operator-overview.md)
+ Benchmark
  - [Sysbench](benchmark-sysbench.md)
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
  - [Deploy TiDB Binlog](deploy-tidb-binlog.md)
+ Configure
  - [Initialize a Cluster](initialize-a-cluster.md)
  - [Configure a TiDB Cluster](configure-a-tidb-cluster.md)
  - [Configure Backup](configure-backup.md)
  - [Configure Storage Class](configure-storage-class.md)
  - [Configure TiDB Binlog Drainer](configure-tidb-binlog-drainer.md)
- [Monitor](monitor-a-tidb-cluster.md)
+ Maintain
  - [Destroy a TiDB Cluster](destroy-a-tidb-cluster.md)
  - [Restart a TiDB Cluster](restart-a-tidb-cluster.md)
  - [Maintain a Hosting Kubernetes Node](maintain-a-kubernetes-node.md)
  + Backup and Restore
    - [Backup and Restore](backup-and-restore-using-helm-charts.md)
    - [Restore Data with TiDB Lightning](restore-data-using-tidb-lightning.md)
  - [Collect TiDB Logs](collect-tidb-logs.md)
  - [Enable Automatic Failover](use-auto-failover.md)
<<<<<<< HEAD
- [Scale](scale-a-tidb-cluster.md)
=======
  - [Enable Admission Controller](enable-admission-webhook.md)
  - [Use PD Recover to Recover the PD Cluster](pd-recover.md)
+ Scale
  - [Scale](scale-a-tidb-cluster.md)
  - [Enable Auto-scaling](enable-tidb-cluster-auto-scaling.md)
+ Backup and Restore
  - [Use Helm Charts](backup-and-restore-using-helm-charts.md)
  + Use CRDs
    - [Back up Data to GCS Using Mydumper](backup-to-gcs.md)
    - [Restore Data from GCS Using TiDB Lightning](restore-from-gcs.md)
    - [Back up Data to S3-Compatible Storage Using Mydumper](backup-to-s3.md)
    - [Restore Data from S3-Compatible Storage Using TiDB Lightning](restore-from-s3.md)
    - [Back up Data to S3-Compatible Storage Using BR](backup-to-aws-s3-using-br.md)
    - [Restore Data from S3-Compatible Storage Using BR](restore-from-aws-s3-using-br.md)
  - [Restore Data Using TiDB Lightning](restore-data-using-tidb-lightning.md)
>>>>>>> bcac7ce... en: add pd-recover doc (#250)
+ Upgrade
  - [TiDB Cluster](upgrade-a-tidb-cluster.md)
  - [TiDB Operator](upgrade-tidb-operator.md)
+ Tools
  - [tkctl](use-tkctl.md)
  - [TiDB Toolkit](tidb-toolkit.md)
+ Components
  - [TiDB Scheduler](tidb-scheduler.md)
- [Troubleshoot](troubleshoot.md)
- [FAQs](faq.md)
