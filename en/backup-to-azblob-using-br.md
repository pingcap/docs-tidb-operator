---
title: Back up Data to Azure Blob Storage Using BR
summary: Learn how to back up data to Azure Blob Storage using BR.
---

# Back up Data to Azure Blob Storage Using BR

This document describes how to back up the data of a TiDB cluster on Kubernetes to Azure Blob Storage. There are two backup types:

- **Snapshot backup**. With snapshot backup, you can restore a TiDB cluster to the time point of the snapshot backup using [full restoration](restore-from-azblob-using-br.md#full-restoration).
- **Log backup**. With snapshot backup and log backup, you can restore a TiDB cluster to any point in time. This is also known as [Point-in-Time Recovery (PITR)](restore-from-azblob-using-br.md#point-in-time-recovery).

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to get the backup data of the TiDB cluster, and then send the data to Azure Blob Storage. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Usage scenarios

If you have the following backup needs, you can use BR to make an [ad-hoc backup](#ad-hoc-backup) or [scheduled snapshot backup](#scheduled-snapshot-backup) of the TiDB cluster data to Azure Blob Storage.

- To back up a large volume of data (more than 1 TB) at a fast speed.
- To get a direct backup of data as SST files (key-value pairs).

If you have the following backup needs, you can use BR **log backup** to make an [ad-hoc backup](#ad-hoc-backup) of the TiDB cluster data to Azure Blob Storage (you can combine log backup and snapshot backup to [restore data](restore-from-azblob-using-br.md#point-in-time-recovery) more efficiently):

- To restore data of any point in time to a new cluster
- The recovery point object (RPO) is within several minutes.

For other backup needs, refer to [Backup and Restore Overview](backup-restore-overview.md) to choose an appropriate backup method.

> **Note:**
>
> - Snapshot backup is only applicable to TiDB v3.1 or later releases.
> - Log backup is only applicable to TiDB v6.2 or later releases.
> - Data that is backed up using BR can only be restored to TiDB instead of other databases.

## Ad-hoc backup

Ad-hoc backup includes snapshot backup and log backup. For log backup, you can start or stop a log backup task and clean log backup data.

To get an ad-hoc backup, you need to create a `Backup` Custom Resource (CR) object to describe the backup details. Then, TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry, and you need to handle this error manually.

This document provides an example about how to back up the data of the `demo1` TiDB cluster in the `test1` Kubernetes namespace to Azure Blob Storage. The following are the detailed steps.

### Prerequisites: Prepare an ad-hoc backup environment

1. Create a namespace for managing backup. The following example creates a `backup-test` namespace:

    ```shell
    kubectl create namespace backup-test
    ```

2. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `backup-test` namespace:

    ```shell
    kubectl apply -f backup-rbac.yaml -n backup-test
    ```

3. Grant permissions to the remote storage for the `backup-test` namespace. You can grant permissions to Azure Blob Storage by two methods. For details, refer to [Azure account permissions](grant-permissions-to-remote-storage.md#azure-account-permissions). After you grant the permissions, the `backup-test` namespace has a secret object named `azblob-secret` or `azblob-secret-ad`.

    > **Note:**
    >
    > The role owned by the account must have the permission to modify blob at least (for example, a [contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#contributor)).
    >
    > When you create a secret object, you can use a customized name for the object. In this document, the name is `azblob-secret`.

4. For a TiDB version earlier than v4.0.8, you also need to complete the following preparation steps. For TiDB v4.0.8 or a later version, skip these preparation steps.

    1. Make sure that you have the `SELECT` and `UPDATE` privileges on the `mysql.tidb` table of the backup database so that the `Backup` CR can adjust the GC time before and after the backup.
    2. Create `backup-demo1-tidb-secret` to store the account and password to access the TiDB cluster:

        ```shell
        kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
        ```

### Snapshot backup

To perform a snapshot backup, take the following steps:

Create the `Backup` CR named `demo1-full-backup-azblob` in the `backup-test` namespace:

```shell
kubectl apply -f full-backup-azblob.yaml
```

The content of `full-backup-azblob.yaml` is as follows:

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-full-backup-azblob
  namespace: backup-test
spec:
  backupType: full
  br:
    cluster: demo1
    clusterNamespace: test1
    # logLevel: info
    # statusAddr: ${status_addr}
    # concurrency: 4
    # rateLimit: 0
    # timeAgo: ${time}
    # checksum: true
    # sendCredToTikv: true
    # options:
    # - --lastbackupts=420134118382108673
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  from:
    host: ${tidb_host}
    port: ${tidb_port}
    user: ${tidb_user}
    secretName: backup-demo1-tidb-secret
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-full-backup-folder
    #accessTier: Hot
```

When you configure `backup-azblob.yaml`, note the following:

- Since TiDB Operator v1.1.6, if you want to back up data incrementally, you only need to specify the last backup timestamp `--lastbackupts` in `spec.br.options`. For the limitations of incremental backup, refer to [Use BR to Back up and Restore Data](https://docs.pingcap.com/tidb/stable/br-usage-backup#back-up-incremental-data).
- For more information about Azure Blob Storage configuration, refer to [Azure Blob Storage fields](backup-restore-cr.md#azure-blob-storage-fields).
- Some parameters in `spec.br` are optional, such as `logLevel` and `statusAddr`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
- `spec.azblob.secretName`: fill in the name of the secret object, such as `azblob-secret`.
- For v4.0.8 or a later version, BR can automatically adjust `tikv_gc_life_time`. You do not need to configure the `spec.tikvGCLifeTime` and `spec.from` fields in the `Backup` CR.
- For more information about the `Backup` CR fields, refer to [Backup CR fields](backup-restore-cr.md#backup-cr-fields).

#### View the snapshot backup status

After you create the `Backup` CR, TiDB Operator starts the backup automatically. You can view the backup status by running the following command:

```shell
kubectl get backup -n backup-test -o wide
```

From the output, you can find the following information for the `Backup` CR named `demo1-full-backup-azblob`. The `COMMITTS` field indicates the time point of the snapshot backup:

```
NAME                       TYPE   MODE       STATUS     BACKUPPATH                                    COMMITTS             ...
demo1-full-backup-azblob   full   snapshot   Complete   azure://my-container/my-full-backup-folder/   436979621972148225   ...
```

### Log backup

You can use a `Backup` CR to describe the start and stop of a log backup task and manage the log backup data. In this section, the example shows how to create a `Backup` CR named `demo1-log-backup-azblob`. See the following detailed steps.

#### Start log backup

1. In the `backup-test` namespace, create a `Backup` CR named `demo1-log-backup-azblob`.

    ```shell
    kubectl apply -f log-backup-azblob.yaml
    ```

    The content of `log-backup-azblob.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-azblob
      namespace: backup-test
    spec:
      backupMode: log
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-log-backup-folder
        #accessTier: Hot
    ```

2. Wait for the start operation to complete:

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                       COMPLETIONS   ...
    backup-demo1-log-backup-azblob-log-start   1/1           ...
    ```

3. View the newly created `Backup` CR:

    ```shell
    kubectl get backup -n backup-test
    ```

    ```
    NAME                       TYPE    MODE   STATUS   ....
    demo1-log-backup-azblob            log    Running  ....
    ```

#### View the log backup status

You can view the log backup status by checking the information of the `Backup` CR:

```shell
kubectl describe backup -n backup-test
```

From the output, you can find the following information for the `Backup` CR named `demo1-log-backup-azblob`. The `Log Checkpoint Ts` field indicates the latest point in time that can be recovered:

```
Status:
Backup Path: azure://my-container/my-log-backup-folder/
Commit Ts:    436568622965194754
Conditions:
    Last Transition Time:  2022-10-10T04:45:20Z
    Status:                True
    Type:                  Scheduled
    Last Transition Time:  2022-10-10T04:45:31Z
    Status:                True
    Type:                  Prepare
    Last Transition Time:  2022-10-10T04:45:31Z
    Status:                True
    Type:                  Running
Log Checkpoint Ts:       436569119308644661
```

#### Stop log backup

Because you already created a `Backup` CR named `demo1-log-backup-azblob` when you started log backup, you can stop the log backup by modifying the same `Backup` CR. The priority of all operations is: stop log backup > delete log backup data > start log backup.

```shell
kubectl edit backup demo1-log-backup-azblob -n backup-test
```

In the last line of the CR, append `spec.logStop: true`. Then save and quit the editor. The modified content is as follows:

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-azblob
  namespace: backup-test
spec:
  backupMode: log
  br:
    cluster: demo1
    clusterNamespace: test1
    sendCredToTikv: true
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-log-backup-folder
    #accessTier: Hot
  logStop: true
```

You can see the `STATUS` of the `Backup` CR named `demo1-log-backup-azblob` change from `Running` to `Complete`:

```shell
kubectl get backup -n backup-test
```

```
NAME                       TYPE    MODE   STATUS    ....
demo1-log-backup-azblob            log    Complete  ....
```

<Tip>
You can stop log backup by taking the same steps as in [Start log backup](#start-log-backup). The existing `Backup` CR will be updated.
</Tip>

#### Clean log backup data

1. Because you already created a `Backup` CR named `demo1-log-backup-azblob` when you started log backup, you can clean the log data backup by modifying the same `Backup` CR. The priority of all operations is: stop log backup > delete log backup data > start log backup. The following example shows how to clean log backup data generated before 2022-10-10T15:21:00+08:00.

    ```shell
    kubectl edit backup demo1-log-backup-azblob -n backup-test
    ```

    In the last line of the CR, append `spec.logTruncateUntil: "2022-10-10T15:21:00+08:00"`. Then save and quit the editor. The modified content is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-azblob
      namespace: backup-test
    spec:
      backupMode: log
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-log-backup-folder
        #accessTier: Hot
      logTruncateUntil: "2022-10-10T15:21:00+08:00"
    ```

2. Wait for the clean operation to complete:

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                          COMPLETIONS   ...
    ...
    backup-demo1-log-backup-azblob-log-truncate   1/1           ...
    ```

3. View the `Backup` CR information:

    ```shell
    kubectl describe backup -n backup-test
    ```

    ```
    ...
    Log Success Truncate Until:  2022-10-10T15:21:00+08:00
    ...
    ```

    You can also view the information by running the following command:

    ```shell
    kubectl get backup -n backup-test -o wide
    ```

    ```
    NAME                TYPE   MODE       STATUS     ...   LOGTRUNCATEUNTIL
    demo1-log-backup           log        Complete   ...   2022-10-10T15:21:00+08:00
    ```

### Backup CR examples

<details>
<summary>Back up data of all clusters</summary>

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-azblob
  namespace: backup-test
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
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
  name: demo1-backup-azblob
  namespace: backup-test
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.*"
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
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
  name: demo1-backup-azblob
  namespace: backup-test
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.table1"
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
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
  name: demo1-backup-azblob
  namespace: backup-test
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.table1"
  - "db1.table2"
  # ...
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    bucket: my-bucket
    prefix: my-folder
```

</details>

## Scheduled snapshot backup

You can set a backup policy to perform scheduled backups of the TiDB cluster, and set a backup retention policy to avoid excessive backup items. A scheduled snapshot backup is described by a custom `BackupSchedule` CR object. A snapshot backup is triggered at each backup time point. Its underlying implementation is the ad-hoc snapshot backup.

### Prerequisites: Prepare a scheduled backup environment

Refer to [Prepare an ad-hoc backup environment](#prerequisites-prepare-an-ad-hoc-backup-environment).

### Perform a scheduled snapshot backup

Depending on which method you choose to grant permissions to the remote storage, perform a scheduled snapshot backup by doing one of the following:

+ Method 1: If you grant permissions by access key, create the `BackupSchedule` CR, and back up cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-scheduler-azblob.yaml
    ```

    The content of `backup-scheduler-azblob.yaml` is as follows:

    {{< copyable "" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-azblob
      namespace: backup-test
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        backupType: full
        br:
          cluster: demo1
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status_addr}
          # concurrency: 4
          # rateLimit: 0
          # timeAgo: ${time}
          # checksum: true
          # sendCredToTikv: true
        # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        azblob:
          secretName: azblob-secret-ad
          container: my-container
          prefix: my-folder
    ```

+ Method 2: If you grant permissions by Azure AD, create the `BackupSchedule` CR, and back up cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-scheduler-azblob.yaml
    ```

    The content of `backup-scheduler-azblob.yaml` is as follows:

    {{< copyable "" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-azblob
      namespace: backup-test
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        backupType: full
        br:
          cluster: demo1
          sendCredToTikv: false
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status_addr}
          # concurrency: 4
          # rateLimit: 0
          # timeAgo: ${time}
          # checksum: true
        # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        azblob:
          secretName: azblob-secret-ad
          container: my-container
          prefix: my-folder
    ```

From the preceding content in `backup-scheduler-azblob.yaml`, you can see that the `backupSchedule` configuration consists of two parts. One is the unique configuration of `backupSchedule`, and the other is `backupTemplate`.

- For the unique configuration of `backupSchedule`, refer to [BackupSchedule CR fields](backup-restore-cr.md#backupschedule-cr-fields).
- `backupTemplate` specifies the configuration related to the cluster and remote storage, which is the same as the `spec` configuration of [the `Backup` CR](backup-restore-cr.md#backup-cr-fields).

After creating the scheduled snapshot backup, you can run the following command to check the backup status:

{{< copyable "shell-regular" >}}

```shell
kubectl get backup -n test1 -o wide
```

You can run the following command to check all the backup items:

{{< copyable "shell-regular" >}}

```shell
kubectl get backup -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-azblob -n test1
```

## Delete the backup CR

If you no longer need the backup CR, you can delete it by referring to [Delete the Backup CR](backup-restore-overview.md#delete-the-backup-cr).

## Troubleshooting

If you encounter any problem during the backup process, refer to [Common Deployment Failures](deploy-failures.md).
