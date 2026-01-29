---
title: Back Up Data to Azure Blob Storage Using BR
summary: Learn how to back up data to Azure Blob Storage using BR.
---

# Back Up Data to Azure Blob Storage Using BR

This document describes how to back up the data of a TiDB cluster on Kubernetes to Azure Blob Storage. There are two backup types:

- **Snapshot backup**. With snapshot backup, you can restore a TiDB cluster to the time point of the snapshot backup using [full restoration](restore-from-azblob-using-br.md#full-restoration).
- **Log backup**. With snapshot backup and log backup, you can restore a TiDB cluster to any point in time. This is also known as [Point-in-Time Recovery (PITR)](restore-from-azblob-using-br.md#point-in-time-recovery).

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to get the backup data of the TiDB cluster, and then send the data to Azure Blob Storage. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Usage scenarios

If you have the following backup needs, you can use BR to make an [ad-hoc backup](#ad-hoc-backup) of the TiDB cluster data to Azure Blob Storage.

- To back up a large volume of data (more than 1 TiB) at a fast speed.
- To get a direct backup of data as SST files (key-value pairs).

If you have the following backup needs, you can use BR **log backup** to make an [ad-hoc backup](#ad-hoc-backup) of the TiDB cluster data to Azure Blob Storage (you can combine log backup and snapshot backup to [restore data](restore-from-azblob-using-br.md#point-in-time-recovery) more efficiently):

- To restore data of any point in time to a new cluster
- The recovery point object (RPO) is within several minutes.

For other backup needs, refer to [Backup and Restore Overview](backup-restore-overview.md) to choose an appropriate backup method.

> **Note:**
>
> - Snapshot backup is only applicable to TiDB v3.1 or later releases.
> - Log backup is only applicable to TiDB v6.3 or later releases.
> - Data backed up using BR can only be restored to TiDB instead of other databases.

## Ad-hoc backup

Ad-hoc backup includes snapshot backup and log backup. For log backup, you can start or stop a log backup task and clean log backup data.

To get an ad-hoc backup, you need to create a `Backup` Custom Resource (CR) object to describe the backup details. Then, TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry, and you need to handle this error manually.

This document provides an example about how to back up the data of the `demo1` TiDB cluster in the `test1` Kubernetes namespace to Azure Blob Storage. The following are the detailed steps.

### Prerequisites: Prepare an ad-hoc backup environment

1. Create the required role-based access control (RBAC) resources:

    ```shell
    kubectl apply -n test1 -f - <<EOF
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: tidb-backup-manager
      labels:
        app.kubernetes.io/component: tidb-backup-manager
    rules:
    - apiGroups: [""]
      resources: ["events"]
      verbs: ["*"]
    - apiGroups: ["br.pingcap.com"]
      resources: ["*"]
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
    EOF
    ```

2. Refer to [Grant permissions to an Azure account](grant-permissions-to-remote-storage.md#grant-permissions-to-an-azure-account) to grant access to remote storage. Azure provides two methods for granting permissions. After successful authorization, a Secret object named `azblob-secret` or `azblob-secret-ad` should exist in the `test1` namespace.

    > **Note:**
    >
    > - The authorized account must have at least write access to Blob data, such as the [Contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#contributor) role.
    > - When creating the Secret object, you can customize its name. For demonstration purposes, this document uses `azblob-secret` as the example Secret name.

### Snapshot backup

To perform a snapshot backup, take the following steps:

Create the `Backup` CR named `demo1-full-backup-azblob` in the `test1` namespace:

```shell
kubectl apply -f full-backup-azblob.yaml
```

The content of `full-backup-azblob.yaml` is as follows:

```yaml
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-full-backup-azblob
  namespace: test1
spec:
  backupType: full
  br:
    cluster: demo1
    # logLevel: info
    # statusAddr: ${status_addr}
    # concurrency: 4
    # rateLimit: 0
    # timeAgo: ${time}
    # checksum: true
    # sendCredToTikv: true
    # options:
    # - --lastbackupts=420134118382108673
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-full-backup-folder
    #accessTier: Hot
```

When configuring the `full-backup-azblob.yaml`, note the following:

- If you want to back up data incrementally, you only need to specify the last backup timestamp `--lastbackupts` in `spec.br.options`. For the limitations of incremental backup, refer to [Use BR to Back up and Restore Data](https://docs.pingcap.com/tidb/stable/br-usage-backup#back-up-incremental-data).
- For more information about Azure Blob Storage configuration, refer to [Azure Blob Storage fields](backup-restore-cr.md#azure-blob-storage-fields).
- Some parameters in `.spec.br` are optional, such as `logLevel` and `statusAddr`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
- `.spec.azblob.secretName`: fill in the name you specified when creating the Secret object, such as `azblob-secret`.
- For more information about the `Backup` CR fields, refer to [Backup CR fields](backup-restore-cr.md#backup-cr-fields).

#### View the snapshot backup status

After you create the `Backup` CR, TiDB Operator starts the backup automatically. You can view the backup status by running the following command:

```shell
kubectl get backup -n test1 -o wide
```

From the output, you can find the following information for the `Backup` CR named `demo1-full-backup-azblob`. The `COMMITTS` field indicates the time point of the snapshot backup:

```
NAME                       TYPE   MODE       STATUS     BACKUPPATH                                    COMMITTS             ...
demo1-full-backup-azblob   full   snapshot   Complete   azure://my-container/my-full-backup-folder/   436979621972148225   ...
```

### Log backup

You can use a `Backup` CR to describe the start and stop of a log backup task and manage the log backup data. In this section, the example shows how to create a `Backup` CR named `demo1-log-backup-azblob`. See the following detailed steps.

#### Description of the `logSubcommand` field

In the Backup Custom Resource (CR), you can use the `logSubcommand` field to control the state of a log backup task. The `logSubcommand` field supports the following commands:

- `log-start`: initiates a new log backup task or resumes a paused task. Use this command to start the log backup process or resume a task from a paused state.

- `log-pause`: temporarily pauses the currently running log backup task. After pausing, you can use the `log-start` command to resume the task.

- `log-stop`: permanently stops the log backup task. After executing this command, the Backup CR enters a stopped state and cannot be restarted.

These commands provide fine-grained control over the lifecycle of log backup tasks, enabling you to start, pause, resume, and stop tasks effectively to manage log data retention in Kubernetes environments.

#### Start log backup

1. In the `test1` namespace, create a `Backup` CR named `demo1-log-backup-azblob`.

    ```shell
    kubectl apply -f log-backup-azblob.yaml
    ```

    The content of `log-backup-azblob.yaml` is as follows:

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-azblob
      namespace: test1
    spec:
      backupMode: log
      logSubcommand: log-start
      br:
        cluster: demo1
        sendCredToTikv: true
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-log-backup-folder
        #accessTier: Hot
    ```

2. Wait for the start operation to complete:

    ```shell
    kubectl get jobs -n test1
    ```

    ```
    NAME                                       COMPLETIONS   ...
    backup-demo1-log-backup-azblob-log-start   1/1           ...
    ```

3. View the newly created `Backup` CR:

    ```shell
    kubectl get backup -n test1
    ```

    ```
    NAME                       MODE   STATUS   ....
    demo1-log-backup-azblob    log    Running  ....
    ```

#### View the log backup status

You can view the log backup status by checking the information of the `Backup` CR:

```shell
kubectl describe backup -n test1
```

From the output, you can find the following information for the `Backup` CR named `demo1-log-backup-azblob`. The `Log Checkpoint Ts` field indicates the latest point in time that can be recovered:

```
Status:
Backup Path:  azure://my-container/my-log-backup-folder/
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

You can pause a log backup task by setting the `logSubcommand` field of the Backup Custom Resource (CR) to `log-pause`. The following example shows how to pause the `demo1-log-backup-azblob` CR created in [Start log backup](#start-log-backup).

```shell
kubectl edit backup demo1-log-backup-azblob -n test1
```

To pause the log backup task, change the value of `logSubcommand` from `log-start` to `log-pause`, then save and exit the editor.

```shell
kubectl apply -f log-backup-azblob.yaml
```

The modified content is as follows:

```yaml
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-azblob
  namespace: test1
spec:
  backupMode: log
  logSubcommand: log-pause
  br:
    cluster: demo1
    sendCredToTikv: true
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-log-backup-folder
```

You can verify that the `STATUS` of the `demo1-log-backup-azblob` Backup CR changes from `Running` to `Pause`:

```shell
kubectl get backup -n test1
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-azblob    log      Pause     ....
```

#### Resume log backup

If a log backup task is paused, you can resume it by setting the `logSubcommand` field to `log-start`. The following example shows how to resume the `demo1-log-backup-azblob` CR that was paused in [Pause Log Backup](#pause-log-backup).

> **Note:**
>
> This operation applies only to tasks in the `Pause` state. You cannot resume tasks in the `Fail` or `Stopped` state.

```shell
kubectl edit backup demo1-log-backup-azblob -n test1
```

To resume the log backup task, change the value of `logSubcommand` from `log-pause` to `log-start`, then save and exit the editor. The modified content is as follows:

```yaml
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-azblob
  namespace: test1
spec:
  backupMode: log
  logSubcommand: log-start
  br:
    cluster: demo1
    sendCredToTikv: true
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-log-backup-folder
```

You can verify that the `STATUS` of the `demo1-log-backup-azblob` Backup CR changes from `Pause` to `Running`:

```shell
kubectl get backup -n test1
```

```
NAME                           MODE     STATUS    ....
demo1-log-backup-azblob        log      Running   ....
```

#### Stop log backup

You can stop a log backup task by setting the `logSubcommand` field of the Backup Custom Resource (CR) to `log-stop`. The following example shows how to stop the `demo1-log-backup-azblob` CR created in [Start log backup](#start-log-backup).

```shell
kubectl edit backup demo1-log-backup-azblob -n test1
```

Change the value of `logSubcommand` to `log-stop`, then save and exit the editor. The modified content is as follows:

```yaml
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-azblob
  namespace: test1
spec:
  backupMode: log
  logSubcommand: log-stop
  br:
    cluster: demo1
    sendCredToTikv: true
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-log-backup-folder
    #accessTier: Hot
```

You can verify that the `STATUS` of the `Backup` CR named `demo1-log-backup-azblob` changes from `Running` to `Stopped`:

```shell
kubectl get backup -n test1
```

```
NAME                       MODE   STATUS    ....
demo1-log-backup-azblob    log    Stopped   ....
```

<Tip>

`Stopped` is the terminal state for log backup. In this state, you cannot change the backup state again, but you can still clean up the log backup data.

</Tip>

#### Clean log backup data

1. Because you already created a `Backup` CR named `demo1-log-backup-azblob` when you started log backup, you can clean the log data backup by modifying the same `Backup` CR. The following example shows how to clean log backup data generated before 2022-10-10T15:21:00+08:00.

    ```shell
    kubectl edit backup demo1-log-backup-azblob -n test1
    ```

    In the last line of the CR, append `spec.logTruncateUntil: "2022-10-10T15:21:00+08:00"`. Then save and exit the editor. The modified content is as follows:

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-azblob
      namespace: test1
    spec:
      backupMode: log
      logSubcommand: log-start/log-pause/log-stop
      br:
        cluster: demo1
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
    kubectl get jobs -n test1
    ```

    ```
    NAME                                          COMPLETIONS   ...
    ...
    backup-demo1-log-backup-azblob-log-truncate   1/1           ...
    ```

3. View the `Backup` CR information:

    ```shell
    kubectl describe backup -n test1
    ```

    ```
    ...
    Log Success Truncate Until:  2022-10-10T15:21:00+08:00
    ...
    ```

    You can also view the information by running the following command:

    ```shell
    kubectl get backup -n test1 -o wide
    ```

    ```
    NAME                MODE       STATUS     ...   LOGTRUNCATEUNTIL
    demo1-log-backup-azblob    log        Complete   ...   2022-10-10T15:21:00+08:00
    ```

### Backup CR examples

<details>
<summary>Back up data of all clusters</summary>

```yaml
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-azblob
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  br:
    cluster: demo1
    sendCredToTikv: false
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
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-azblob
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.*"
  br:
    cluster: demo1
    sendCredToTikv: false
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
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-azblob
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.table1"
  br:
    cluster: demo1
    sendCredToTikv: false
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
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-azblob
  namespace: test1
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
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
```

</details>

## Delete the backup CR

If you no longer need the backup CR, you can delete it by referring to [Delete the Backup CR](backup-restore-overview.md#delete-the-backup-cr).

## Troubleshooting

If you encounter any problem during the backup process, refer to [Common Deployment Failures](deploy-failures.md).
