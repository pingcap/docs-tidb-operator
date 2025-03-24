---
title: 使用 BR 备份 TiDB 集群数据到 Azure Blob Storage
summary: 介绍如何使用 BR 备份 TiDB 集群数据到 Azure Blob Storage 上。
---

# 使用 BR 备份 TiDB 集群数据到 Azure Blob Storage

本文介绍如何将运行在 Kubernetes 环境中的 TiDB 集群数据备份到 Azure Blob Storage 上。其中包括以下两种备份方式：

- **快照备份**。使用快照备份，你可以通过[全量恢复](restore-from-azblob-using-br.md#全量恢复)将 TiDB 集群恢复到快照备份的时刻点。
- **日志备份**。使用快照备份与日志备份，你可以通过快照备份与日志备份产生的备份数据将 TiDB 集群恢复到历史任意时刻点，即 [Point-in-Time Recovery (PITR)](restore-from-azblob-using-br.md#pitr-恢复)。

本文使用的备份方式基于 TiDB Operator 的 Custom Resource Definition(CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 获取集群数据，然后再将数据上传到 Azure Blob Storage 上。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

如果你对数据备份有以下要求，可考虑使用 BR 的**快照备份**方式将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)或[定时快照备份](#定时快照备份)的方式备份至 Azure Blob Storage 上：

- 需要备份的数据量较大（大于 1 TB），而且要求备份速度较快
- 需要直接备份数据的 SST 文件（键值对）

如果你对数据备份有以下要求，可考虑使用 BR 的**日志备份**方式将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)的方式备份至 Azure Blob Storage 上（同时也需要配合快照备份的数据，来更高效地[恢复](restore-from-azblob-using-br.md#pitr-恢复)数据）：

- 需要在新集群上恢复备份集群的历史任意时刻点快照（PITR）
- 数据的 RPO 在分钟级别

如有其他备份需求，请参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

> **注意：**
>
> - 快照备份只支持 TiDB v3.1 及以上版本。
> - 日志备份只支持 TiDB v6.3 及以上版本。
> - 使用 BR 备份出的数据只能恢复到 TiDB 数据库中，无法恢复到其他数据库中。

## Ad-hoc 备份

Ad-hoc 备份支持快照备份，也支持[启动](#启动日志备份)和[停止](#停止日志备份)日志备份任务，以及[清理](#清理日志备份数据)日志备份数据等操作。

要进行 Ad-hoc 备份，你需要创建一个自定义的 `Backup` custom resource (CR) 对象来描述本次备份。创建好 `Backup` 对象后，TiDB Operator 根据这个对象自动完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

本文假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份。下面是具体的操作过程。

### 前置条件：准备 Ad-hoc 备份环境

1. 创建一个用于管理备份的 namespace，这里创建了名为 `backup-test` 的 namespace。

    ```shell
    kubectl create namespace backup-test
    ```

2. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/v1.6.1/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `backup-test` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    ```shell
    kubectl apply -f backup-rbac.yaml -n backup-test
    ```

3. 为刚创建的 namespace `backup-test` 授予远程存储访问权限，可以使用两种方式授予权限，可参考文档 [Azure 账号授权](grant-permissions-to-remote-storage.md#azure-账号授权)。创建成功后, namespace `backup-test` 就拥有了名为 `azblob-secret` 或 `azblob-secret-ad` 的 secret 对象。

    > **注意：**
    >
    > 授予的账户所拥有的角色至少拥有对 blob 修改的权限（例如[参与者](https://learn.microsoft.com/zh-cn/azure/role-based-access-control/built-in-roles#contributor)）。
    >
    > 在创建 secret 对象时，你可以自定义 secret 对象的名字。下文为了叙述简洁，统一使用名为 `azblob-secret` 的 secret 对象。

4. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要完成以下步骤。如果你使用的 TiDB 为 v4.0.8 及以上版本，请跳过这些步骤。

    1. 确保你拥有备份数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于备份前后调整 GC 时间。

    2. 创建 `backup-demo1-tidb-secret` secret 用于存放访问 TiDB 集群的用户所对应的密码。

        ```shell
        kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
        ```

### 快照备份

执行以下步骤，进行快照备份：

在 `backup-test` 这个 namespace 中创建一个名为 `demo1-full-backup-azblob` 的 `Backup` CR，用于快照备份：

```shell
kubectl apply -f full-backup-azblob.yaml
```

`full-backup-azblob.yaml` 文件内容如下：

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
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-full-backup-folder
    #accessTier: Hot
```

在配置 `full-backup-azblob.yaml` 文件时，请参考以下信息：

- 自 TiDB Operator v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考[使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。
- 关于 Azure Blob Storage 相关配置，请参考 [Azure Blob Storage 存储字段介绍](backup-restore-cr.md#azure-blob-storage-存储字段介绍)。
- `spec.br` 中的一些参数是可选的，例如 `logLevel`、`statusAddr` 等。完整的 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
- `spec.azblob.secretName`：填写你在创建 secret 对象时自定义的 secret 对象的名字，例如 `azblob-secret`。
- 如果你使用的 TiDB 为 v4.0.8 及以上版本, BR 会自动调整 `tikv_gc_life_time` 参数，不需要配置 `spec.tikvGCLifeTime` 和 `spec.from` 字段。
- 更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

#### 查看快照备份的状态

创建好 `Backup` CR 后，TiDB Operator 会根据 `Backup` CR 自动开始备份。你可以通过如下命令查看备份状态：

```shell
kubectl get backup -n backup-test -o wide
```

从上述命令的输出中，你可以找到描述名为 `demo1-full-backup-azblob` 的 `Backup` CR 的如下信息，其中 `COMMITTS` 表示快照备份的时刻点：

```
NAME                       TYPE   MODE       STATUS     BACKUPPATH                                    COMMITTS             ...
demo1-full-backup-azblob   full   snapshot   Complete   azure://my-container/my-full-backup-folder/   436979621972148225   ...
```

### 日志备份

你可以使用一个 `Backup` CR 来描述日志备份任务的启动、停止以及清理日志备份数据等操作。本节示例创建了名为 `demo1-log-backup-azblob` 的 `Backup` CR。具体操作如下所示。

#### `logSubcommand` 字段说明

在 Backup 自定义资源 (CR) 中，你可以使用 `logSubcommand` 字段控制日志备份任务的状态。`logSubcommand` 支持以下三个命令：

- `log-start`：该命令用于启动新的日志备份任务，或恢复已暂停的任务。使用此命令可以开始日志备份流程，或从暂停状态恢复任务。

- `log-pause`：该命令用于暂停当前正在进行的日志备份任务。暂停任务后，你可以使用 `log-start` 命令恢复任务。

- `log-stop`：该命令用于永久停止日志备份任务。执行此命令后，Backup CR 会进入停止状态，且无法再次启动。

这些命令提供了对日志备份任务生命周期的精细控制，支持启动、暂停、恢复和停止操作，帮助有效管理 Kubernetes 环境中的日志数据保留。

<Tip>

在 TiDB Operator v1.5.4、v1.6.0 及之前版本中，可以使用 `logStop: true/false` 字段来停止或启动日志备份任务。此字段仍然保留以确保向后兼容。

但是，请勿在同一个 Backup CR 中同时使用 `logStop` 和 `logSubcommand` 字段，这属于不支持的用法。对于 TiDB Operator v1.5.5、v1.6.1 及之后版本，推荐使用 `logSubcommand` 以确保配置清晰且一致。

</Tip>

#### 启动日志备份

1. 在 `backup-test` 这个 namespace 中创建一个名为 `demo1-log-backup-azblob` 的 `Backup` CR。

    ```shell
    kubectl apply -f log-backup-azblob.yaml
    ```

    `log-backup-azblob.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-azblob
      namespace: backup-test
    spec:
      backupMode: log
      logSubcommand: log-start
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

2. 等待启动操作完成：

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                       COMPLETIONS   ...
    backup-demo1-log-backup-azblob-log-start   1/1           ...
    ```

3. 查看新增的 `Backup` CR：

    ```shell
    kubectl get backup -n backup-test
    ```

    ```
    NAME                       MODE   STATUS   ....
    demo1-log-backup-azblob    log    Running  ....
    ```

#### 查看日志备份的状态

通过查看 `Backup` CR 的信息，可查看日志备份的状态。

```shell
kubectl describe backup -n backup-test
```

从上述命令的输出中，你可以找到描述名为 `demo1-log-backup-azblob` 的 `Backup` CR 的如下信息，其中 `Log Checkpoint Ts` 表示日志备份可恢复的最近时间点：

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

#### 暂停日志备份

你可以通过将 Backup 自定义资源 (CR) 的 `logSubcommand` 字段设置为 `log-pause` 来暂停日志备份任务。下面以暂停[启动日志备份](#启动日志备份)中创建的名为 `demo1-log-backup-azblob` 的 CR 为例。

```shell
kubectl edit backup demo1-log-backup-azblob -n backup-test
```

要暂停日志备份任务，只需将 `logSubcommand` 的值从 `log-start` 修改为 `log-pause`，然后保存并退出编辑器。

```shell
kubectl apply -f log-backup-azblob.yaml
```

修改后 `log-backup-azblob.yaml` 文件内容如下：

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-azblob
  namespace: backup-test
spec:
  backupMode: log
  logSubcommand: log-pause
  br:
    cluster: demo1
    clusterNamespace: test1
    sendCredToTikv: true
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-log-backup-folder
```

可以看到名为 `demo1-log-backup-azblob` 的 `Backup` CR 的 `STATUS` 从 `Running` 变成了 `Pause`：

```shell
kubectl get backup -n backup-test
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-azblob    log      Pause     ....
```

#### 恢复日志备份

如果日志备份任务已暂停，你可以通过将 `logSubcommand` 字段设置为 `log-start` 来恢复该任务。下面以恢复[暂停日志备份](#暂停日志备份)中已暂停的 `demo1-log-backup-azblob` CR 为例。

> **Note:**
> 
> 此操作仅适用于处于暂停状态 (`Pause`) 的任务，无法恢复状态为 `Fail` 或 `Stopped` 的任务。

```shell
kubectl edit backup demo1-log-backup-azblob -n backup-test
```

要恢复日志备份任务，只需将 `logSubcommand` 的值从 `log-pause` 更改为 `log-start`，然后保存并退出编辑器。修改后的内容如下：

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-azblob
  namespace: backup-test
spec:
  backupMode: log
  logSubcommand: log-start
  br:
    cluster: demo1
    clusterNamespace: test1
    sendCredToTikv: true
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-log-backup-folder
```

可以看到名为 `demo1-log-backup-azblob` 的 Backup CR 的 `STATUS` 从 `Paused` 状态变为 `Running`：

```shell
kubectl get backup -n backup-test
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-azblob        log      Running   ....
```

#### 停止日志备份

你可以通过将 Backup 自定义资源 (CR) 的 `logSubcommand` 字段设置为 `log-stop` 来停止日志备份。下面以停止[启动日志备份](#启动日志备份)中创建的名为 `demo1-log-backup-azblob` 的 CR 为例。

```shell
kubectl edit backup demo1-log-backup-azblob -n backup-test
```

将 `logSubcommand` 的值修改为 `log-stop`，然后保存并退出编辑器。修改后的内容如下：

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-azblob
  namespace: backup-test
spec:
  backupMode: log
  logSubcommand: log-stop
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

可以看到名为 `demo1-log-backup-azblob` 的 `Backup` CR 的 `STATUS` 从 `Running` 变成了 `Stopped`：

```shell
kubectl get backup -n backup-test
```

```
NAME                       MODE   STATUS    ....
demo1-log-backup-azblob    log    Stopped   ....
```

<Tip>

`Stopped` 是日志备份的终止状态。在此状态下，无法再次更改备份状态，但你仍然可以清理日志备份数据。

在 TiDB Operator v1.5.4、v1.6.0 及之前版本中，可以使用 `logStop: true/false` 字段来停止或启动日志备份任务。此字段仍然保留以确保向后兼容。

</Tip>

#### 清理日志备份数据

1. 由于你在开启日志备份的时候已经创建了名为 `demo1-log-backup-azblob` 的 `Backup` CR，因此可以直接更新该 `Backup` CR 的配置，来激活清理日志备份数据的操作。执行如下操作来清理 2022-10-10T15:21:00+08:00 之前的所有日志备份数据。

    ```shell
    kubectl edit backup demo1-log-backup-azblob -n backup-test
    ```

    在最后新增一行字段 `spec.logTruncateUntil: "2022-10-10T15:21:00+08:00"`，保存并退出。更新后的内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-azblob
      namespace: backup-test
    spec:
      backupMode: log
      logSubcommand: log-start/log-pause/log-stop
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

2. 等待清理操作完成：

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                          COMPLETIONS   ...
    ...
    backup-demo1-log-backup-azblob-log-truncate   1/1           ...
    ```

3. 查看 `Backup` CR 的信息：

    ```shell
    kubectl describe backup -n backup-test
    ```

    ```
    ...
    Log Success Truncate Until:  2022-10-10T15:21:00+08:00
    ...
    ```

    也可以通过以下命令查看：

    ```shell
    kubectl get backup -n backup-test -o wide
    ```

    ```
    NAME                MODE       STATUS     ...   LOGTRUNCATEUNTIL
    demo1-log-backup    log        Complete   ...   2022-10-10T15:21:00+08:00
    ```

### 压缩日志备份

对于 TiDB v9.0.0 及以上版本的集群，你可以使用 `CompactBackup` CR 将日志备份数据压缩为 SST 格式，以加速下游的日志恢复 (Point-in-time recovery, PITR)。 

本节基于前文的日志备份示例，介绍如何使用压缩日志备份。

1. 在 `backup-test` namespace 中创建一个名为 `demo1-compact-backup` 的 CompactBackup CR。

    ```shell
    kubectl apply -f compact-backup-demo1.yaml
    ```

    `compact-backup-demo1.yaml` 的内容如下：

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
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-log-backup-folder
    ```

    其中，`startTs` 和 `endTs` 指定 `demo1-compact-backup` 需要压缩的日志备份时间范围。任何包含至少一个该时间区间内写入的日志都会被送去压缩。因此，最终的压缩结果可能包含该时间范围之外的写入数据。

    `azblob` 设置应与需要压缩的日志备份的存储设置相同，`CompactBackup` 会读取相应地址的日志文件并进行压缩。

#### 查看压缩日志备份状态

创建 `CompactBackup` CR 后，TiDB Operator 会自动开始压缩日志备份。你可以运行以下命令查看备份状态：

```shell
kubectl get cpbk -n backup-test
```

从上述命令的输出中，你可以找到描述名为 `demo1-compact-backup` 的 `CompactBackup` CR 的信息，输出示例如下：

```
NAME                   STATUS                   PROGRESS                                     MESSAGE
demo1-compact-backup   Complete   [READ_META(17/17),COMPACT_WORK(1291/1291)]   
```

如果 `STATUS` 字段显示为 `Complete` 则代表压缩日志备份已经完成。

### 备份示例

<details>
<summary>备份全部集群数据</summary>

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
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
```

</details>

<details>
<summary>备份单个数据库的数据</summary>

以下示例中，备份 `db1` 数据库的数据。

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
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
```

</details>

<details>
<summary>备份单张表的数据</summary>

以下示例中，备份 `db1.table1` 表的数据。

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
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
```

</details>

<details>
<summary>使用表库过滤功能备份多张表的数据</summary>

以下示例中，备份 `db1.table1` 表 和  `db1.table2` 表的数据。

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
  azblob:
    secretName: azblob-secret-ad
    container: my-container
    prefix: my-folder
```

</details>

## 定时快照备份

你可以通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时快照备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次快照备份，定时快照备份底层通过 Ad-hoc 快照备份来实现。

### 前置条件：准备定时快照备份环境

同[准备 Ad-hoc 备份环境](#前置条件准备-ad-hoc-备份环境)。

### 执行快照备份

依据准备 Ad-hoc 备份环境时所选择的远程存储访问授权方式，你需要使用下面对应的方法将数据定时备份到 Azure Blob Storage 上：

+ 方法 1：如果通过了访问密钥的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时快照备份：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-scheduler-azblob.yaml
    ```

    `backup-scheduler-azblob.yaml` 文件内容如下：

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
       azblob:
          secretName: azblob-secret-ad
          container: my-container
          prefix: my-folder
    ```

+ 方法 2：如果通过了 Azure AD 的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时快照备份：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-scheduler-azblob.yaml
    ```

    `backup-scheduler-azblob.yaml` 文件内容如下：

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
        azblob:
          secretName: azblob-secret-ad
          container: my-container
          prefix: my-folder
    ```

从以上 `backup-scheduler-azblob.yaml` 文件配置示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。

- 关于 `backupSchedule` 独有的配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。
- `backupTemplate` 用于指定集群及远程存储相关的配置，字段和 Backup CR 中的 `spec` 一样，详细介绍可参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

定时快照备份创建完成后，可以通过以下命令查看定时快照备份的状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bks -n backup-test -o wide
```

查看定时快照备份下面所有的备份条目：

{{< copyable "shell-regular" >}}

```shell
kubectl get backup -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-azblob -n backup-test
```

## 集成管理定时快照备份和日志备份

`BackupSchedule` CR 可以集成管理 TiDB 集群的定时快照备份和日志备份，通过设置备份的保留时间可以定期回收快照备份和日志备份，且能保证在保留期内可以通过快照备份和日志备份进行 PiTR 恢复。本节示例创建了名为 `integrated-backup-schedule-azblob` 的 `BackupSchedule` CR 为例，其中访问 Azure 远程存储的方式参考[Azure 账号授权](grant-permissions-to-remote-storage.md#azure-账号授权)，具体操作如下所示。

### 前置条件：准备定时快照备份环境

同[准备 Ad-hoc 备份环境](#前置条件准备-ad-hoc-备份环境)。

### 创建 `BackupSchedule`

1. 在 `backup-test` 这个 namespace 中创建一个名为 `integrated-backup-schedule-azblob` 的 `BackupSchedule` CR。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f integrated-backup-scheduler-azblob.yaml
    ```

    `integrated-backup-scheduler-azblob` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: integrated-backup-schedule-azblob
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
        azblob:
          secretName: azblob-secret
          container: my-container
          prefix: schedule-backup-folder-snapshot
          #accessTier: Hot
      logBackupTemplate:
        backupMode: log
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        azblob:
          secretName: azblob-secret
          container: my-container
          prefix: schedule-backup-folder-log
          #accessTier: Hot
    ```

    以上 `integrated-backup-scheduler-azblob.yaml` 文件配置示例中，`backupSchedule` 的配置由三部分组成：`backupSchedule` 独有的配置，快照备份配置 `backupTemplate`，日志备份配置 `logBackupTemplate`。

    关于 `backupSchedule` 配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。

2. `backupSchedule` 创建完成后，可以通过以下命令查看定时快照备份的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bks -n backup-test -o wide
    ```

    日志备份会随着 `backupSchedule` 创建，可以通过如下命令查看 `backupSchedule` 的 `status.logBackup`，即日志备份名称。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl describe bks integrated-backup-schedule-azblob -n backup-test
    ```

3. 在进行集群恢复时，需要指定备份的路径，可以通过如下命令查看定时快照备份下面所有的备份条目，在命令输出中 `MODE` 为 `snapshot` 的条目为快照备份，`MODE` 为 `log` 的条目为日志备份。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=integrated-backup-schedule-azblob -n backup-test
    ```

    ```
    NAME                                                       MODE       STATUS    ....
    integrated-backup-schedule-azblob-2023-03-08t02-48-00      snapshot   Complete  ....  
    log-integrated-backup-schedule-azblob                      log        Running   ....
    ```

## 集成定时快照备份、日志备份和压缩日志备份

为了加快下游恢复速度，可以在 `BackupSchedule` CR 中添加压缩日志备份。压缩日志备份可以定期压缩远程存储中的日志备份文件。你必须先启用日志备份，才能使用压缩日志备份。本节基于上一节内容进行扩展。

### 前置条件：准备定时快照备份环境

同[准备 Ad-hoc 备份环境](#前置条件准备-ad-hoc-备份环境)。

### 创建 `BackupSchedule`

1. 在 `backup-test` 这个 namespace 中创建一个名为 `integrated-backup-schedule-azblob` 的 `BackupSchedule` CR。

    ```shell
    kubectl apply -f integrated-backup-scheduler-azblob.yaml
    ```

    `integrated-backup-scheduler-azblob` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: integrated-backup-schedule-azblob
      namespace: backup-test
    spec:
      maxReservedTime: "3h"
      schedule: "* */2 * * *"
      compactInterval: "1h"
      backupTemplate:
        backupType: full
        cleanPolicy: Delete
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        azblob:
          secretName: azblob-secret
          container: my-container
          prefix: schedule-backup-folder-snapshot
          #accessTier: Hot
      logBackupTemplate:
        backupMode: log
        br:
          cluster: demo1
          clusterNamespace: test1
          sendCredToTikv: true
        azblob:
          secretName: azblob-secret
          container: my-container
          prefix: schedule-backup-folder-log
          #accessTier: Hot
    ```

    以上 `integrated-backup-scheduler-azblob.yaml` 文件配置示例中，`backupSchedule` 配置基于上一节内容，新增了 `compactBackup` 相关设置，主要改动如下：
    
    - 新增 `BackupSchedule.spec.compactInterval` 字段，用于指定日志压缩备份的时间间隔。建议不要超过定时快照备份的间隔，并控制在定时快照备份间隔的二分之一至三分之一之间。
    
    - 新增 `BackupSchedule.spec.compactBackupTemplate` 字段。请确保 `BackupSchedule.spec.compactBackupTemplate.azblob` 配置与 `BackupSchedule.spec.logBackupTemplate.azblob` 保持一致。

    关于 `backupSchedule` 配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。

2. `backupSchedule` 创建完成后，可以通过以下命令查看定时快照备份的状态：

    ```shell
    kubectl get bks -n backup-test -o wide
    ```

    压缩日志备份会随着 `backupSchedule` 创建，可以通过如下命令查看 `CompactBackup` CR 的信息。

    ```shell
    kubectl get cpbk -n backup-test
    ```

## 删除备份的 Backup CR

如果你不再需要已备份的 Backup CR，请参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
