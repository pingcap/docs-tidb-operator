---
title: Restore Data from S3-Compatible Storage Using BR
summary: Learn how to restore data from Amazon S3-compatible storage using BR.
---

# Restore Data from S3-Compatible Storage Using BR

This document describes how to restore the TiDB cluster data backed up using TiDB Operator in Kubernetes.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Usage Scenarios

After backing up TiDB cluster data to Amazon S3 using BR, if you need to recover the backup SST (key-value pairs) files from Amazon S3 to a TiDB cluster, you can follow steps in this document to restore the data using BR.

> **Note:**
>
> - BR is only applicable to TiDB v3.1 or later releases.
> - Data restored by BR cannot be replicated to a downstream cluster, because BR directly imports SST files to TiDB and the downstream cluster currently cannot access the upstream SST files.

This document provides an example about how to restore the backup data from the `spec.s3.prefix` folder of the `spec.s3.bucket` bucket on Amazon S3 to the `demo2` TiDB cluster in the `test2` namespace. The following are the detailed steps.

## Step 1: Prepare the restore environment

Before restoring backup data on a S3-compatible storage to TiDB using BR, take the following steps to prepare the restore environment:

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test2` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. Grant permissions to the remote storage.

    If the data to be restored is in Amazon S3, you can grant permissions in three methods. For more information, see [AWS account permissions](grant-permissions-to-remote-storage.md#aws-account-permissions).

    If the data to be restored is in other S3-compatible storage (such as Ceph and MinIO), you can grant permissions by [using AccessKey and SecretKey](grant-permissions-to-remote-storage.md#grant-permissions-by-accesskey-and-secretkey).

3. For a TiDB version earlier than v4.0.8, you also need to complete the following preparation steps. For TiDB v4.0.8 or a later version, skip these preparation steps.

    1. Make sure that you have the `SELECT` and `UPDATE` privileges on the `mysql.tidb` table of the target database so that the `Restore` CR can adjust the GC time before and after the restore.

    2. Create the `restore-demo2-tidb-secret` secret to store the account and password to access the TiDB cluster:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=password=${password} --namespace=test2
        ```

## Step 2: Restore the backup data to a TiDB cluster

Depending on which method you choose to grant permissions to the remote storage when preparing the restore environment, you can restore the data by doing one of the following:

+ Method 1: If you grant permissions by importing AccessKey and SecretKey, create the `Restore` CR to restore cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    The content of `restore-aws-s3.yaml` is as follows:

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
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # sendCredToTikv: true
      # # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      # to:
      #   host: ${tidb_host}
      #   port: ${tidb_port}
      #   user: ${tidb_user}
      #   secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ Method 2: If you grant permissions by associating IAM with Pod, create the `Restore` CR to restore cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    The content of `restore-aws-s3.yaml` is as follows:

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
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ Method 3: If you grant permissions by associating IAM with ServiceAccount, create the `Restore` CR to restore cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    The content of `restore-aws-s3.yaml` is as follows:

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
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

When configuring `restore-aws-s3.yaml`, note the following:

- For more information about S3-compatible storage configuration, refer to [S3 storage fields](backup-restore-cr.md#s3-storage-fields).
- Some parameters in `.spec.br` are optional, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, `timeAgo`, and `sendCredToTikv`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
- For v4.0.8 or a later version, BR can automatically adjust `tikv_gc_life_time`. You do not need to configure `spec.to` fields in the `Restore` CR.
- For more information about the `Restore` CR fields, refer to [Restore CR fields](backup-restore-cr.md#restore-cr-fields).

After creating the `Restore` CR, execute the following command to check the restore status:

{{< copyable "shell-regular" >}}

```shell
kubectl get rt -n test2 -o wide
```

## Troubleshooting

If you encounter any problem during the restore process, refer to [Common Deployment Failures](deploy-failures.md).