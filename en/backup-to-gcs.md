---
title: Back up Data to GCS Using Dumpling
summary: Learn how to back up the TiDB cluster to GCS (Google Cloud Storage) using Dumpling.
aliases: ['/docs/tidb-in-kubernetes/stable/backup-to-gcs/','/docs/tidb-in-kubernetes/v1.1/backup-to-gcs/']
---

# Back up Data to GCS Using Dumpling

This document describes how to back up the data of the TiDB cluster in Kubernetes to [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/). "Backup" in this document refers to full backup (ad-hoc full backup and scheduled full backup). [Dumpling](https://docs.pingcap.com/tidb/dev/export-or-backup-using-dumpling) is used to get the logic backup of the TiDB cluster, and then this backup data is sent to the remote GCS.

The backup method described in this document is implemented using CustomResourceDefinition (CRD) in TiDB Operator v1.1 or later versions.

## Required database account privileges

* The `SELECT` and `UPDATE` privileges of the `mysql.tidb` table: Before and after the backup, the `Backup` CR needs a database account with these privileges to adjust the GC time.
* SELECT
* RELOAD
* LOCK TABLES
* REPLICATION CLIENT

## Ad-hoc full backup to GCS

Ad-hoc full backup describes a backup operation by creating a `Backup` custom resource (CR) object. TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry and you need to handle this error manually.

To better explain how to perform the backup operation, this document shows an example in which the data of the `demo1` TiDB cluster is backed up to the `test1` Kubernetes namespace.

### Prerequisites for ad-hoc full backup

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) and execute the following command to create the role-based access control (RBAC) resources in the `test1` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. Grant permissions to the remote storage.

    Refer to [GCS account permissions](grant-permissions-to-remote-storage.md#gcs-account-permissions).

3. Create the `backup-demo1-tidb-secret` secret which stores the root account and password needed to access the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

### Ad-hoc backup process

1. Create the `Backup` CR and back up data to GCS:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-gcs.yaml
    ```

    The content of `backup-gcs.yaml` is as follows:

    {{< copyable "" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-gcs
      namespace: test1
    spec:
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      gcs:
        secretName: gcs-secret
        projectId: ${project_id}
        bucket: ${bucket}
        # prefix: ${prefix}
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
        # bucketAcl: private
    # dumpling:
    #  options:
    #  - --threads=16
    #  - --rows=10000
    #  tableFilter:
    #  - "test.*"
<<<<<<< HEAD
    storageClassName: local-storage
    storageSize: 10Gi
    ```

2. Create the `Backup` CR and back up data to GCS:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-gcs.yaml
    ```

In the above example, all data of the TiDB cluster is exported and backed up to GCS. You can ignore the `location`, `objectAcl`, `bucketAcl`, and `storageClass` items in the GCS configuration.

`projectId` in the configuration is the unique identifier of the user project on GCP. To learn how to get this identifier, refer to the [GCP documentation](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

GCS supports the following `storageClass` types:

* `MULTI_REGIONAL`
* `REGIONAL`
* `NEARLINE`
* `COLDLINE`
* `DURABLE_REDUCED_AVAILABILITY`

If `storageClass` is not configured, `COLDLINE` is used by default. For the detailed description of these storage types, refer to [GCS documentation](https://cloud.google.com/storage/docs/storage-classes).

GCS supports the following object ACL polices:

* `authenticatedRead`
* `bucketOwnerFullControl`
* `bucketOwnerRead`
* `private`
* `projectPrivate`
* `publicRead`

If the object ACL policy is not configured, the `private` policy is used by default. For the detailed description of these access control policies, refer to [GCS documentation](https://cloud.google.com/storage/docs/access-control/lists).

GCS supports the following bucket ACL policies:

* `authenticatedRead`
* `private`
* `projectPrivate`
* `publicRead`
* `publicReadWrite`

If the bucket ACL policy is not configured, the `private` policy is used by default. For the detailed description of these access control policies, refer to [GCS documentation](https://cloud.google.com/storage/docs/access-control/lists).

After creating the `Backup` CR, you can use the following command to check the backup status:

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -n test1 -owide
```

More parameter description:

* `.spec.metadata.namespace`: the namespace where the `Backup` CR is located.
* `.spec.tikvGCLifeTime`: the temporary `tikv_gc_life_time` time setting during the backup. Defaults to 72h.

    Before the backup begins, if the `tikv_gc_life_time` setting in the TiDB cluster is smaller than `spec.tikvGCLifeTime` set by the user, TiDB Operator adjusts the value of `tikv_gc_life_time` to the value of `spec.tikvGCLifeTime`. This operation makes sure that the backup data is not garbage-collected by TiKV.

    After the backup, no matter whether the backup is successful or not, as long as the previous `tikv_gc_life_time` is smaller than `.spec.tikvGCLifeTime`, TiDB Operator will try to set `tikv_gc_life_time` to the previous value.

    In extreme cases, if TiDB Operator fails to access the database, TiDB Operator cannot automatically recover the value of `tikv_gc_life_time` and treats the backup as failed. At this time, you can view `tikv_gc_life_time` of the current TiDB cluster using the following statement:

    {{< copyable "sql" >}}

    ```sql
    select VARIABLE_NAME, VARIABLE_VALUE from mysql.tidb where VARIABLE_NAME like "tikv_gc_life_time";
    ```

    In the output of the command above, if the value of `tikv_gc_life_time` is still larger than expected (10m by default), it means TiDB Operator failed to automatically recover the value. Therefore, you need to set `tikv_gc_life_time` back to the previous value manually:

    {{< copyable "sql" >}}

    ```sql
    update mysql.tidb set VARIABLE_VALUE = '10m' where VARIABLE_NAME = 'tikv_gc_life_time';
=======
      storageClassName: local-storage
      storageSize: 10Gi
    ```
>>>>>>> a203adc... en: Refactor backup restore (#1071)

    The example above backs up all data in the TiDB cluster to GCS. Some parameters in `spec.gcs` can be ignored, such as `location`, `objectAcl`, `bucketAcl`, and `storageClass`. For more information about GCS configuration, refer to [GCS fields](backup-restore-overview.md#gcs-fields).

    `spec.dumpling` refers to Dumpling-related configuration. You can specify Dumpling's operation parameters in the `options` field. See [Dumpling Option list](https://docs.pingcap.com/tidb/stable/dumpling-overview#option-list-of-dumpling) for more information. These configuration items of Dumpling can be ignored by default. When these items are not specified, the default values of `options` fields are as follows:

    ```
    options:
    - --threads=16
    - --rows=10000
    ```

    For more information about the `Backup` CR fields, refer to [Backup CR fields](backup-restore-overview.md#backup-cr-fields).

2. After creating the `Backup` CR, use the following command to check the backup status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -n test1 -owide
    ```

## Scheduled full backup to GCS

You can set a backup policy to perform scheduled backups of the TiDB cluster, and set a backup retention policy to avoid excessive backup items. A scheduled full backup is described by a custom `BackupSchedule` CR object. A full backup is triggered at each backup time point. Its underlying implementation is the ad-hoc full backup.

### Prerequisites for scheduled backup

The prerequisites for the scheduled backup is the same as the [prerequisites for ad-hoc full backup](#prerequisites-for-ad-hoc-full-backup).

### Scheduled backup process

1. Create the `BackupSchedule` CR, and back up cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-gcs.yaml
    ```

    The content of `backup-schedule-gcs.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-gcs
      namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        gcs:
          secretName: gcs-secret
          projectId: ${project_id}
          bucket: ${bucket}
          # prefix: ${prefix}
          # location: us-east1
          # storageClass: STANDARD_IA
          # objectAcl: private
          # bucketAcl: private
      # dumpling:
      #  options:
      #  - --threads=16
      #  - --rows=10000
      #  tableFilter:
      #  - "test.*"
        # storageClassName: local-storage
        storageSize: 10Gi
    ```

2. After creating the scheduled full backup, use the following command to check the backup status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bks -n test1 -owide
    ```

    Use the following command to check all the backup items:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-gcs -n test1
    ```

From the example above, you can see that the `backupSchedule` configuration consists of two parts. One is the unique configuration of `backupSchedule`, and the other is `backupTemplate`.

`backupTemplate` specifies the configuration related to the cluster and remote storage, which is the same as the `spec` configuration of [the `Backup` CR](backup-restore-overview.md#backup-cr-fields). For the unique configuration of `backupSchedule`, refer to [BackupSchedule CR fields](backup-restore-overview.md#backupschedule-cr-fields).

> **Note:**
>
> TiDB Operator creates a PVC used for both ad-hoc full backup and scheduled full backup. The backup data is stored in PV first and then uploaded to remote storage. If you want to delete this PVC after the backup is completed, you can refer to [Delete Resource](cheat-sheet.md#delete-resources) to delete the backup Pod first, and then delete the PVC.
>
> If the backup data is successfully uploaded to remote storage, TiDB Operator automatically deletes the local data. If the upload fails, the local data is retained.

## Delete the backup CR

Refer to [Delete the Backup CR](backup-restore-overview.md#delete-the-backup-cr).

## Troubleshooting

If you encounter any problem during the backup process, refer to [Common Deployment Failures](deploy-failures.md).
