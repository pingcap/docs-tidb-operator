---
title: 使用 BR 备份 TiDB 集群数据到兼容 S3 的存储
summary: 介绍如何使用 BR 备份 TiDB 集群数据到兼容 Amazon S3 的存储。
---

# 使用 BR 备份 TiDB 集群数据到兼容 S3 的存储

本文介绍如何将运行在 AWS Kubernetes 环境中的 TiDB 集群数据备份到 AWS 的存储上。其中包括以下两种备份方式：

- **快照备份**。使用快照备份，你可以通过[全量恢复](restore-from-aws-s3-using-br.md#全量恢复)将 TiDB 集群恢复到快照备份的时刻点。
- **日志备份**。使用快照备份与日志备份，你可以通过快照备份与日志备份产生的备份数据将 TiDB 集群恢复到历史任意时刻点，即 [Point-in-Time Recovery (PITR)](restore-from-aws-s3-using-br.md#pitr-恢复)。

本文使用的备份方式基于 TiDB Operator 的 Custom Resource Definition (CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 获取集群数据，然后再将数据上传到 AWS 的存储上。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

如果你对数据备份有以下要求，可考虑使用 BR 的**快照备份**方式将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)或[定时快照备份](#定时快照备份)的方式备份至兼容 S3 的存储上：

- 需要备份的数据量较大（大于 1 TiB），而且要求备份速度较快
- 需要直接备份数据的 SST 文件（键值对）

如果你对数据备份有以下要求，可考虑使用 BR 的**日志备份**方式将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)的方式备份至兼容 S3 的存储上（同时也需要配合快照备份的数据，来更高效地[恢复](restore-from-aws-s3-using-br.md#pitr-恢复)数据）：

- 需要在新集群上恢复备份集群的历史任意时刻点快照 (PITR)
- 数据的 RPO 在分钟级别

如有其他备份需求，请参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

> **注意：**
>
> - 快照备份只支持 TiDB v3.1 及以上版本。
> - 日志备份只支持 TiDB v6.3 及以上版本。
> - 使用 BR 备份出的数据只能恢复到 TiDB 数据库中，无法恢复到其他数据库中。

## Ad-hoc 备份

Ad-hoc 备份支持快照备份，也支持[启动](#启动日志备份)和[停止](#停止日志备份)日志备份任务，以及[清理](#清理日志备份数据)日志备份数据等操作。

要进行 Ad-hoc 备份，你需要创建一个自定义的 `Backup` Custom Resource (CR) 对象来描述本次备份。创建好 `Backup` 对象后，TiDB Operator 根据这个对象自动完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

本文假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份。下面是具体的操作过程。

### 前置条件：准备 Ad-hoc 备份环境

> **注意：**
>
> - BR 使用的 ServiceAccount 名称为固定值，必须为 `tidb-backup-manager`。
> - 从 TiDB Operator v2 开始，`Backup` 和 `Restore` 等资源的 `apiGroup` 从 `pingcap.com` 修改为 `br.pingcap.com`。

1. 将以下内容保存为 `backup-rbac.yaml` 文件，用于创建所需的 RBAC 资源：

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
    ```

2. 执行以下命令在 namespace `test1` 中创建备份需要的 RBAC 相关资源：

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

3. 为 namespace `test1` 授予远程存储访问权限：

    - 如果使用 Amazon S3 来备份集群，可以使用三种方式授予权限，可参考文档 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。
    - 如果使用其他兼容 S3 的存储来备份集群，例如 Ceph、MinIO，可以使用 AccessKey 和 SecretKey 授权的方式，可参考文档[通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-accesskey-和-secretkey-授权)。

### 快照备份

根据上一步选择的远程存储访问授权方式，你需要使用下面对应的方法将数据导出到兼容 S3 的存储上：

+ 方法 1：如果通过了 accessKey 和 secretKey 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据：

    ```shell
    kubectl apply -f full-backup-s3.yaml
    ```

    `full-backup-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-full-backup-s3
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
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-full-backup-folder
    ```

+ 方法 2：如果通过了 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据：

    ```shell
    kubectl apply -f full-backup-s3.yaml
    ```

    `full-backup-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-full-backup-s3
      namespace: test1
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      backupType: full
      br:
        cluster: demo1
        sendCredToTikv: false
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # options:
        # - --lastbackupts=420134118382108673
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-full-backup-folder
    ```

+ 方法 3：如果通过了 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据：

    ```shell
    kubectl apply -f full-backup-s3.yaml
    ```

    `full-backup-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-full-backup-s3
      namespace: test1
    spec:
      backupType: full
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo1
        sendCredToTikv: false
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # options:
        # - --lastbackupts=420134118382108673
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-full-backup-folder
    ```

在配置 `full-backup-s3.yaml` 文件时，请参考以下信息：

- 自 TiDB Operator v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考[使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。
- Amazon S3 的 `acl`、`endpoint`、`storageClass` 配置项均可以省略。兼容 S3 的存储相关配置，请参考 [S3 存储字段介绍](backup-restore-cr.md#s3-存储字段介绍)。
- `.spec.br` 中的一些参数是可选的，例如 `logLevel`、`statusAddr` 等。完整的 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
- 如果你使用的 TiDB 为 v4.0.8 及以上版本，BR 会自动调整 `tikv_gc_life_time` 参数，不需要配置 `spec.tikvGCLifeTime` 和 `spec.from` 字段。
- 更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

#### 查看快照备份的状态

创建好 `Backup` CR 后，TiDB Operator 会根据 `Backup` CR 自动开始备份。你可以通过如下命令查看备份状态：

```shell
kubectl get backup -n test1 -o wide
```

从上述命令的输出中，你可以找到描述名为 `demo1-full-backup-s3` 的 `Backup` CR 的如下信息，其中 `COMMITTS` 表示快照备份的时刻点：

```
NAME                   TYPE   MODE       STATUS     BACKUPPATH                              COMMITTS             ...
demo1-full-backup-s3   full   snapshot   Complete   s3://my-bucket/my-full-backup-folder/   436979621972148225   ...
```

### 日志备份

你可以使用一个 `Backup` CR 来描述日志备份任务的启动、停止以及清理日志备份数据等操作。日志备份对远程存储访问授权方式与快照备份一致。本节示例创建了名为 `demo1-log-backup-s3` 的 `Backup` CR，对远程存储访问授权方式仅以通过 accessKey 和 secretKey 的方式为例，具体操作如下所示。

#### `logSubcommand` 字段说明

在 Backup 自定义资源 (CR) 中，你可以使用 `logSubcommand` 字段控制日志备份任务的状态。`logSubcommand` 支持以下三个命令：

- `log-start`：该命令用于启动新的日志备份任务，或恢复已暂停的任务。使用此命令可以开始日志备份流程，或从暂停状态恢复任务。

- `log-pause`：该命令用于暂停当前正在进行的日志备份任务。暂停任务后，你可以使用 `log-start` 命令恢复任务。

- `log-stop`：该命令用于永久停止日志备份任务。执行此命令后，Backup CR 会进入停止状态，且无法再次启动。

这些命令提供了对日志备份任务生命周期的精细控制，支持启动、暂停、恢复和停止操作，帮助有效管理 Kubernetes 环境中的日志数据保留。

<Tip>

在 TiDB Operator v1.5.4、v1.6.0 及之前版本中，可以使用 `logStop: true/false` 字段来停止或启动日志备份任务。此字段在 TiDB Operator v2 中不再保留，推荐使用 `logSubcommand` 以确保配置清晰且一致。

</Tip>

#### 启动日志备份

1. 在 `test1` 这个 namespace 中创建一个名为 `demo1-log-backup-s3` 的 `Backup` CR。

    ```shell
    kubectl apply -f log-backup-s3.yaml
    ```

    `log-backup-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-s3
      namespace: test1
    spec:
      backupMode: log
      br:
        cluster: demo1
        sendCredToTikv: true
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-log-backup-folder
    ```

2. 等待启动操作完成：

    ```shell
    kubectl get jobs -n test1
    ```

    ```
    NAME                                   COMPLETIONS   ...
    backup-demo1-log-backup-s3-log-start   1/1           ...
    ```

3. 查看新增的 `Backup` CR：

    ```shell
    kubectl get backup -n test1
    ```

    ```
    NAME                       MODE   STATUS   ....
    demo1-log-backup-s3        log    Running  ....
    ```

#### 查看日志备份的状态

通过查看 `Backup` CR 的信息，可查看日志备份的状态。

```shell
kubectl describe backup -n test1
```

从上述命令的输出中，你可以找到描述名为 `demo1-log-backup-s3` 的 `Backup` CR 的如下信息，其中 `Log Checkpoint Ts` 表示日志备份可恢复的最近时间点：

```
Status:
Backup Path:  s3://my-bucket/my-log-backup-folder/
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

你可以通过将 Backup 自定义资源 (CR) 的 `logSubcommand` 字段设置为 `log-pause` 来暂停日志备份任务。下面以暂停[启动日志备份](#启动日志备份)中创建的名为 `demo1-log-backup-s3` 的 CR 为例。

```shell
kubectl edit backup demo1-log-backup-s3 -n test1
```

要暂停日志备份任务，只需将 `logSubcommand` 的值从 `log-start` 修改为 `log-pause`，然后保存并退出编辑器。修改后的内容如下：

```yaml
---
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-s3
  namespace: test1
spec:
  backupMode: log
  logSubcommand: log-pause
  br:
    cluster: demo1
    sendCredToTikv: true
  s3:
    provider: aws
    secretName: s3-secret
    region: us-west-1
    bucket: my-bucket
    prefix: my-log-backup-folder
```

可以看到名为 `demo1-log-backup-s3` 的 `Backup` CR 的 `STATUS` 从 `Running` 变成了 `Pause`：

```shell
kubectl get backup -n test1
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-s3        log      Pause     ....
```

#### 恢复日志备份

如果日志备份任务已暂停，你可以通过将 `logSubcommand` 字段设置为 `log-start` 来恢复该任务。下面以恢复[暂停日志备份](#暂停日志备份)中已暂停的 `demo1-log-backup-s3` CR 为例。

> **Note:**
>
> 此操作仅适用于处于暂停状态 (`Pause`) 的任务，无法恢复状态为 `Fail` 或 `Stopped` 的任务。

```shell
kubectl edit backup demo1-log-backup-s3 -n test1
```

要恢复日志备份任务，只需将 `logSubcommand` 的值从 `log-pause` 更改为 `log-start`，然后保存并退出编辑器。修改后的内容如下：

```yaml
---
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-s3
  namespace: test1
spec:
  backupMode: log
  logSubcommand: log-start
  br:
    cluster: demo1
    sendCredToTikv: true
  s3:
    provider: aws
    secretName: s3-secret
    region: us-west-1
    bucket: my-bucket
    prefix: my-log-backup-folder
```

可以看到名为 `demo1-log-backup-s3` 的 Backup CR 的 `STATUS` 从 `Paused` 状态变为 `Running`：

```shell
kubectl get backup -n test1
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-s3        log      Running   ....
```

#### 停止日志备份

你可以通过将 Backup 自定义资源 (CR) 的 `logSubcommand` 字段设置为 `log-stop` 来停止日志备份。下面以停止[启动日志备份](#启动日志备份)中创建的名为 `demo1-log-backup-s3` 的 CR 为例。

```shell
kubectl edit backup demo1-log-backup-s3 -n test1
```

将 `logSubcommand` 的值修改为 `log-stop`，然后保存并退出编辑器。修改后的内容如下：

```yaml
---
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-s3
  namespace: test1
spec:
  backupMode: log
  logSubcommand: log-stop
  br:
    cluster: demo1
    sendCredToTikv: true
  s3:
    provider: aws
    secretName: s3-secret
    region: us-west-1
    bucket: my-bucket
    prefix: my-log-backup-folder
```

可以看到名为 `demo1-log-backup-s3` 的 `Backup` CR 的 `STATUS` 从 `Running` 变成了 `Stopped`：

```shell
kubectl get backup -n test1
```

```
NAME                       MODE     STATUS    ....
demo1-log-backup-s3        log      Stopped   ....
```

<Tip>

`Stopped` 是日志备份的终止状态。在此状态下，无法再次更改备份状态，但你仍然可以清理日志备份数据。

在 TiDB Operator v1.5.4、v1.6.0 及之前版本中，可以使用 `logStop: true/false` 字段来停止或启动日志备份任务。此字段仍然保留以确保向后兼容。

</Tip>

#### 清理日志备份数据

1. 由于你在开启日志备份的时候已经创建了名为 `demo1-log-backup-s3` 的 `Backup` CR，因此可以直接更新该 `Backup` CR 的配置，来激活清理日志备份数据的操作。执行如下操作来清理 2022-10-10T15:21:00+08:00 之前的所有日志备份数据。

    ```shell
    kubectl edit backup demo1-log-backup-s3 -n test1
    ```

    在最后新增一行字段 `spec.logTruncateUntil: "2022-10-10T15:21:00+08:00"`，保存并退出。更新后的内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-s3
      namespace: test1
    spec:
      backupMode: log
      logSubcommand: log-start/log-pause/log-stop
      br:
        cluster: demo1
        sendCredToTikv: true
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-log-backup-folder
      logTruncateUntil: "2022-10-10T15:21:00+08:00"
    ```

2. 等待清理操作完成：

    ```shell
    kubectl get jobs -n test1
    ```

    ```
    NAME                                      COMPLETIONS   ...
    ...
    backup-demo1-log-backup-s3-log-truncate   1/1           ...
    ```

3. 查看 `Backup` CR 的信息：

    ```shell
    kubectl describe backup -n test1
    ```

    ```
    ...
    Log Success Truncate Until:  2022-10-10T15:21:00+08:00
    ...
    ```

    也可以通过以下命令查看：

    ```shell
    kubectl get backup -n test1 -o wide
    ```

    ```
    NAME                   MODE       STATUS     ...   LOGTRUNCATEUNTIL
    demo1-log-backup-s3    log        Stopped    ...   2022-10-10T15:21:00+08:00
    ```

### 压缩日志备份

对于 TiDB v9.0.0 及以上版本的集群，你可以使用 `CompactBackup` CR 将日志备份数据压缩为 SST 格式，以加速下游的日志恢复 (Point-in-time recovery, PITR)。

本节基于前文的日志备份示例，介绍如何使用压缩日志备份。

1. 在 `test1` namespace 中创建一个名为 `demo1-compact-backup` 的 CompactBackup CR。

    ```shell
    kubectl apply -f compact-backup-demo1.yaml
    ```

    `compact-backup-demo1.yaml` 的内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: CompactBackup
    metadata:
      name: demo1-compact-backup
      namespace: test1
    spec:
      startTs: "***"
      endTs: "***"
      concurrency: 8
      maxRetryTimes: 2
      br:
        cluster: demo1
        sendCredToTikv: true
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-log-backup-folder
    ```

    其中，`startTs` 和 `endTs` 指定 `demo1-compact-backup` 需要压缩的日志备份时间范围。任何包含至少一个该时间区间内写入的日志都会被送去压缩。因此，最终的压缩结果可能包含该时间范围之外的写入数据。

    `s3` 设置应与需要压缩的日志备份的存储设置相同，`CompactBackup` 会读取相应地址的日志文件并进行压缩。

#### 查看压缩日志备份状态

创建 `CompactBackup` CR 后，TiDB Operator 会自动开始压缩日志备份。你可以运行以下命令查看备份状态：

```shell
kubectl get cpbk -n test1
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
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  br:
    cluster: demo1
    sendCredToTikv: false
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

<details>
<summary>备份单个数据库的数据</summary>

以下示例中，备份 `db1` 数据库的数据。

```yaml
---
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.*"
  br:
    cluster: demo1
    sendCredToTikv: false
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

<details>
<summary>备份单张表的数据</summary>

以下示例中，备份 `db1.table1` 表的数据。

```yaml
---
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.table1"
  br:
    cluster: demo1
    sendCredToTikv: false
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

<details>
<summary>使用表库过滤功能备份多张表的数据</summary>

以下示例中，备份 `db1.table1` 表 和  `db1.table2` 表的数据。

```yaml
---
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
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
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

## 定时快照备份

你可以通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时快照备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次快照备份，定时快照备份底层通过 Ad-hoc 快照备份来实现。

### 前置条件：准备定时快照备份环境

同[准备 Ad-hoc 备份环境](#前置条件准备-ad-hoc-备份环境)。

### 执行快照备份

依据准备 Ad-hoc 备份环境时所选择的远程存储访问授权方式，你需要使用下面对应的方法将数据定时备份到 Amazon S3 存储上：

+ 方法 1：如果通过了 accessKey 和 secretKey 的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时快照备份：

    ```shell
    kubectl apply -f backup-scheduler-aws-s3.yaml
    ```

    `backup-scheduler-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-s3
      namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        backupType: full
        # Clean outdated backup data based on maxBackups or maxReservedTime. If not configured, the default policy is Retain
        # cleanPolicy: Delete
        br:
          cluster: demo1
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
          prefix: my-folder
    ```

+ 方法 2：如果通过了 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时快照备份：

    ```shell
    kubectl apply -f backup-scheduler-aws-s3.yaml
    ```

    `backup-scheduler-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-s3
      namespace: test1
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        backupType: full
        # Clean outdated backup data based on maxBackups or maxReservedTime. If not configured, the default policy is Retain
        # cleanPolicy: Delete
        br:
          cluster: demo1
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
          prefix: my-folder
    ```

+ 方法 3：如果通过了 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时快照备份：

    ```shell
    kubectl apply -f backup-scheduler-aws-s3.yaml
    ```

    `backup-scheduler-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-s3
      namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        backupType: full
        serviceAccount: tidb-backup-manager
        # Clean outdated backup data based on maxBackups or maxReservedTime. If not configured, the default policy is Retain
        # cleanPolicy: Delete
        br:
          cluster: demo1
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
          prefix: my-folder
    ```

以上 `backup-scheduler-aws-s3.yaml` 文件配置示例中，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。

- 关于 `backupSchedule` 独有的配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。
- `backupTemplate` 用于指定集群及远程存储相关的配置，字段和 Backup CR 中的 `spec` 一样，详细介绍可参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

定时快照备份创建完成后，可以通过以下命令查看定时快照备份的状态：

```shell
kubectl get bks -n test1 -o wide
```

在进行集群恢复时，需要指定备份的路径，可以通过如下命令查看定时快照备份下面所有的备份条目，这些备份的名称以定时快照备份名称为前缀：

```shell
kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-s3 -n test1
```

## 集成管理定时快照备份和日志备份

`BackupSchedule` CR 可以集成管理 TiDB 集群的定时快照备份和日志备份。通过设置备份的保留时间，可以定期回收快照备份和日志备份，且能保证在保留期内可以通过快照备份和日志备份进行 PITR 恢复。

本节示例创建了名为 `integrated-backup-schedule-s3` 的 `BackupSchedule` CR，使用 accessKey 和 secretKey 的方式为例对远程存储进行访问授权，详细的授权方式参考[AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。具体操作如下所示。

### 前置条件：准备定时快照备份环境

同[准备 Ad-hoc 备份环境](#前置条件准备-ad-hoc-备份环境)。

### 创建 `BackupSchedule`

1. 在 `test1` 这个 namespace 中创建一个名为 `integrated-backup-schedule-s3` 的 `BackupSchedule` CR。

    ```shell
    kubectl apply -f integrated-backup-schedule-s3.yaml
    ```

    `integrated-backup-schedule-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: integrated-backup-schedule-s3
      namespace: test1
    spec:
      maxReservedTime: "3h"
      schedule: "* */2 * * *"
      backupTemplate:
        backupType: full
        cleanPolicy: Delete
        br:
          cluster: demo1
          sendCredToTikv: true
        s3:
          provider: aws
          secretName: s3-secret
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder-snapshot
      logBackupTemplate:
        backupMode: log
        br:
          cluster: demo1
          sendCredToTikv: true
        s3:
          provider: aws
          secretName: s3-secret
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder-log
    ```

    以上 `integrated-backup-schedule-s3.yaml` 文件配置示例中，`backupSchedule` 的配置由三部分组成：`backupSchedule` 独有的配置，快照备份配置 `backupTemplate`，日志备份配置 `logBackupTemplate`。

    关于 `backupSchedule` 配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。

2. `backupSchedule` 创建完成后，可以通过以下命令查看定时快照备份的状态：

    ```shell
    kubectl get bks -n test1 -o wide
    ```

    日志备份会随着 `backupSchedule` 创建，可以通过如下命令查看 `backupSchedule` 的 `status.logBackup`，即日志备份名称。

    ```shell
    kubectl describe bks integrated-backup-schedule-s3 -n test1
    ```

3. 在进行集群恢复时，需要指定备份的路径。你可以通过如下命令查看定时快照备份下面所有的备份条目，在命令输出中 `MODE` 为 `snapshot` 的条目为快照备份，`MODE` 为 `log` 的条目为日志备份。

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=integrated-backup-schedule-s3 -n test1
    ```

    ```
    NAME                                                   MODE       STATUS    ....
    integrated-backup-schedule-s3-2023-03-08t02-45-00      snapshot   Complete  ....
    log-integrated-backup-schedule-s3                      log        Running   ....
    ```

## 集成定时快照备份、日志备份和压缩日志备份

为了加快下游恢复速度，可以在 `BackupSchedule` CR 中添加压缩日志备份。压缩日志备份可以定期压缩远程存储中的日志备份文件。你必须先启用日志备份，才能使用压缩日志备份。本节基于上一节内容进行扩展。

### 前置条件：准备定时快照备份环境

同[准备 Ad-hoc 备份环境](#前置条件准备-ad-hoc-备份环境)。

### 创建 `BackupSchedule`

1. 在 `test1` 这个 namespace 中创建一个名为 `integrated-backup-schedule-s3` 的 `BackupSchedule` CR。

    ```shell
    kubectl apply -f integrated-backup-schedule-s3.yaml
    ```

    `integrated-backup-schedule-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: integrated-backup-schedule-s3
      namespace: test1
    spec:
      maxReservedTime: "3h"
      schedule: "* */2 * * *"
      compactInterval: "1h"
      backupTemplate:
        backupType: full
        cleanPolicy: Delete
        br:
          cluster: demo1
          sendCredToTikv: true
        s3:
          provider: aws
          secretName: s3-secret
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder-snapshot
      logBackupTemplate:
        backupMode: log
        br:
          cluster: demo1
          sendCredToTikv: true
        s3:
          provider: aws
          secretName: s3-secret
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder-log
      compactBackupTemplate:
        br:
          cluster: demo1
          sendCredToTikv: true
        s3:
          provider: aws
          secretName: s3-secret
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder-log
    ```

    以上 `integrated-backup-schedule-s3.yaml` 文件配置示例中，`backupSchedule` 配置基于上一节内容，新增了 `compactBackup` 相关设置，主要改动如下：

    - 新增 `BackupSchedule.spec.compactInterval` 字段，用于指定日志压缩备份的时间间隔。建议不要超过定时快照备份的间隔，并控制在定时快照备份间隔的二分之一至三分之一之间。

    - 新增 `BackupSchedule.spec.compactBackupTemplate` 字段。请确保 `BackupSchedule.spec.compactBackupTemplate.s3` 配置与 `BackupSchedule.spec.logBackupTemplate.s3` 保持一致。

    关于 `backupSchedule` 配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。

2. `backupSchedule` 创建完成后，可以通过以下命令查看定时快照备份的状态：

    ```shell
    kubectl get bks -n test1 -o wide
    ```

    压缩日志备份会随着 `backupSchedule` 创建，可以通过如下命令查看 `CompactBackup` CR 的信息。

    ```shell
    kubectl get cpbk -n test1
    ```

## 删除备份的 Backup CR

如果你不再需要已备份的 Backup CR，请参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
