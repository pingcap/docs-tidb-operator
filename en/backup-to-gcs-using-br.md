---
title: Back up Data to GCS Using BR
summary: Learn how to back up data to Google Cloud Storage (GCS) using BR.
---

# Back up Data to GCS Using BR

This document describes how to back up the data of a TiDB cluster in Kubernetes to [Google Cloud Storage](https://cloud.google.com/storage/docs/) (GCS).

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to get the backup data of the TiDB cluster, and then send the data to the AWS storage. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Usage scenarios

If you have the following backup needs, you can use BR to make an [ad-hoc backup](#ad-hoc-backup) or [scheduled snapshot backup](#scheduled-snapshot-backup) of the TiDB cluster data to GCS.

- To back up a large volume of data (more than 1 TB) at a fast speed
- To get a direct backup of data as SST files (key-value pairs)

For other backup needs, refer to [Backup and Restore Overview](backup-restore-overview.md) to choose an appropriate backup method.

> **Note:**
>
> - BR is only applicable to TiDB v3.1 or later releases.
> - Data that is backed up using BR can only be restored to TiDB instead of other databases.

## Ad-hoc backup

Ad-hoc backup supports both snapshot backup and incremental backup.

To get an Ad-hoc backup, you need to create a `Backup` Custom Resource (CR) object to describe the backup details. Then, TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry, and you need to handle this error manually.

This document provides an example about how to back up the data of the `demo1` TiDB cluster in the `test1` Kubernetes namespace to GCS. The following are the detailed steps.

### Step 1: Prepare for an ad-hoc backup

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test1` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. Grant permissions to the remote storage.

    Refer to [GCS account permissions](grant-permissions-to-remote-storage.md#gcs-account-permissions).

3. For a TiDB version earlier than v4.0.8, you also need to complete the following preparation steps. For TiDB v4.0.8 or a later version, skip these preparation steps.

    1. Make sure that you have the `SELECT` and `UPDATE` privileges on the `mysql.tidb` table of the backup database so that the `Backup` CR can adjust the GC time before and after the backup.
    2. Create the `backup-demo1-tidb-secret` secret to store the root account and password to access the TiDB cluster:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
        ```

### Step 2: Perform an ad-hoc backup

1. Create the `Backup` CR to back up cluster data to GCS as described below:

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
      # backupType: full
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      from:
        host: ${tidb-host}
        port: ${tidb-port}
        user: ${tidb-user}
        secretName: backup-demo1-tidb-secret
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
        # statusAddr: ${status-addr}
        # concurrency: 4
        # rateLimit: 0
        # checksum: true
        # sendCredToTikv: true
        # options:
        # - --lastbackupts=420134118382108673
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        bucket: ${bucket}
        prefix: ${prefix}
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

    When configuring the `backup-gcs.yaml`, note the following:

    - Since TiDB Operator v1.1.6, if you want to back up data incrementally, you only need to specify the last backup timestamp `--lastbackupts` in `spec.br.options`. For the limitations of incremental backup, refer to [Use BR to Back up and Restore Data](https://docs.pingcap.com/tidb/stable/br-usage-backup#back-up-incremental-data).
    - Some parameters in `spec.br` are optional, such as `logLevel` and `statusAddr`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
    - Some parameters in `spec.gcs` are optional, such as `location`, `objectAcl`, and `storageClass`. For more information about GCS configuration, refer to [GCS fields](backup-restore-cr.md#gcs-fields).
    - For v4.0.8 or a later version, BR can automatically adjust `tikv_gc_life_time`. You do not need to configure `spec.tikvGCLifeTime` and `spec.from` fields in the `Backup` CR.
    - For more information about the `Backup` CR fields, refer to [Backup CR fields](backup-restore-cr.md#backup-cr-fields).

2. After you create the `Backup` CR, TiDB Operator starts the backup automatically. You can view the backup status by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -n test1 -owide
    ```

### Backup CR examples

<details>
<summary>Back up data of all clusters</summary>

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-gcs
  namespace: test1
spec:
  # backupType: full
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb-host}
    # port: ${tidb-port}
    # user: ${tidb-user}
    # secretName: backup-demo1-tidb-secret
  br:
    cluster: demo1
    clusterNamespace: test1
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: ${bucket}
    prefix: ${prefix}
    # location: us-east1
    # storageClass: STANDARD_IA
    # objectAcl: private
```

</details>

<details>
<summary>Back up data of a single database</summary>

The following example backs up data of the `db1` database.

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-gcs
  namespace: test1
spec:
  # backupType: full
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb-host}
    # port: ${tidb-port}
    # user: ${tidb-user}
    # secretName: backup-demo1-tidb-secret
  tableFilter:
  - "db1.*"
  br:
    cluster: demo1
    clusterNamespace: test1
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: ${bucket}
    prefix: ${prefix}
    # location: us-east1
    # storageClass: STANDARD_IA
    # objectAcl: private
```

</details>

<details>
<summary>Back up data of a single table</summary>

The following example backs up data of the `db1.table1` table.

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-gcs
  namespace: test1
spec:
  # backupType: full
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb-host}
    # port: ${tidb-port}
    # user: ${tidb-user}
    # secretName: backup-demo1-tidb-secret
  tableFilter:
  - "db1.table1"
  br:
    cluster: demo1
    clusterNamespace: test1
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: ${bucket}
    prefix: ${prefix}
    # location: us-east1
    # storageClass: STANDARD_IA
    # objectAcl: private
```

</details>

<details>
<summary>Back up data of multiple tables using the table filter</summary>

The following example backs up data of the `db1.table1` table and `db1.table2` table.

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-gcs
  namespace: test1
spec:
  # backupType: full
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb-host}
    # port: ${tidb-port}
    # user: ${tidb-user}
    # secretName: backup-demo1-tidb-secret
  tableFilter:
  - "db1.table1"
  - "db1.table2"
  br:
    cluster: demo1
    clusterNamespace: test1
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: ${bucket}
    prefix: ${prefix}
    # location: us-east1
    # storageClass: STANDARD_IA
    # objectAcl: private
```

</details>

## Scheduled snapshot backup

You can set a backup policy to perform scheduled backups of the TiDB cluster, and set a backup retention policy to avoid excessive backup items. A scheduled snapshot backup is described by a custom `BackupSchedule` CR object. A snapshot backup is triggered at each backup time point. Its underlying implementation is the ad-hoc snapshot backup.

### Step 1: Prepare for a scheduled snapshot backup

The steps to prepare for a scheduled snapshot backup are the same as that of [Prepare for an ad-hoc backup](#step-1-prepare-for-an-ad-hoc-backup).

### Step 2: Perform a scheduled snapshot backup

1. Create a `BackupSchedule` CR to back up cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-gcs.yaml
    ```

    The content of `backup-schedule-gcs.yaml` is as follows:

    {{< copyable "" >}}

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
        # Clean outdated backup data based on maxBackups or maxReservedTime. If not configured, the default policy is Retain
        # cleanPolicy: Delete
        # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        br:
          cluster: demo1
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status-addr}
          # concurrency: 4
          # rateLimit: 0
          # checksum: true
          # sendCredToTikv: true
        gcs:
          secretName: gcs-secret
          projectId: ${project_id}
          bucket: ${bucket}
          prefix: ${prefix}
          # location: us-east1
          # storageClass: STANDARD_IA
          # objectAcl: private
    ```

    From the above in `backup-schedule-gcs.yaml`, you can see that the `backupSchedule` configuration consists of two parts. One is the unique configuration of `backupSchedule`, and the other is `backupTemplate`.

    - For the unique configuration of `backupSchedule`, refer to [BackupSchedule CR fields](backup-restore-cr.md#backupschedule-cr-fields).
    - `backupTemplate` specifies the configuration related to the cluster and remote storage, which is the same as the `spec` configuration of [the `Backup` CR](backup-restore-cr.md#backup-cr-fields).

2. After creating the scheduled snapshot backup, use the following command to check the backup status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bks -n test1 -owide
    ```

    Use the following command to check all the backup items:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-gcs -n test1
    ```

## Delete the backup CR

If you no longer need the backup CR, refer to [Delete the Backup CR](backup-restore-overview.md#delete-the-backup-cr).

## Troubleshooting

If you encounter any problem during the backup process, refer to [Common Deployment Failures](deploy-failures.md).
