---
title: Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots
summary: Learn how to back up TiDB cluster data across multiple Kubernetes to S3 based on EBS volume snapshots using BR Federation Manager.
---

# Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots

This document describes how to back up the data of a TiDB cluster deployed across multiple AWS Kubernetes to AWS storage based on EBS volume snapshots.

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in BR Federation Manager and TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to get the backup data of the TiDB cluster, and then send the data to the AWS storage. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Recommended scenarios and limitations

### Recommended scenarios

If you have the following requirements when backing up TiDB cluster data, you can use TiDB Operator to back up the data by volume snapshots and metadata to AWS S3:

- Minimize the impact of backup, for example, to keep the impact on QPS and transaction latency less than 5%, and to occupy no cluster CPU and memory.
- Back up and restore data in a short time. For example, finish backup within 1 hour and restore in 2 hours.

If you have any other requirements, select an appropriate backup method based on [Backup and Restore Overview](backup-restore-overview.md).

### Limitations

- Snapshot backup is applicable to TiDB Operator v1.5.0 or above, and TiDB v6.5.3 or above.
- To use this backup method, the TiDB cluster must be deployed on AWS EC2 and uses AWS EBS volumes.
- This backup method is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.

> **Note:**
>
> - After you upgrade the TiDB cluster from an earlier version to v6.5.0+, you might find the volume snapshot backup does not work. To address this issue, see [Backup failed after an upgrade of the TiDB cluster](backup-restore-faq.md#backup-failed-after-an-upgrade-of-the-tidb-cluster).
> - To perform volume snapshot restore, ensure that the TiKV configuration during restore is consistent with the configuration during backup. To check consistency, download the `backupmeta` file from the backup file stored in Amazon S3, and check the `kubernetes.crd_tidb_cluster.spec` field. If this field is inconsistent, you can modify the TiKV configuration by referring to [Configure a TiDB Cluster on Kubernetes](configure-a-tidb-cluster.md).
> - If [Encryption at Rest](https://docs.pingcap.com/tidb/stable/encryption-at-rest) is enabled for TiKV KMS, ensure that the master key is enabled for AWS KMS during restore.

## Backup process

You can either fully or incrementally back up snapshots based on AWS EBS volumes. The first backup of a node is full, and subsequent backups are incremental.
Snapshot backup is defined by a customized `VolumeBackup` custom resource (CR) object. BR Federation Manager completes the backup task based on this object.

### Step 1. Set up the environment for EBS volume snapshot backup in every data plane

**You must execute the steps below in every data plane**.

1. Download the file [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) to the backup server.

2. Supposed that you deploy the TiDB cluster in `${namespace}`, create the RBAC-related resources required for the backup in this namespace by running the following command.

    ```shell
    kubectl apply -f backup-rbac.yaml -n ${namespace}
    ```

3. Grant permissions to access remote storage.

   To back up cluster data and save snapshot metadata to Amazon S3, you need to grant permissions to remote storage. Three ways are available. See [AWS account authorization](grant-permissions-to-remote-storage.md#aws-account-permissions).

### Step 2. Back up data to S3 storage

**You must execute the steps below in the control plane**. Based on the authorization method you selected in the previous step to grant remote storage access, you can back up data to S3 storage using any of the following methods accordingly:

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
    ```
</div>
</SimpleTab>

> **Note:**
> 
> The value of `spec.clusters.k8sClusterName` field in `VolumeBackup` CR should be same as the **context name** of the kubeconfig which the br-federation-manager uses.

After creating the `VolumeBackup` CR, BR Federation Manager automatically starts the backup process in every data plane. You can check the volume backup status using the following command:

```shell
kubectl get vbk -n ${namespace} -o wide
```

After the volume backup complete, you can get the information of all the data planes in `status.backups` field, which can be used in volume restore. You can get it using the following command:

```shell
kubectl get vbk ${backup-name} -n ${namespace} -o yaml
```

Then you can get information as follows.

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

## Delete the `VolumeBackup` CR

You can delete the `VolumeBackup` CR by running the following commands:

```shell
kubectl delete backup ${backup-name} -n ${namespace}
```

If you set the value of `spec.template.cleanPolicy` to `Delete`, when you delete the CR, BR Federation Manager will clean up the backup file and the volume snapshots on AWS.

# Scheduled volume backup across Kubernetes Clusters

You can set a backup policy to perform scheduled backups of the TiDB cluster, and set a backup retention policy to avoid excessive backup items. A scheduled snapshot backup is described by a custom `VolumeBackupSchedule` CR object. A volume backup is triggered at each backup time point. Its underlying implementation is the ad-hoc volume backup.

## Perform a scheduled volume backup

Perform a scheduled volume backup by doing one of the following:

+ Create the `VolumeBackupSchedule` CR, and back up cluster data as described below:

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
            backup:
          - k8sClusterName: {k8s-name2}
            tcName: {tc-name2}
            tcNamespace: {tc-namespace2} 
          - ... # other clusters
        template:
          br:
            sendCredToTikv: false
            cleanPolicy: Delete
            resources: {}
          s3:
            provider: aws
            region: {region-name}
            bucket: {bucket-name}
            prefix: {backup-path}
          serviceAccount: tidb-backup-manager
          toolImage: {br-image}
    ```
