---
title: 使用 BR 备份 TiDB 集群到 GCS
summary: 介绍如何使用 BR 备份 TiDB 集群到 Google Cloud Storage (GCS)。
---

# 使用 BR 备份 TiDB 集群到 GCS

本文介绍如何将运行在 Kubernetes 环境中的 TiDB 集群数据备份到 Google Cloud Storage (GCS) 的存储上。其中包括以下两种备份方式：

- **快照备份**。使用快照备份，你可以通过[全量恢复](restore-from-gcs-using-br.md#全量恢复)将 TiDB 集群恢复到快照备份的时刻点。
- **日志备份**。使用快照备份与日志备份，你可以通过快照备份与日志备份产生的备份数据将 TiDB 集群恢复到历史任意时刻点，即 [Point-in-Time Recovery (PITR)](restore-from-gcs-using-br.md#pitr-恢复)。

本文使用的备份方式基于 TiDB Operator 的 Custom Resource Definition (CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 获取集群数据，然后再将数据上传到远端 GCS。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

如果你对数据备份有以下要求，可考虑使用 BR 的**快照备份**方式将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)或[定时快照备份](#定时快照备份)的方式备份至 GCS 上：

- 需要备份的数据量较大（大于 1 TB），而且要求备份速度较快
- 需要直接备份数据的 SST 文件（键值对）

如果你对数据备份有以下要求，可考虑使用 BR 的**日志备份**方式将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)的方式备份至 GCS 上（同时也需要配合快照备份的数据，来更高效地[恢复](restore-from-gcs-using-br.md#pitr-恢复)数据）：

- 需要在新集群上恢复备份集群的历史任意时刻点快照（PITR）
- 数据的 RPO 在分钟级别

如有其他备份需求，请参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

> **注意：**
>
> - 快照备份只支持 TiDB v3.1 及以上版本。
> - 日志备份只支持 TiDB v6.2 及以上版本。
> - 使用 BR 备份出的数据只能恢复到 TiDB 数据库中，无法恢复到其他数据库中。

## Ad-hoc 备份

Ad-hoc 备份支持快照备份，也支持[启动](#启动日志备份)和[停止](#停止日志备份)日志备份任务，以及[清理](#清理日志备份数据)日志备份数据等操作。

要进行 Ad-hoc 备份，你需要创建一个自定义的 `Backup` custom resource (CR) 对象来描述本次备份。创建好 `Backup` 对象后，TiDB Operator 根据这个对象自动完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

本文档假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份。下面是具体的操作过程。

### 前置条件：准备 Ad-hoc 备份环境

1. 创建一个用于管理备份的 namespace，这里创建了名为 `backup-test` 的 namespace。

    ```shell
    kubectl create namespace backup-test
    ```

2. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `backup-test` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n backup-test
    ```

3. 为刚创建的 namespace `backup-test` 授予远程存储访问权限。

    参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#gcs-账号授权)，授权访问 GCS 远程存储。

4. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要完成以下步骤。如果你使用的 TiDB 为 v4.0.8 及以上版本，请跳过这些步骤。

    1. 确保你拥有备份数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于备份前后调整 GC 时间。

    2. 创建 `backup-demo1-tidb-secret` secret 用于存放访问 TiDB 集群的 root 账号和密钥。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
        ```

### 快照备份

1. 创建 `Backup` CR，将数据备份到 GCS：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f full-backup-gcs.yaml
    ```

    `full-backup-gcs.yaml` 文件内容如下：

    {{< copyable "" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-full-backup-gcs
      namespace: backup-test
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
        bucket: my-bucket
        prefix: my-full-backup-folder
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

    在配置 `full-backup-gcs.yaml` 文件时，请参考以下信息：

    - 自 v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考[使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。
    - `.spec.br` 中的一些参数是可选的，例如 `logLevel`、`statusAddr` 等。完整的 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
    - `spec.gcs` 中的一些参数为可选项，如 `location`、`objectAcl`、`storageClass`。GCS 存储相关配置参考 [GCS 存储字段介绍](backup-restore-cr.md#gcs-存储字段介绍)。
    - 如果你使用的 TiDB 为 v4.0.8 及以上版本, BR 会自动调整 `tikv_gc_life_time` 参数，不需要配置 `spec.tikvGCLifeTime` 和 `spec.from` 字段。
    - 更多 `Backup` CR 字段的详细解释，请参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

#### 查看快照备份的状态

创建好 `Backup` CR 后，TiDB Operator 会根据 `Backup` CR 自动开始备份。你可以通过如下命令查看备份状态：

```shell
kubectl get backup -n backup-test -o wide
```

从上述命令的输出中，你可以找到描述名为 `demo1-full-backup-gcs` 的 `Backup` CR 的如下信息，其中 `COMMITTS` 表示快照备份的时刻点：

```
NAME                    TYPE   MODE       STATUS     BACKUPPATH                               COMMITTS             ...
demo1-full-backup-gcs   full   snapshot   Complete   gcs://my-bucket/my-full-backup-folder/   436979621972148225   ...
```

### 日志备份

你可以使用一个 `Backup` CR 来描述日志备份任务的启动、停止以及清理日志备份数据等操作。日志备份对远程存储访问授权方式与快照备份一致。本节示例创建了名为 `demo1-log-backup-gcs` 的 `Backup` CR，具体操作如下所示。

#### 启动日志备份

1. 在 `backup-test` 这个 namespace 中创建一个名为 `demo1-log-backup-gcs` 的 `Backup` CR。

    ```shell
    kubectl apply -f log-backup-gcs.yaml
    ```

    `log-backup-gcs.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-log-backup-gcs
      namespace: backup-test
    spec:
      backupMode: log
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

2. 等待启动操作完成：

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                    COMPLETIONS   ...
    backup-demo1-log-backup-gcs-log-start   1/1           ...
    ```

3. 查看新增的 `Backup` CR：

    ```shell
    kubectl get backup -n backup-test
    ```

    ```
    NAME                        TYPE    MODE   STATUS   ....
    demo1-log-backup-gcs        log    Running  ....
    ```

#### 查看日志备份的状态

通过查看 `Backup` CR 的信息，可查看日志备份的状态。

```shell
kubectl describe backup -n backup-test
```

从上述命令的输出中，你可以找到描述名为 `demo1-log-backup-gcs` 的 `Backup` CR 的如下信息，其中 `Log Checkpoint Ts` 表示日志备份可恢复的最近时间点：

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

#### 停止日志备份

由于你在开启日志备份的时候已经创建了名为 `demo1-log-backup-gcs` 的 `Backup` CR，因此可以直接更新该 `Backup` CR 的配置，来激活停止日志备份的操作。操作激活优先级从高到低分别是停止日志备份任务、删除日志备份数据和开启日志备份任务。

```shell
kubectl edit backup demo1-log-backup-gcs -n backup-test
```

在最后新增一行字段 `spec.logStop: true`，保存并退出。更新后的内容如下：

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-log-backup-gcs
  namespace: backup-test
spec:
  backupMode: log
  br:
    cluster: demo1
    clusterNamespace: test1
    sendCredToTikv: true
  gcs:
    projectId: ${project_id}
    secretName: gcs-secret
    bucket: my-bucket
    prefix: my-log-backup-folder
  logStop: true
```

可以看到名为 `demo1-log-backup-gcs` 的 `Backup` CR 的 `STATUS` 从 `Running` 变成了 `Stopped`：

```shell
kubectl get backup -n backup-test
```

```
NAME                       TYPE    MODE     STATUS    ....
demo1-log-backup-gcs       log     Stopped  ....
```

<Tip>
你也可以采用和启动日志备份时相同的方法来停止日志备份，已经被创建过的 `Backup` CR 会因此被更新。
</Tip>

#### 清理日志备份数据

1. 由于你在开启日志备份的时候已经创建了名为 `demo1-log-backup-gcs` 的 `Backup` CR，因此可以直接更新该 `Backup` CR 的配置，来激活清理日志备份数据的操作。操作激活优先级从高到低分别是停止日志备份任务、删除日志备份数据和开启日志备份任务。执行如下操作来清理 2022-10-10T15:21:00+08:00 之前的所有日志备份数据。

    ```shell
    kubectl edit backup demo1-log-backup-gcs -n backup-test
    ```

    在最后新增一行字段 `spec.logTruncateUntil: "2022-10-10T15:21:00+08:00"`，保存并退出。更新后的内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-gcs
      namespace: backup-test
    spec:
      backupMode: log
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

2. 等待清理操作完成：

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                       COMPLETIONS   ...
    ...
    backup-demo1-log-backup-gcs-log-truncate   1/1           ...
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
    NAME                    TYPE   MODE       STATUS     ...   LOGTRUNCATEUNTIL
    demo1-log-backup-gcs           log        Stopped    ...   2022-10-10T15:21:00+08:00
    ```

### 备份示例

<details>
<summary>备份全部集群数据</summary>

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-gcs
  namespace: backup-test
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
<summary>备份单个数据库的数据</summary>

以下示例中，备份 `db1` 数据库的数据。

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
<summary>备份单张表的数据</summary>

以下示例中，备份 `db1.table1` 表的数据。

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
<summary>使用表库过滤功能备份多张表的数据</summary>

以下示例中，备份 `db1.table1` 表 和  `db1.table2` 表的数据。

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

## 定时快照备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时快照备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次快照备份，定时快照备份底层通过 Ad-hoc 快照备份来实现。下面是创建定时快照备份的具体步骤：

### 前置条件：准备定时快照备份环境

同[Ad-hoc 快照备份环境准备](#前置条件准备-ad-hoc-备份环境)。

### 执行快照备份

1. 创建 `BackupSchedule` CR，开启 TiDB 集群的定时快照备份，将数据备份到 GCS：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-gcs.yaml
    ```

    `backup-schedule-gcs.yaml` 文件内容如下：

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

    从以上 `backup-schedule-gcs.yaml` 文件配置示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。

    - 关于 `backupSchedule` 独有的配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。
    - `backupTemplate` 用于指定集群及远程存储相关的配置，字段和 Backup CR 中的 `spec` 一样，详细介绍可参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

2. 定时快照备份创建完成后，通过以下命令查看备份的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bks -n test1 -owide
    ```

    查看定时快照备份下面所有的备份条目：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-gcs -n test1
    ```

## 删除备份的 Backup CR

如果你不再需要已备份的 Backup CR，请参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
