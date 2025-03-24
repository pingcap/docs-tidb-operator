---
title: Back up Data to GCS Using BR
summary: Learn how to back up data to Google Cloud Storage (GCS) using BR.
---

# Back up Data to GCS Using BR

This document describes how to back up the data of a TiDB cluster on Kubernetes to [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/). There are two backup types:

- **Snapshot backup**. With snapshot backup, you can restore a TiDB cluster to the time point of the snapshot backup using [full restoration](restore-from-gcs-using-br.md#full-restoration).
- **Log backup**. With snapshot backup and log backup, you can restore a TiDB cluster to any point in time. This is also known as [Point-in-Time Recovery (PITR)](restore-from-gcs-using-br.md#point-in-time-recovery).

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to get the backup data of the TiDB cluster, and then send the data to the AWS storage. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Usage scenarios

If you have the following backup needs, you can use BR's **snapshot backup** method to make an [ad-hoc backup](#ad-hoc-backup) or [scheduled snapshot backup](#scheduled-snapshot-backup) of the TiDB cluster data to GCS.

- To back up a large volume of data (more than 1 TB) at a fast speed
- To get a direct backup of data as SST files (key-value pairs)

If you have the following backup needs, you can use BR **log backup** to make an [ad-hoc backup](#ad-hoc-backup) of the TiDB cluster data to GCS (you can combine log backup and snapshot backup to [restore data](restore-from-gcs-using-br.md#point-in-time-recovery) more efficiently):

- To restore data of any point in time to a new cluster
- The recovery point object (RPO) is within several minutes.

For other backup needs, refer to [Backup and Restore Overview](backup-restore-overview.md) to choose an appropriate backup method.

> **Note:**
>
> - Snapshot backup is only applicable to TiDB v3.1 or later releases.
> - Log backup is only applicable to TiDB v6.3 or later releases.
> - Data that is backed up using BR can only be restored to TiDB instead of other databases.

## Ad-hoc backup

Ad-hoc backup includes snapshot backup and log backup. For log backup, you can [start](#start-log-backup) or [stop](#stop-log-backup) a log backup task and [clean log backup data](#clean-log-backup-data).

To get an Ad-hoc backup, you need to create a `Backup` Custom Resource (CR) object to describe the backup details. Then, TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry, and you need to handle this error manually.

This document provides an example about how to back up the data of the `demo1` TiDB cluster in the `test1` Kubernetes namespace to GCS. The following are the detailed steps.

### Prerequisites: Prepare for an ad-hoc backup

1. Create a namespace for managing backup. The following example creates a `backup-test` namespace:

    ```shell
    kubectl create namespace backup-test
    ```

2. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/v1.6.1/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test1` namespace:

    ```shell
    kubectl apply -f backup-rbac.yaml -n backup-test
    ```

3. Grant permissions to the remote storage for the created `backup-test` namespace.

    Refer to [GCS account permissions](grant-permissions-to-remote-storage.md#gcs-account-permissions).

4. For a TiDB version earlier than v4.0.8, you also need to complete the following preparation steps. For TiDB v4.0.8 or a later version, skip these preparation steps.

    1. Make sure that you have the `SELECT` and `UPDATE` privileges on the `mysql.tidb` table of the backup database so that the `Backup` CR can adjust the GC time before and after the backup.
    2. Create the `backup-demo1-tidb-secret` secret to store the root account and password to access the TiDB cluster:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
        ```

### Perform an ad-hoc backup

1. Create the `Backup` CR to back up cluster data to GCS as described below:

    ```shell
    kubectl apply -f full-backup-gcs.yaml
    ```

    The content of `full-backup-gcs.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-full-backup-gcs
      namespace: backup-test
    spec:
      # backupType: full
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
        bucket: my-bucket
        prefix: my-full-backup-folder
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

    When configuring the `full-backup-gcs.yaml`, note the following:

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

#### View the snapshot backup status

After you create the `Backup` CR, TiDB Operator starts the backup automatically. You can view the backup status by running the following command:

```shell
kubectl get backup -n backup-test -o wide
```

From the output, you can find the following information for the `Backup` CR named `demo1-full-backup-gcs`. The `COMMITTS` field indicates the time point of the snapshot backup:

```
NAME                    TYPE   MODE       STATUS     BACKUPPATH                               COMMITTS             ...
demo1-full-backup-gcs   full   snapshot   Complete   gcs://my-bucket/my-full-backup-folder/   436979621972148225   ...
```

### Log backup

You can use a `Backup` CR to describe the start and stop of a log backup task and manage the log backup data. Log backup grants permissions to remote storages in the same way as snapshot backup. In this section, the example shows how to create a `Backup` CR named `demo1-log-backup-gcs`. See the following detailed steps.

#### Description of the `logSubcommand` field

In the Backup Custom Resource (CR), you can use the `logSubcommand` field to control the state of a log backup task. The `logSubcommand` field supports the following commands:

- `log-start`: initiates a new log backup task or resumes a paused task. Use this command to start the log backup process or resume a task from a paused state.

- `log-pause`: temporarily pauses the currently running log backup task. After pausing, you can use the `log-start` command to resume the task.

- `log-stop`: permanently stops the log backup task. After executing this command, the Backup CR enters a stopped state and cannot be restarted.

These commands provide fine-grained control over the lifecycle of log backup tasks, enabling you to start, pause, resume, and stop tasks effectively to manage log data retention in Kubernetes environments.

<Tip>

In TiDB Operator v1.5.4, v1.6.0, and earlier versions, you can use the `logStop: true/false` field to stop or start log backup tasks. This field is retained for backward compatibility.  

However, do not use `logStop` and `logSubcommand` fields in the same Backup CR, as this is not supported. For TiDB Operator v1.5.5, v1.6.1, and later versions, it is recommended to use the `logSubcommand` field to ensure clear and consistent configuration.

</Tip>

#### Start log backup

1. In the `backup-test` namespace, create a `Backup` CR named `demo1-log-backup-gcs`.

    ```shell
    kubectl apply -f log-backup-gcs.yaml
    ```

    The content of `log-backup-gcs.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-gcs
      namespace: backup-test
    spec:
      backupMode: log
      logSubcommand: log-start
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        bucket: my-bucket
        prefix: my-log-backup-folder
    ```

2. Wait for the start operation to complete:

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                    COMPLETIONS   ...
    backup-demo1-log-backup-gcs-log-start   1/1           ...
    ```

3. View the newly created `Backup` CR:

    ```shell
    kubectl get backup -n backup-test
    ```

    ```
    NAME                        MODE   STATUS   ....
    demo1-log-backup-gcs        log    Running  ....
    ```

#### View the log backup status

You can view the log backup status by checking the information of the `Backup` CR:

```shell
kubectl describe backup -n backup-test
```

From the output, you can find the following information for the `Backup` CR named `demo1-log-backup-gcs`. The `Log Checkpoint Ts` field indicates the latest point in time that can be recovered:

```
Status:
Backup Path:  gcs://my-bucket/my-log-backup-folder/
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

#### Pause log backup

You can pause a log backup task by setting the `logSubcommand` field of the Backup Custom Resource (CR) to `log-pause`. The following example shows how to pause the `demo1-log-backup-gcs` CR created in [Start log backup](#start-log-backup).

```shell
kubectl edit backup demo1-log-backup-gcs -n backup-test
```

To pause the log backup task, change the value of `logSubcommand` from `log-start` to `log-pause`, then save and exit the editor. The modified content is as follows:

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-gcs
  namespace: backup-test
spec:
  backupMode: log
  logSubcommand: log-pause
  br:
    cluster: demo1
    clusterNamespace: test1
    sendCredToTikv: true
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: my-bucket
    prefix: my-log-backup-folder
```

You can verify that the `STATUS` of the `demo1-log-backup-gcs` Backup CR changes from `Running` to `Pause`:

```shell
kubectl get backup -n backup-test
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-gcs        log      Pause     ....
```

#### Resume log backup

If a log backup task is paused, you can resume it by setting the `logSubcommand` field to `log-start`. The following example shows how to resume the `demo1-log-backup-gcs` CR that was paused in [Pause Log Backup](#pause-log-backup).

> **Note:**
> 
> This operation applies only to tasks in the `Pause` state. You cannot resume tasks in the `Fail` or `Stopped` state.

```shell
kubectl edit backup demo1-log-backup-gcs -n backup-test
```

To resume the log backup task, change the value of `logSubcommand` from `log-pause` to `log-start`, then save and exit the editor. The modified content is as follows:

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-gcs
  namespace: backup-test
spec:
  backupMode: log
  logSubcommand: log-start
  br:
    cluster: demo1
    clusterNamespace: test1
    sendCredToTikv: true
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: my-bucket
    prefix: my-log-backup-folder
```

You can verify that the `STATUS` of the `demo1-log-backup-gcs` Backup CR changes from `Pause` to `Running`:

```shell
kubectl get backup -n backup-test
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-gcs        log      Running   ....
```

#### Stop log backup

You can stop a log backup task by setting the `logSubcommand` field of the Backup Custom Resource (CR) to `log-stop`. The following example shows how to stop the `demo1-log-backup-gcs` CR created in [Start log backup](#start-log-backup).

```shell
kubectl edit backup demo1-log-backup-gcs -n backup-test
```

Change the value of `logSubcommand` to `log-stop`, then save and exit the editor. The modified content is as follows:

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-gcs
  namespace: backup-test
spec:
  backupMode: log
  logSubcommand: log-stop
  br:
    cluster: demo1
    clusterNamespace: test1
    sendCredToTikv: true
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: my-bucket
    prefix: my-log-backup-folder
```

You can verify that the `STATUS` of the `Backup` CR named `demo1-log-backup-gcs` changes from `Running` to `Stopped`:

```shell
kubectl get backup -n backup-test
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-gcs       log      Stopped   ....
```

<Tip>

`Stopped` is the terminal state for log backup. In this state, you cannot change the backup state again, but you can still clean up the log backup data.

In TiDB Operator v1.5.4, v1.6.0, and earlier versions, you can use the `logStop: true/false` field to stop or start log backup tasks. This field is retained for backward compatibility.

</Tip>

#### Clean log backup data

1. Because you already created a `Backup` CR named `demo1-log-backup-gcs` when you started log backup, you can clean the log data backup by modifying the same `Backup` CR. The following example shows how to clean log backup data generated before 2022-10-10T15:21:00+08:00.

    ```shell
    kubectl edit backup demo1-log-backup-gcs -n backup-test
    ```

    In the last line of the CR, append `spec.logTruncateUntil: "2022-10-10T15:21:00+08:00"`. Then save and quit the editor. The modified content is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-gcs
      namespace: backup-test
    spec:
      backupMode: log
      logSubcommand: log-start/log-pause/log-stop
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        bucket: my-bucket
        prefix: my-log-backup-folder
      logTruncateUntil: "2022-10-10T15:21:00+08:00"
    ```

2. Wait for the clean operation to complete:

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                       COMPLETIONS   ...
    ...
    backup-demo1-log-backup-gcs-log-truncate   1/1           ...
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
    NAME                    MODE       STATUS     ...   LOGTRUNCATEUNTIL
    demo1-log-backup-gcs    log        Stopped    ...   2022-10-10T15:21:00+08:00
    ```

### Compact log backup

For TiDB v9.0.0 and later versions, you can use a `CompactBackup` CR to compact log backup data into SST format, accelerating downstream PITR (Point-in-time recovery).

This section explains how to compact log backup based on the log backup example from previous sections.

1. In the `backup-test` namespace, create a `CompactBackup` CR named `demo1-compact-backup`.

    ```shell
    kubectl apply -f compact-backup-demo1.yaml
    ```

    The content of `compact-backup-demo1.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: CompactBackup
    metadata:
      name: demo1-compact-backup
      namespace: backup-test
    spec:
      startTs: "***"
      endTs: "***"
      concurrency: 8
      maxRetryTimes: 2
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        bucket: my-bucket
        prefix: my-log-backup-folder
    ```

    The `startTs` and `endTs` fields specify the time range for the logs to be compacted by `demo1-compact-backup`. Any log that contains at least one write within this time range will be included in the compaction process. As a result, the final compacted data might include data written outside this range.
    
    The `gcs` settings should be the same as the storage settings of the log backup to be compacted. `CompactBackup` reads log files from the corresponding location and compact them.

#### View the status of log backup compaction

After creating the `CompactBackup` CR, TiDB Operator automatically starts compacting the log backup. You can check the backup status using the following command:

```shell
kubectl get cpbk -n backup-test
```

From the output, you can find the status of the `CompactBackup` CR named `demo1-compact-backup`. An example output is as follows:

```
NAME                   STATUS                   PROGRESS                                     MESSAGE
demo1-compact-backup   Complete   [READ_META(17/17),COMPACT_WORK(1291/1291)]   
```

If the `STATUS` field displays `Complete`, the compact log backup process has finished successfully.

### Backup CR examples

<details>
<summary>Back up data of all clusters</summary>

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-gcs
  namespace: backup-test
spec:
  # backupType: full
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
  namespace: backup-test
spec:
  # backupType: full
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
  namespace: backup-test
spec:
  # backupType: full
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
  namespace: backup-test
spec:
  # backupType: full
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

### Prerequisites: Prepare for a scheduled snapshot backup

The steps to prepare for a scheduled snapshot backup are the same as that of [Prepare for an ad-hoc backup](#prerequisites-prepare-for-an-ad-hoc-backup).

### Perform a scheduled snapshot backup

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
      namespace: backup-test
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        # Clean outdated backup data based on maxBackups or maxReservedTime. If not configured, the default policy is Retain
        # cleanPolicy: Delete
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

    ```shell
    kubectl get bks -n backup-test -owide
    ```

    Use the following command to check all the backup items:

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-gcs -n backup-test
    ```

## Integrated management of scheduled snapshot backup and log backup

You can use the `BackupSchedule` CR to integrate the management of scheduled snapshot backup and log backup for TiDB clusters. By setting the backup retention time, you can regularly recycle the scheduled snapshot backup and log backup, and ensure that you can perform PITR recovery through the scheduled snapshot backup and log backup within the retention period.

The following example creates a `BackupSchedule` CR named `integrated-backup-schedule-gcs`. For more information about the authorization method, refer to [GCS account permissions](grant-permissions-to-remote-storage.md#gcs-account-permissions).

### Prerequisites: Prepare for a scheduled snapshot backup environment

The steps to prepare for a scheduled snapshot backup are the same as those of [Prepare for an ad-hoc backup](#prerequisites-prepare-for-an-ad-hoc-backup).

### Create `BackupSchedule`

1. Create a `BackupSchedule` CR named `integrated-backup-schedule-gcs` in the `backup-test` namespace.

    ```shell
    kubectl apply -f integrated-backup-scheduler-gcs.yaml
    ```

    The content of `integrated-backup-schedule-gcs.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: integrated-backup-schedule-gcs
      namespace: backup-test
    spec:
      maxReservedTime: "3h"
      schedule: "* */2 * * *"
      backupTemplate:
        backupType: full
        cleanPolicy: Delete
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        gcs:
          projectId: ${project_id}
          secretName: gcs-secret
          bucket: my-bucket
          prefix: schedule-backup-folder-snapshot
      logBackupTemplate:
        backupMode: log
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        gcs:
          projectId: ${project_id}
          secretName: gcs-secret
          bucket: my-bucket
          prefix: schedule-backup-folder-log
    ```

    In the above example of `integrated-backup-scheduler-gcs.yaml`, the `backupSchedule` configuration consists of three parts: the unique configuration of `backupSchedule`, the configuration of the snapshot backup `backupTemplate`, and the configuration of the log backup `logBackupTemplate`.

    For the field description of `backupSchedule`, refer to [BackupSchedule CR fields](backup-restore-cr.md#backupschedule-cr-fields).

2. After creating `backupSchedule`, use the following command to check the backup status:

    ```shell
    kubectl get bks -n backup-test -o wide
    ```

    A log backup task is created together with `backupSchedule`. You can check the log backup name through the `status.logBackup` field of the `backupSchedule` CR.

    ```shell
    kubectl describe bks integrated-backup-schedule-gcs -n backup-test
    ```

3. To perform data restoration for a cluster, you need to specify the backup path. You can use the following command to check all the backup items under the scheduled snapshot backup.

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=integrated-backup-schedule-gcs -n backup-test
    ```

    The `MODE` field in the output indicates the backup mode. `snapshot` indicates the scheduled snapshot backup, and `log` indicates the log backup.

    ```
    NAME                                                       MODE       STATUS    ....
    integrated-backup-schedule-gcs-2023-03-08t02-50-00         snapshot   Complete  ....
    log-integrated-backup-schedule-gcs                         log        Running   ....
    ```

## Integrated management of scheduled snapshot backup, log backup, and compact log backup

To accelerate downstream recovery, you can enable `CompactBackup` CR in the `BackupSchedule` CR. This feature periodically compacts log backup files in remote storage. You must enable log backup before using log backup compaction. This section extends the configuration from the previous section.

### Prerequisites: Prepare for a scheduled snapshot backup

The steps to prepare for a scheduled snapshot backup are the same as that of [Prepare for an ad-hoc backup](#prerequisites-prepare-for-an-ad-hoc-backup).

### Create `BackupSchedule`

1. Create a `BackupSchedule` CR named `integrated-backup-schedule-gcs` in the `backup-test` namespace.

    ```shell
    kubectl apply -f integrated-backup-schedule-s3.yaml
    ```

    The content of `integrated-backup-schedule-gcs.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: integrated-backup-schedule-gcs
      namespace: backup-test
    spec:
      maxReservedTime: "3h"
      schedule: "* */2 * * *"
      backupTemplate:
        backupType: full
        cleanPolicy: Delete
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        gcs:
          projectId: ${project_id}
          secretName: gcs-secret
          bucket: my-bucket
          prefix: schedule-backup-folder-snapshot
      logBackupTemplate:
        backupMode: log
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        gcs:
          projectId: ${project_id}
          secretName: gcs-secret
          bucket: my-bucket
          prefix: schedule-backup-folder-log
      compactBackupTemplate:
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        gcs:
          projectId: ${project_id}
          secretName: gcs-secret
          bucket: my-bucket
          prefix: schedule-backup-folder-log
    ```

    In the preceding example of `integrated-backup-schedule-gcs.yaml`,  the `backupSchedule` configuration is based on the previous section, with the following additions for `compactBackup`:
    
    * Added the `BackupSchedule.spec.compactInterval` field to specify the time interval for log backup compaction. It is recommended not to exceed the interval of scheduled snapshot backups and to keep it between one-half to one-third of the scheduled snapshot backup interval.
    
    * Added the `BackupSchedule.spec.compactBackupTemplate` field. Ensure that the `BackupSchedule.spec.compactBackupTemplate.gcs` configuration matches the `BackupSchedule.spec.logBackupTemplate.gcs` configuration.

    For the field description of `backupSchedule`, refer to [BackupSchedule CR fields](backup-restore-cr.md#backupschedule-cr-fields).

2. After creating `backupSchedule`, use the following command to check the backup status:

    ```shell
    kubectl get bks -n backup-test -o wide
    ```

    A compact log backup task is created together with `backupSchedule`. You can check the `CompactBackup` CR using the following command:

    ```shell
    kubectl get cpbk -n backup-test
    ```

## Delete the backup CR

If you no longer need the backup CR, refer to [Delete the Backup CR](backup-restore-overview.md#delete-the-backup-cr).

## Troubleshooting

If you encounter any problem during the backup process, refer to [Common Deployment Failures](deploy-failures.md).
