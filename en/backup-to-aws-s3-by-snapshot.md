---
title: Back Up a TiDB Cluster Using EBS Volume Snapshots
summary: Learn how to back up TiDB cluster data to S3 based on EBS volume snapshots using TiDB Operator.
---

# Back Up a TiDB Cluster Using EBS Volume Snapshots

This document describes how to back up a TiDB cluster deployed on AWS Elastic Kubernetes Service (EKS) to S3.

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to get the backup data of the TiDB cluster, and then send the data to the AWS storage. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data. If your TiDB cluster is deployed on AWS EKS and uses EBS volumes, you can use the method described in this document to back up the TiDB cluster.

## Recommended scenarios and limitations

### Recommended scenarios

If you have the following requirements when backing up TiDB cluster data, you can use TiDB Operator to back up the data by volume snapshots and metadata to AWS S3:

- Minimize the impact of backup, for example, to keep the impact on QPS and transaction latency less than 5%, and to occupy no cluster CPU and memory.
- Back up and restore data in a short time. For example, finish backup within 1 hour and restore in 2 hours.

If you have any other requirements, select an appropriate backup method based on [Backup and Restore Overview](backup-restore-overview.md).

### Limitations

- Snapshot backup is applicable to TiDB Operator v1.4.0 or above, and TiDB v6.3.0 or above.
- To use this backup method, the TiDB cluster must be deployed on AWS EKS and uses AWS EBS volumes.
- This backup method is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.

> **Note:**
>
> After you upgrade the TiDB cluster from an earlier version to v6.5.0, you might find the volume snapshot backup does not work. To address this issue, see [Backup failed after an upgrade of the TiDB cluster](backup-restore-faq.md#backup-failed-after-an-upgrade-of-the-tidb-cluster).

## Backup process

You can either fully or incrementally back up snapshots based on AWS EBS volumes. The first backup of a node is full, and subsequent backups are incremental. Snapshot backup is defined by a customized `Backup` custom resource (CR) object. TiDB Operator completes the backup task based on this object. If an error occurs during the backup process, TiDB Operator does not retry automatically. At this time, you need to handle it manually.

The following sections exemplify how to back up data of the TiDB cluster `demo1`. `demo1` is deployed in the `test1` namespace in Kubernetes.

### Step 1. Set up the environment for EBS volume snapshot backup

1. Download the file [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) to the backup server.

2. Create the RBAC-related resources required for the backup in the `test1` namespace by running the following command:

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

3. Grant permissions to access remote storage.

    To back up cluster data and save snapshot metadata to Amazon S3, you need to grant permissions to remote storage. Three ways are available. See [AWS account authorization](grant-permissions-to-remote-storage.md#aws-account-permissions).

### Step 2. Back up data to S3 storage

Based on the authorization method you selected in the previous step to grant remote storage access, you can back up data to S3 storage using any of the following methods accordingly:

+ Method 1: If you grant permissions by accessKey and secretKey, you can create the `Backup` CR as follows:

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    The `backup-aws-s3.yaml` file has the following content:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      backupType: full
      backupMode: volume-snapshot
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ Method 2: If you grant permissions by associating Pod with IAM, you can create the `Backup` CR as follows:

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    The `backup-aws-s3.yaml` file has the following content:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      backupMode: volume-snapshot
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ Method 3: If you grant permissions by associating ServiceAccount with IAM, you can create the `Backup` CR as follows:

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    The `backup-aws-s3.yaml` file has the following content:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      backupType: full
      backupMode: volume-snapshot
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

When configuring `backup-aws-s3.yaml`, note the following:

- To back up data using volume snapshots, you need to set `spec.br.backupMode` to `volume-snapshot`.
- For storage configurations of Amazon S3, see [S3 storage fields](backup-restore-cr.md#s3-storage-fields).
- Some parameters in `.spec.br` are optional, such as `logLevel`. You can decide whether to configure them based on your needs.

After creating the `Backup` CR, TiDB Operator automatically starts the backup process. You can check the backup status using the following command:

```shell
kubectl get bk -n test1 -o wide
```

## Delete the `Backup` CR

After a backup is completed, you might need to delete the `Backup` CR. For details, see [Delete the Backup CR](backup-restore-overview.md#delete-the-backup-cr).

## Troubleshooting

If you encounter any problem during the backup process, see [Common Deployment Failures of TiDB on Kubernetes](deploy-failures.md).
