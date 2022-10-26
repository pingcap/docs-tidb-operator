---
title: Restore Data from Azure Blob Storage Using BR
summary: Learn how to restore data from Azure Blob Storage using BR.
---

# Restore Data from Azure Blob Storage Using BR

This document describes how to restore the backup data stored in Azure Blob Storage to a TiDB cluster in Kubernetes, including two restoration methods:

- Full restoration. This method takes the backup data of snapshot backup and restores a TiDB cluster to the time point of the snapshot backup.
- Point-in-time recovery (PITR). This method takes the backup data of both snapshot backup and log backup and restores a TiDB cluster to any point in time.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

PITR allows you to restore a new TiDB cluster to any point in time of the backup cluster. To use PITR, you need the backup data of snapshot backup and log backup. During the restoration, the snapshot backup data is first restored to the TiDB cluster, and then the log backup data between the snapshot backup time point and the specified point in time is restored to the TiDB cluster.

> **Note:**
>
> - BR is only applicable to TiDB v3.1 or later releases.
> - PITR is only applicable to TiDB v6.2 or later releases.
> - Data restored by BR cannot be replicated to a downstream cluster, because BR directly imports SST and LOG files to TiDB and the downstream cluster currently cannot access the upstream SST and LOG files.

## Full restoration

This section provides an example about how to restore the backup data from the `spec.azblob.prefix` folder of the `spec.azblob.container` bucket on Azure Blob Storage to the `demo2` TiDB cluster in the `test2` namespace. The following are the detailed steps.

### Prerequisites: Complete the snapshot backup

In this example, the `my-full-backup-folder` folder in the `my-container` bucket of Azure Blob Storage stores the snapshot backup data. For steps of performing snapshot backup, refer to [Back up Data to Azure Blob Storage Using BR](backup-to-azblob-using-br.md).

### Step 1: Prepare the restoration environment

Before restoring backup data on Azure Blob Storage to TiDB using BR, take the following steps to prepare the restore environment:

1. Create a namespace for managing restoration. The following example creates a `restore-test` namespace:

    ```shell
    kubectl create namespace restore-test
    ```

2. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `restore-test` namespace:

    ```shell
    kubectl apply -f backup-rbac.yaml -n restore-test
    ```

3. Grant permissions to the remote storage for the `restore-test` namespace. You can grant permissions to Azure Blob Storage by two methods. For details, refer to [Azure account permissions](grant-permissions-to-remote-storage.md#azure-account-permissions). After you grant the permissions, the `restore-test` namespace has a secret object named `azblob-secret` or `azblob-secret-ad`.

    > **Note:**
    >
    > The role owned by the account must have the permission to access blob at least (for example, a [reader](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#reader)).
    >
    > When you create a secret object, you can use a customized name for the object. In this document, the name is `azblob-secret`.

4. For a TiDB version earlier than v4.0.8, you also need to complete the following preparation steps. For TiDB v4.0.8 or a later version, skip these preparation steps.

    1. Make sure that you have the `SELECT` and `UPDATE` privileges on the `mysql.tidb` table of the target database so that the `Restore` CR can adjust the GC time before and after the restore.

    2. Create the `restore-demo2-tidb-secret` secret to store the account and password to access the TiDB cluster:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=password=${password} --namespace=test2
        ```

### Step 2. Restore the backup data to a TiDB cluster

Create a `Restore` CR named `demo2-restore-azblob` in the `restore-test` namespace to restore cluster data as described below:

```shell
kubectl apply -f restore-full-azblob.yaml
```

The content of `restore-full-azblob.yaml` is as follows:

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Restore
metadata:
  name: demo2-restore-azblob
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
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-folder
```

When configuring `restore-azblob.yaml`, note the following:

- For more information about Azure Blob Storage configuration, refer to [Azure Blob Storage fields](backup-restore-cr.md#azure-blob-storage-fields).
- Some parameters in `.spec.br` are optional, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, `timeAgo`, and `sendCredToTikv`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
- `spec.azblob.secretName`: fill in the name of the secret object, such as `azblob-secret`.
- For v4.0.8 or a later version, BR can automatically adjust `tikv_gc_life_time`. You do not need to configure the `spec.to` fields in the `Restore` CR.
- For more information about the `Restore` CR fields, refer to [Restore CR fields](backup-restore-cr.md#restore-cr-fields).

After creating the `Restore` CR, execute the following command to check the restore status:

```shell
kubectl get rt -n test2 -o wide
```

## Point-in-time recovery

This section provides an example about how to perform point-in-time recovery (PITR) in a `demo3` cluster in the `test3` namespace. PITR takes two steps:

1. Restore the cluster to the time point of the snapshot backup using the snapshot backup data in the `spec.pitrFullBackupStorageProvider.azblob.prefix` folder of the `spec.pitrFullBackupStorageProvider.azblob.container` bucket.
2. Restore the cluster to any point in time using the log backup data in the `spec.azblob.prefix` folder of the `spec.azblob.container` bucket.

The detailed steps are as follows.

### Prerequisites: Complete data backup

In this example, the `my-container` bucket of Azure Blob Storage stores the following two types of backup data:

- The snapshot backup data generated during the **log backup**, stored in the `my-full-backup-folder-pitr` folder.
- The log backup data, stored in the `my-log-backup-folder-pitr` folder.

For detailed steps of how to perform data backup, refer to [Back up data to Azure Blob Storage](backup-to-azblob-using-br.md).

> **Note:**
>
> The specified restoration time point must be between the snapshot backup time point and the log backup `checkpoint-ts`.

### Step 1. Prepare the restoration environment

Before restoring backup data on Azure Blob Storage to TiDB using BR, take the following steps to prepare the restoration environment:

1. Create a namespace for managing restoration. The following example creates a `restore-test` namespace:

    ```shell
    kubectl create namespace restore-test
    ```

2. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `restore-test` namespace:

    ```shell
    kubectl apply -f backup-rbac.yaml -n restore-test
    ```

3. Grant permissions to the remote storage for the `restore-test` namespace. You can grant permissions to Azure Blob Storage by two methods. For details, refer to [Azure account permissions](grant-permissions-to-remote-storage.md#azure-account-permissions). After you grant the permissions, the `restore-test` namespace has a secret object named `azblob-secret` or `azblob-secret-ad`.

    > **Note:**
    >
    > The role owned by the account must have the permission to access blob at least (for example, a [reader](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#reader)).
    >
    > When you create a secret object, you can use a customized name for the object. In this document, the name is `azblob-secret`.

### Step 2. Restore the backup data to a TiDB cluster

The example in this section restores the snapshot backup data to the cluster. The specified restoration time point must be between [the time point of snapshot backup](backup-to-azblob-using-br.md#view-the-snapshot-backup-status) and the [`Log Checkpoint Ts` of log backup](backup-to-azblob-using-br.md#view-the-log-backup-status).

The detailed steps are as follows:

1. Create a `Restore` CR named `demo3-restore-azblob` in the `restore-test` namespace and specify the restoration time point as `2022-10-10T17:21:00+08:00`:

    ```shell
    kubectl apply -f restore-point-azblob.yaml
    ```

    The content of `restore-point-azblob.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
    name: demo3-restore-azblob
    namespace: restore-test
    spec:
      restoreMode: pitr
      br:
        cluster: demo3
        clusterNamespace: test3
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-log-backup-folder-pitr
      pitrRestoredTs: "2022-10-10T17:21:00+08:00"
      pitrFullBackupStorageProvider:
        azblob:
          secretName: azblob-secret
          container: my-container
          prefix: my-full-backup-folder-pitr
    ```

2. Wait for the restoration operation to complete:

    ```shell
    kubectl get jobs -n restore-test
    ```

    ```
    NAME                           COMPLETIONS   ...
    restore-demo3-restore-azblob   1/1           ...
    ```

    You can also check the restoration status by using the following command:

    ```shell
    kubectl get rt -n restore-test -o wide
    ```

## Troubleshooting

If you encounter any problem during the restore process, refer to [Common Deployment Failures](deploy-failures.md).
