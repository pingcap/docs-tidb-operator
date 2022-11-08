---
title: Restore a TiDB Cluster from EBS Volume Snapshots
summary: Learn how to restore backup metadata and EBS volume snapshots from S3 storage to a TiDB cluster.
---

# Restore a TiDB Cluster from EBS Volume Snapshots

> **Warning:**
>
> This feature is still experimental. It is NOT recommended that you use it in the production environment.

This document describes how to restore backup data in AWS EBS snapshots from S3 storage to a TiDB cluster.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data. The backup data based on AWS EBS snapshots contains two parts, the snapshots of the TiDB cluster data volumes, and the backup metadata of the snapshots and the cluster.

## Requirements

- Snapshot restore is applicable to TiDB Operator v1.4.0 or above, and TiDB v6.3.0 or above.
- Snapshot restore only supports restoring to a cluster with the same number of TiKV nodes and volumes configuration. That is, the number of TiKV nodes and volume configurations is identical between the restore cluster and backup cluster.
- Snapshot restore is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.

## Step 1. Set up the environment for EBS volume snapshot restore

Before using TiDB Operator to restore backup metadata and EBS snapshots from S3 storage to TiDB, prepare the restore environment by following the steps below:

1. Download the file [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml).

2. Create the RBAC-related resources required for the restore in the `test2` namespace by running the following command:

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

3. Grant permissions to access remote storage.

    To restore data from Amazon S3, you need to grant permissions to remote storage. Three ways are available. See [AWS account permissions](grant-permissions-to-remote-storage.md#aws-account-permissions).

## Step 2. Prepare the restore cluster

Deploy a cluster to which you want to restore data. See [Deploy TiDB on AWS EKS](deploy-on-aws-eks.md).

Add the `recoveryMode: true` field to spec and run the following command to create the resources required for the restore in the `test2` namespace:

```shell
kubectl apply -f tidb-cluster.yaml -n test2
```

## Step 3. Restore backup data to the TiDB cluster

Based on the authorization method you selected in [step 1](#step-1-set-up-the-environment-for-ebs-volume-snapshot-restore) to grant remote storage access, you can restore data to TiDB using any of the following methods accordingly:

+ Method 1: If you grant permissions by accessKey and secretKey, you can create the `Restore` CR as follows:

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    The `restore-aws-s3.yaml` file has the following content:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
    spec:
      br:
        cluster: demo2
        clusterNamespace: test2
        backupType: full
        restoreMode: volume-snapshot
        # logLevel: info
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ Method 2: If you grant permissions by associating Pod with IAM, you can create the `Restore` CR as follows:

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    The `restore-aws-s3.yaml` file has the following content:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      br:
        cluster: demo2
        sendCredToTikv: false
        clusterNamespace: test2
        backupType: full
        restoreMode: volume-snapshot
        # logLevel: info
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ Method 3: If you grant permissions by associating ServiceAccount with IAM, you can create the `Restore` CR as follows:

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    The `restore-aws-s3.yaml` file has the following content:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
    spec:
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo2
        sendCredToTikv: false
        clusterNamespace: test2
        backupType: full
        restoreMode: volume-snapshot
        # logLevel: info
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

When configuring `restore-aws-s3.yaml`, note the following:

- For detailed descriptions of the `restoreMode` field, see [BR fields](backup-restore-cr.md#br-fields).
- For storage configurations of S3-compatible storage, see [S3 storage fields](backup-restore-cr.md#s3-storage-fields).
- Some parameters in `.spec.br` are optional, such as `logLevel`. You can decide whether to configure them based on your needs.

After creating the `Restore` CR, you can check the restore status using the following command:

```shell
kubectl get rt -n test2 -o wide
```

## Troubleshooting

If you encounter any problem during the restore process, see [Common Deployment Failures of TiDB on Kubernetes](deploy-failures.md).
