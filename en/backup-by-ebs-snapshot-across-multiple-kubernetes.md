---
title: Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots
summary: Learn how to back up TiDB cluster data across multiple Kubernetes to S3 based on EBS volume snapshots using BR Federation.
---

# Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots

This document describes how to back up the data of a TiDB cluster deployed across multiple AWS Kubernetes clusters to AWS storage using EBS volume snapshots.

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in [BR Federation](br-federation-architecture.md#br-federation-architecture-and-processes) and TiDB Operator. [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) (Backup & Restore) is a command-line tool for distributed backup and recovery of the TiDB cluster data. For the underlying implementation, BR gets the backup data of the TiDB cluster, and then sends the data to the AWS storage.

> **Note**
>
> Before you back up data, make sure that you have [deployed BR Federation](deploy-br-federation.md).

## Usage scenarios

If you have the following requirements when backing up TiDB cluster data, you can use TiDB Operator to back up the data using volume snapshots and metadata to Amazon S3:

- Minimize the impact of backup, such as keeping the impact on QPS and transaction latency less than 5%, and not utilizing cluster CPU and memory.
- Back up and restore data in a short period of time. For example, completing a backup within 1 hour and restore it within 2 hours.

If you have any other requirements, refer to [Backup and Restore Overview](backup-restore-overview.md) and select an appropriate backup method.

## Prerequisites

Storage blocks on volumes that were created from snapshots must be initialized (pulled down from Amazon S3 and written to the volume) before you can access the block. This preliminary action takes time and can cause a significant increase in the latency of an I/O operation the first time each block is accessed. Volume performance is achieved after all blocks have been downloaded and written to the volume.

According to AWS documentation, the EBS volume restored from snapshots might have high latency before it is initialized. This can impact the performance of a restored TiDB cluster. See details in [Create a volume from a snapshot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-creating-volume.html#ebs-create-volume-from-snapshot).

To initialize the restored volume more efficiently, it is recommended to **separate WAL and raft log into a dedicated small volume apart from TiKV data**. By fully initializing the volume of WAL and raft log separately, we can enhance write performance for a restored TiDB cluster.

## Limitations

- Snapshot backup is applicable to TiDB Operator v1.5.1 or later versions, and TiDB v6.5.4 or later versions.
- For TiKV configuration, do not set `resolved-ts.enable` to `false`, and do not set `raftstore.report-min-resolved-ts-interval` to `"0s"`. Otherwise, it can lead to backup failure.
- For PD configuration, do not set `pd-server.min-resolved-ts-persistence-interval` to `"0s"`. Otherwise, it can lead to backup failure.
- To use this backup method, the TiDB cluster must be deployed on AWS EC2 and use AWS EBS volumes.
- This backup method is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.

> **Note:**
>
> - To perform volume snapshot restore, ensure that the TiKV configuration during restore is consistent with the configuration used during backup.
>     - To check consistency, download the `backupmeta` file from the backup file stored in Amazon S3, and check the `kubernetes.crd_tidb_cluster.spec` field.
>     - If this field is inconsistent, you can modify the TiKV configuration by referring to [Configure a TiDB Cluster on Kubernetes](configure-a-tidb-cluster.md).
> - If [Encryption at Rest](https://docs.pingcap.com/tidb/stable/encryption-at-rest) is enabled for TiKV KMS, ensure that the master key is enabled for AWS KMS during restore.

## Ad-hoc backup

You can either fully or incrementally back up snapshots based on AWS EBS volumes. The initial backup of a node is full backup, while subsequent backups are incremental backup.

Snapshot backup is defined in a customized `VolumeBackup` custom resource (CR) object. The BR Federation completes the backup task according to the specifications in this object.

### Step 1. Set up the environment for EBS volume snapshot backup in every data plane

**You must execute the following steps in every data plane**.

1. Download the [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/v1.6.1/manifests/backup/backup-rbac.yaml) file to the backup server.

2. If you have deployed the TiDB cluster in `${namespace}`, create the RBAC-related resources required for the backup in this namespace by running the following command:

    ```shell
    kubectl apply -f backup-rbac.yaml -n ${namespace}
    ```

3. Grant permissions to access remote storage.

    To back up cluster data and save snapshot metadata to Amazon S3, you need to grant permissions to remote storage. Refer to [AWS account authorization](grant-permissions-to-remote-storage.md#aws-account-permissions) for the three available methods.

### Step 2. Back up data to S3 storage

**You must execute the following steps in the control plane**.

Depending on the authorization method you choose in the previous step for granting remote storage access, you can back up data by EBS snapshots using any of the following methods accordingly:

<SimpleTab>
<div label="AK/SK">

If you grant permissions by accessKey and secretKey, you can create the `VolumeBackup` CR as follows:

```shell
kubectl apply -f backup-fed.yaml
```

The `backup-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackup
metadata:
  name: ${backup-name}
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: true
    s3:
      provider: aws
      secretName: s3-secret
      region: ${region-name}
      bucket: ${bucket-name}
      prefix: ${backup-path}
    toolImage: ${br-image}
    cleanPolicy: Delete
    calcSizeLevel: {snapshot-size-calculation-level}
```

</div>

<div label="IAM role with Pod">

If you grant permissions by associating Pod with IAM, you can create the `VolumeBackup` CR as follows:

```shell
kubectl apply -f backup-fed.yaml
```

The `backup-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackup
metadata:
  name: ${backup-name}
  annotations:
    iam.amazonaws.com/role: arn:aws:iam::123456789012:role/role-name
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: false
    s3:
      provider: aws
      region: ${region-name}
      bucket: ${bucket-name}
      prefix: ${backup-path}
    toolImage: ${br-image}
    cleanPolicy: Delete
    calcSizeLevel: {snapshot-size-calculation-level}
```

</div>

<div label="IAM role with ServiceAccount">

If you grant permissions by associating ServiceAccount with IAM, you can create the `VolumeBackup` CR as follows:

```shell
kubectl apply -f backup-fed.yaml
```

The `backup-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackup
metadata:
  name: ${backup-name}
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: false
    s3:
      provider: aws
      region: ${region-name}
      bucket: ${bucket-name}
      prefix: ${backup-path}
    toolImage: ${br-image}
    serviceAccount: tidb-backup-manager
    cleanPolicy: Delete
    calcSizeLevel: {snapshot-size-calculation-level}
```

</div>
</SimpleTab>

> **Note:**
>
> The value of `spec.clusters.k8sClusterName` field in `VolumeBackup` CR must be the same as the **context name** of the kubeconfig used by the br-federation-manager.

### Step 3. View the backup status

After creating the `VolumeBackup` CR, the BR Federation automatically starts the backup process in each data plane.

To check the volume backup status, use the following command:

```shell
kubectl get vbk -n ${namespace} -o wide
```

Once the volume backup is complete, you can get the information of all the data planes in the `status.backups` field. This information can be used for volume restore.

To obtain the information, use the following command:

```shell
kubectl get vbk ${backup-name} -n ${namespace} -o yaml
```

The information is as follows:

```yaml
status:
  backups:
  - backupName: fed-{backup-name}-{k8s-name1}
    backupPath: s3://{bucket-name}/{backup-path}-{k8s-name1}
    commitTs: "ts1"
    k8sClusterName: {k8s-name1}
    tcName: {tc-name1}
    tcNamespace: {tc-namespace1}
  - backupName: fed-{backup-name}-{k8s-name2}
    backupPath: s3://{bucket-name}/{backup-path}-{k8s-name2}
    commitTs: "ts2"
    k8sClusterName: {k8s-name2}
    tcName: {tc-name2}
    tcNamespace: {tc-namespace2}
  - ... # other backups
```

### Delete the `VolumeBackup` CR

If you set `spec.template.cleanPolicy` to `Delete`, when you delete the `VolumeBackup` CR, the BR Federation will clean up the backup file and the volume snapshots on AWS.

To delete the `VolumeBackup` CR, run the following commands:

```shell
kubectl delete backup ${backup-name} -n ${namespace}
```

## Scheduled volume backup

To ensure regular backups of the TiDB cluster and prevent an excessive number of backup items, you can set a backup policy and retention policy.

This can be done by creating a `VolumeBackupSchedule` CR object that describes the scheduled snapshot backup. Each backup time point triggers a volume backup. The underlying implementation is the ad-hoc volume backup.

### Perform a scheduled volume backup

**You must execute the following steps in the control plane**.

Depending on the authorization method you choose in the previous step for granting remote storage access, perform a scheduled volume backup by doing one of the following:

<SimpleTab>
<div label="AK/SK">

If you grant permissions by accessKey and secretKey, Create the `VolumeBackupSchedule` CR, and back up cluster data as described below:

```shell
kubectl apply -f volume-backup-scheduler.yaml
```

The content of `volume-backup-scheduler.yaml` is as follows:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackupSchedule
metadata:
  name: {scheduler-name}
  namespace: {namespace-name}
spec:
  #maxBackups: {number}
  #pause: {bool}
  maxReservedTime: {duration}
  schedule: {cron-expression}
  backupTemplate:
    clusters:
      - k8sClusterName: {k8s-name1}
        tcName: {tc-name1}
        tcNamespace: {tc-namespace1}
      - k8sClusterName: {k8s-name2}
        tcName: {tc-name2}
        tcNamespace: {tc-namespace2}
      - ... # other clusters
    template:
      br:
        sendCredToTikv: true
      s3:
        provider: aws
        secretName: s3-secret
        region: {region-name}
        bucket: {bucket-name}
        prefix: {backup-path}
      toolImage: {br-image}
      cleanPolicy: Delete
      calcSizeLevel: {snapshot-size-calculation-level}
```

</div>

<div label="IAM role with ServiceAccount">

If you grant permissions by associating Pod with IAM, Create the `VolumeBackupSchedule` CR, and back up cluster data as described below:

```shell
kubectl apply -f volume-backup-scheduler.yaml
```

The content of `volume-backup-scheduler.yaml` is as follows:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackupSchedule
metadata:
  name: {scheduler-name}
  namespace: {namespace-name}
  annotations:
     iam.amazonaws.com/role: arn:aws:iam::123456789012:role/role-name
spec:
  #maxBackups: {number}
  #pause: {bool}
  maxReservedTime: {duration}
  schedule: {cron-expression}
  backupTemplate:
    clusters:
      - k8sClusterName: {k8s-name1}
        tcName: {tc-name1}
        tcNamespace: {tc-namespace1}
      - k8sClusterName: {k8s-name2}
        tcName: {tc-name2}
        tcNamespace: {tc-namespace2}
      - ... # other clusters
    template:
      br:
        sendCredToTikv: false
      s3:
        provider: aws
        region: {region-name}
        bucket: {bucket-name}
        prefix: {backup-path}
      toolImage: {br-image}
      cleanPolicy: Delete
      calcSizeLevel: {snapshot-size-calculation-level}
```

</div>

<div label="IAM role with ServiceAccount">

If you grant permissions by associating ServiceAccount with IAM, Create the `VolumeBackupSchedule` CR, and back up cluster data as described below:

```shell
kubectl apply -f volume-backup-scheduler.yaml
```

The content of `volume-backup-scheduler.yaml` is as follows:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackupSchedule
metadata:
  name: {scheduler-name}
  namespace: {namespace-name}
spec:
  #maxBackups: {number}
  #pause: {bool}
  maxReservedTime: {duration}
  schedule: {cron-expression}
  backupTemplate:
    clusters:
      - k8sClusterName: {k8s-name1}
        tcName: {tc-name1}
        tcNamespace: {tc-namespace1}
      - k8sClusterName: {k8s-name2}
        tcName: {tc-name2}
        tcNamespace: {tc-namespace2}
      - ... # other clusters
    template:
      br:
        sendCredToTikv: false
      s3:
        provider: aws
        region: {region-name}
        bucket: {bucket-name}
        prefix: {backup-path}
      serviceAccount: tidb-backup-manager
      toolImage: {br-image}
      cleanPolicy: Delete
      calcSizeLevel: {snapshot-size-calculation-level}
```

</div>
</SimpleTab>
