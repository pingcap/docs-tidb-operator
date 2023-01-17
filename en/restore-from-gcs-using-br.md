---
title: Restore Data from GCS Using BR
summary: Learn how to restore data from Google Cloud Storage (GCS) using BR.
---

# Restore Data from GCS Using BR

This document describes how to restore the backup data stored in [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/) to a TiDB cluster on Kubernetes, including two restoration methods:

- Full restoration. This method takes the backup data of snapshot backup and restores a TiDB cluster to the time point of the snapshot backup.
- Point-in-time recovery (PITR). This method takes the backup data of both snapshot backup and log backup and restores a TiDB cluster to any point in time.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

PITR allows you to restore a new TiDB cluster to any point in time of the backup cluster. To use PITR, you need the backup data of snapshot backup and log backup. During the restoration, the snapshot backup data is first restored to the TiDB cluster, and then the log backup data between the snapshot backup time point and the specified point in time is restored to the TiDB cluster.

> **Note:**
>
> - BR is only applicable to TiDB v3.1 or later releases.
> - PITR is only applicable to TiDB v6.3 or later releases.
> - Data restored by BR cannot be replicated to a downstream cluster, because BR directly imports SST and LOG files to TiDB and the downstream cluster currently cannot access the upstream SST and LOG files.

This document provides an example about how to restore the backup data from the `spec.gcs.prefix` folder of the `spec.gcs.bucket` bucket on GCS to the `demo2` TiDB cluster in the `test2` namespace. The following are the detailed steps.

## Full restoration

This section provides an example about how to restore the backup data from the `spec.gcs.prefix` folder of the `spec.gcs.bucket` bucket on GCS to the `demo2` TiDB cluster in the `test2` namespace. The following are the detailed steps.

### Prerequisites: Complete the snapshot backup

In this example, the `my-full-backup-folder` folder in the `my-bucket` bucket of GCS stores the snapshot backup data. For steps of performing snapshot backup, refer to [Back up Data to GCS Using BR](backup-to-gcs-using-br.md).

### Step 1: Prepare the restore environment

Before restoring backup data on GCS to TiDB using BR, take the following steps to prepare the restore environment:

1. Create a namespace for managing restoration. The following example creates a `restore-test` namespace:

    ```shell
    kubectl create namespace restore-test
    ```

2. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `restore-test` namespace:

    ```shell
    kubectl apply -f backup-rbac.yaml -n restore-test
    ```

3. Grant permissions to the remote storage for the `restore-test` namespace.

    Refer to [GCS account permissions](grant-permissions-to-remote-storage.md#gcs-account-permissions).

4. For a TiDB version earlier than v4.0.8, you also need to complete the following preparation steps. For TiDB v4.0.8 or a later version, skip these preparation steps.

    1. Make sure that you have the `SELECT` and `UPDATE` privileges on the `mysql.tidb` table of the target database so that the `Restore` CR can adjust the GC time before and after the restore.

    2. Create the `restore-demo2-tidb-secret` secret to store the root account and password to access the TiDB cluster:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
        ```

## Step 2: Restore the backup data to a TiDB cluster

1. Create the `Restore` custom resource (CR) to restore the specified data to your cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-full-gcs.yaml
    ```

    The content of `restore-full-gcs.yaml` file is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-gcs
      namespace: restore-test
    spec:
      # backupType: full
      br:
        cluster: demo2
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status-addr}
        # concurrency: 4
        # rateLimit: 0
        # checksum: true
        # sendCredToTikv: true
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      # to:
      #   host: ${tidb_host}
      #   port: ${tidb_port}
      #   user: ${tidb_user}
      #   secretName: restore-demo2-tidb-secret
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        bucket: my-bucket
        prefix: my-full-backup-folder
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

    When configuring `restore-full-gcs.yaml`, note the following:

    - For more information about GCS configuration, refer to [GCS fields](backup-restore-cr.md#gcs-fields).
    - Some parameters in `.spec.br` are optional, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, `timeAgo`, and `sendCredToTikv`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
    - For v4.0.8 or a later version, BR can automatically adjust `tikv_gc_life_time`. You do not need to configure `spec.to` fields in the `Restore` CR.
    - For more information about the `Restore` CR fields, refer to [Restore CR fields](backup-restore-cr.md#restore-cr-fields).

2. After creating the `Restore` CR, execute the following command to check the restore status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get restore -n restore-test -owide
    ```

    ```
    NAME                STATUS     ...
    demo2-restore-gcs   Complete   ...
     ```

## Point-in-time recovery

This section provides an example about how to perform point-in-time recovery (PITR) in a `demo3` cluster in the `test3` namespace. PITR takes two steps:

1. Restore the cluster to the time point of the snapshot backup using the snapshot backup data in the `spec.pitrFullBackupStorageProvider.gcs.prefix` folder of the `spec.pitrFullBackupStorageProvider.gcs.bucket` bucket.
2. Restore the cluster to any point in time using the log backup data in the `spec.gcs.prefix` folder of the `spec.gcs.bucket` bucket.

The detailed steps are as follows.

### Prerequisites: Complete data backup

In this example, the `my-bucket` bucket of GCS stores the following two types of backup data:

- The snapshot backup data generated during the **log backup**, stored in the `my-full-backup-folder-pitr` folder.
- The log backup data, stored in the `my-log-backup-folder-pitr` folder.

For detailed steps of how to perform data backup, refer to [Back up data to GCS Using BR](backup-to-gcs-using-br.md).

> **Note:**
>
> The specified restoration time point must be between the snapshot backup time point and the log backup `checkpoint-ts`.

### Step 1: Prepare the restoration environment

Before restoring backup data on GCS to TiDB using BR, take the following steps to prepare the restoration environment:

1. Create a namespace for managing restoration. The following example creates a `restore-test` namespace:

    ```shell
    kubectl create namespace restore-test
    ```

2. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `restore-test` namespace:

    ```shell
    kubectl apply -f backup-rbac.yaml -n restore-test
    ```

3. Grant permissions to the remote storage for the `restore-test` namespace.

    Refer to [GCS account permissions](grant-permissions-to-remote-storage.md#gcs-account-permissions).

### Step 2: Restore the backup data to a TiDB cluster

The example in this section restores the snapshot backup data to the cluster. The specified restoration time point must be between [the time point of snapshot backup](backup-to-gcs-using-br.md#view-the-snapshot-backup-status) and the [`Log Checkpoint Ts` of log backup](backup-to-gcs-using-br.md#view-the-log-backup-status).

The detailed steps are as follows:

1. Create a `Restore` CR named `demo3-restore-gcs` in the `restore-test` namespace and specify the restoration time point as `2022-10-10T17:21:00+08:00`:

    ```shell
    kubectl apply -f restore-point-gcs.yaml
    ```

    The content of `restore-point-gcs.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo3-restore-gcs
      namespace: restore-test
    spec:
      restoreMode: pitr
      br:
        cluster: demo3
        clusterNamespace: test3
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        bucket: my-bucket
        prefix: my-log-backup-folder-pitr
      pitrRestoredTs: "2022-10-10T17:21:00+08:00"
      pitrFullBackupStorageProvider:
        gcs:
          projectId: ${project_id}
          secretName: gcs-secret
          bucket: my-bucket
          prefix: my-full-backup-folder-pitr
    ```

    When you configure `restore-point-gcs.yaml`, note the following:

    - `spec.restoreMode`: when you perform PITR, set this field to `pitr`. The default value of this field is `snapshot`, which means snapshot backup.

2. Wait for the restoration operation to complete:

    ```shell
    kubectl get jobs -n restore-test
    ```

    ```
    NAME                        COMPLETIONS   ...
    restore-demo3-restore-gcs   1/1           ...
    ```

    You can also check the restoration status by using the following command:

    ```shell
    kubectl get restore -n restore-test -o wide
    ```

    ```
    NAME                STATUS     ...
    demo3-restore-gcs   Complete   ...
    ```

## Troubleshooting

If you encounter any problem during the restore process, refer to [Common Deployment Failures](deploy-failures.md).
