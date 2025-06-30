---
title: Restore Data from S3-Compatible Storage Using BR
summary: Learn how to restore data from Amazon S3-compatible storage using BR.
---

# Restore Data from S3-Compatible Storage Using BR

This document describes how to restore the backup data stored in S3-compatible storages to a TiDB cluster on Kubernetes, including two restoration methods:

- Full restoration. This method takes the backup data of snapshot backup and restores a TiDB cluster to the time point of the snapshot backup.
- Point-in-time recovery (PITR). This method takes the backup data of both snapshot backup and log backup and restores a TiDB cluster to any point in time.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

PITR allows you to restore a new TiDB cluster to any point in time of the backup cluster. To use PITR, you need the backup data of snapshot backup and log backup. During the restoration, the snapshot backup data is first restored to the TiDB cluster, and then the log backup data between the snapshot backup time point and the specified point in time is restored to the TiDB cluster.

> **Note:**
>
> - BR is only applicable to TiDB v3.1 or later releases.
> - PITR is only applicable to TiDB v6.3 or later releases.
> - Data restored by BR cannot be replicated to a downstream cluster, because BR directly imports SST and LOG files to TiDB and the downstream cluster currently cannot access the upstream SST and LOG files.

## Full restoration

This document provides an example about how to restore the backup data from the `spec.s3.prefix` folder of the `spec.s3.bucket` bucket on Amazon S3 to the `demo2` TiDB cluster in the `test1` namespace. The following are the detailed steps.

### Prerequisites: Complete the snapshot backup

In this example, the `my-full-backup-folder` folder in the `my-bucket` bucket of Amazon S3 stores the snapshot backup data. For steps of performing snapshot backup, refer to [Back up Data to S3 Using BR](backup-to-aws-s3-using-br.md).

### Step 1: Prepare the restore environment

Before restoring backup data on an S3-compatible storage to TiDB using BR, take the following steps to prepare the restore environment:

> **Note:**
>
> - BR uses a fixed ServiceAccount name that must be `tidb-backup-manager`.
> - Starting from TiDB Operator v2, the `apiGroup` for resources such as `Backup` and `Restore` changes from `pingcap.com` to `br.pingcap.com`.

1. Save the following content as the `backup-rbac.yaml` file to create the required role-based access control (RBAC) resources:

    ```yaml
    ---
    kind: Role
    apiVersion: rbac.authorization.k8s.io/v1
    metadata:
      name: tidb-backup-manager
      labels:
        app.kubernetes.io/component: tidb-backup-manager
    rules:
    - apiGroups: [""]
      resources: ["events"]
      verbs: ["*"]
    - apiGroups: ["br.pingcap.com"]
      resources: ["backups", "restores"]
      verbs: ["get", "watch", "list", "update"]

    ---
    kind: ServiceAccount
    apiVersion: v1
    metadata:
      name: tidb-backup-manager

    ---
    kind: RoleBinding
    apiVersion: rbac.authorization.k8s.io/v1
    metadata:
      name: tidb-backup-manager
      labels:
        app.kubernetes.io/component: tidb-backup-manager
    subjects:
    - kind: ServiceAccount
      name: tidb-backup-manager
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: Role
      name: tidb-backup-manager
    ```

2. Execute the following command to create the RBAC resources in the `test1` namespace:

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

3. Grant permissions to the remote storage for the `test1` namespace:

    - If you are using Amazon S3 to back up your cluster, you can grant permissions in three methods. For more information, see [AWS account permissions](grant-permissions-to-remote-storage.md#grant-permissions-to-an-aws-account).
    - If you are using other S3-compatible storage (such as Ceph and MinIO) to back up your cluster, you can grant permissions by [using AccessKey and SecretKey](grant-permissions-to-remote-storage.md#grant-permissions-by-accesskey-and-secretkey).

### Step 2: Restore the backup data to a TiDB cluster

Depending on which method you choose to grant permissions to the remote storage when preparing the restore environment, you can restore the data by doing one of the following:

+ Method 1: If you grant permissions by importing AccessKey and SecretKey, create the `Restore` CR to restore cluster data as follows:

    ```shell
    kubectl apply -f restore-full-s3.yaml
    ```

    The content of `restore-full-s3.yaml` is as follows:

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test1
    spec:
      br:
        cluster: demo2
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # sendCredToTikv: true
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-full-backup-folder
    ```

+ Method 2: If you grant permissions by associating IAM with Pod, create the `Restore` CR to restore cluster data as follows:

    ```shell
    kubectl apply -f restore-full-s3.yaml
    ```

    The content of `restore-full-s3.yaml` is as follows:

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test1
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      br:
        cluster: demo2
        sendCredToTikv: false
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-full-backup-folder
    ```

+ Method 3: If you grant permissions by associating IAM with ServiceAccount, create the `Restore` CR to restore cluster data as follows:

    ```shell
    kubectl apply -f restore-full-s3.yaml
    ```

    The content of `restore-full-s3.yaml` is as follows:

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test1
    spec:
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo2
        sendCredToTikv: false
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-full-backup-folder
    ```

When configuring `restore-full-s3.yaml`, note the following:

- For more information about S3-compatible storage configuration, refer to [S3 storage fields](backup-restore-cr.md#s3-storage-fields).
- Some parameters in `.spec.br` are optional, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, `timeAgo`, and `sendCredToTikv`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
- For v4.0.8 or a later version, BR can automatically adjust `tikv_gc_life_time`. You do not need to configure `spec.to` fields in the `Restore` CR.
- For more information about the `Restore` CR fields, refer to [Restore CR fields](backup-restore-cr.md#restore-cr-fields).

After creating the `Restore` CR, execute the following command to check the restore status:

```shell
kubectl get restore -n test1 -o wide
```

```
NAME               STATUS     ...
demo2-restore-s3   Complete   ...
```

## Point-in-time recovery

This section provides an example about how to perform point-in-time recovery (PITR) in a `demo3` cluster in the `test1` namespace. PITR takes two steps:

1. Restore the cluster to the time point of the snapshot backup using the snapshot backup data in the `spec.pitrFullBackupStorageProvider.s3.prefix` folder of the `spec.pitrFullBackupStorageProvider.s3.bucket` bucket.
2. Restore the cluster to any point in time using the log backup data in the `spec.s3.prefix` folder of the `spec.s3.bucket` bucket.

The detailed steps are as follows.

### Prerequisites: Complete data backup

In this example, the `my-bucket` bucket of Amazon S3 stores the following two types of backup data:

- The snapshot backup data generated during the **log backup**, stored in the `my-full-backup-folder-pitr` folder.
- The log backup data, stored in the `my-log-backup-folder-pitr` folder.

For detailed steps of how to perform data backup, refer to [Back up data to Azure Blob Storage](backup-to-aws-s3-using-br.md).

> **Note:**
>
> The specified restoration time point must be between the snapshot backup time point and the log backup `checkpoint-ts`.

### Step 1: Prepare the restoration environment

For more information, see [Step 1: Prepare the restore environment](#step-1-prepare-the-restore-environment).

### Step 2: Restore the backup data to a TiDB cluster

The example in this section restores the snapshot backup data to the cluster. The specified restoration time point must be between [the time point of snapshot backup](backup-to-aws-s3-using-br.md#view-the-snapshot-backup-status) and the [`Log Checkpoint Ts` of log backup](backup-to-aws-s3-using-br.md#view-the-log-backup-status). PITR grants permissions to remote storages in the same way as snapshot backup. The example in this section grants permissions by using AccessKey and SecretKey. The detailed steps are as follows:

1. Create a `Restore` CR named `demo3-restore-s3` in the `restore-test` namespace and specify the restoration time point as `2022-10-10T17:21:00+08:00`:

    ```shell
    kubectl apply -f restore-point-s3.yaml
    ```

    The content of `restore-point-s3.yaml` is as follows:

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo3-restore-s3
      namespace: test1
    spec:
      restoreMode: pitr
      br:
        cluster: demo3
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-log-backup-folder-pitr
      pitrRestoredTs: "2022-10-10T17:21:00+08:00"
      pitrFullBackupStorageProvider:
        s3:
          provider: aws
          region: us-west-1
          bucket: my-bucket
          prefix: my-full-backup-folder-pitr
    ```

    When you configure `restore-point-s3.yaml`, note the following:

    - `spec.restoreMode`: when you perform PITR, set this field to `pitr`. The default value of this field is `snapshot`, which means snapshot backup.

2. Wait for the restoration operation to complete:

    ```shell
    kubectl get jobs -n test1
    ```

    ```
    NAME                       COMPLETIONS   ...
    restore-demo3-restore-s3   1/1           ...
    ```

    You can also check the restoration status by using the following command:

    ```shell
    kubectl get restore -n test1 -o wide
    ```

    ```
    NAME               STATUS     ...
    demo3-restore-s3   Complete   ...
    ```

## Troubleshooting

If you encounter any problem during the restore process, refer to [Common Deployment Failures](deploy-failures.md).
