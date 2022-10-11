---
title: 使用 PITR 备份 TiDB 集群数据到 Azure Blob Storage
summary: 介绍如何使用 PITR 备份 TiDB 集群数据到 Azure Blob Storage 上。
---

# 使用 PITR 日志备份功能备份 TiDB 集群数据到 Azure Blob Storage

本文介绍如何使用 PITR 日志备份功能备份 TiDB 集群数据到 Azure Blob Storage 上。

本文使用的备份方式基于 TiDB Operator 的 Custom Resource Definition(CRD) 实现，底层使用 BR 的 PITR 功能，让 TiKV 监听增量数据，然后再将数据上传到 Azure Blob Storage 上。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。PITR 全称为 Point-in-time recovery，使用该功能可以让你在新集群上恢复备份集群的历史任意时刻点的快照。

## 使用场景

如果你对数据备份有以下要求，可考虑使用 PITR 将 TiDB 集群数据以 Ad-hoc 的方式备份至 Azure Blob Storage 上：

- 需要在新集群上恢复备份集群的历史任意时刻点快照
- 数据的 RPO 在分钟级别

如有其他备份需求，请参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

> **注意：**
>
> - BR 的 PITR 功能只支持 TiDB v6.2 及以上版本。
> - 使用 PITR 备份出的数据只能恢复到 TiDB 数据库中，无法恢复到其他数据库中。

## 使用流程

本节将介绍使用 PITR 功能的具体流程。

### 前置条件

本节假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份。

### 准备 Ad-hoc 备份环境

Ad-hoc 备份支持 PITR 功能的启动和停止日志备份任务、恢复任意时间点和清理日志备份数据等操作。

要进行 Ad-hoc 备份，你需要创建一个自定义的 `Backup` custom resource (CR) 对象来描述本次备份。创建好 `Backup` 对象后，TiDB Operator 根据这个对象自动完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。具体流程如下：

1. 创建一个用于管理备份的 namespace，这里创建了名为 `backup-test` 的 namespace。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create namespace backup-test
    ```

2. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `backup-test` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n backup-test
    ```

3. 为刚创建的 namespace `backup-test` 授予远程存储访问权限，可以使用两种方式授予权限，可参考文档 [Azure 账号授权](grant-permissions-to-remote-storage.md#azure-账号授权)。创建成功后, namespace `backup-test` 就拥有了名为 `azblob-secret` 或 `azblob-secret-ad` 的 secret 对象。

> **注意：**
>
> 授予的账户所拥有的角色至少拥有对 blob 修改的权限（例如[参与者](https://learn.microsoft.com/zh-cn/azure/role-based-access-control/built-in-roles#contributor)）。
>
> 下文为了叙述简洁，统一使用名为 `azblob-secret` 的 secret 对象。

### PITR 中日志备份任务以及日志备份数据的管理

日志备份任务的启动和停止，以及清理日志备份数据等操作都使用了相同的 `Backup CR`。本节示例创建了名为 `demo1-backup-azblob` 的 `Backup CR`。具体管理操作如以下几个流程所示。

#### 启动日志备份

+ 在 `backup-test` 这个 namespace 中产生一个名为 `demo1-backup-azblob` 的 `Backup CR`。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-azblob.yaml
    ```

    `backup-azblob.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-azblob
      namespace: backup-test
    spec:
      backupType: log
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-folder
    
    ```

+ 等待启动操作完成：

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                   COMPLETIONS   ...
    backup-demo1-backup-azblob-log-start   1/1           ...
    ```

+ 查看新增的 `Backup CR`：

    ```shell
    kubectl get backups -n backup-test
    ```

    ```
    NAME                   TYPE    MODE    ....
    demo1-backup-azblob            log     ....
    ```

---

#### 查看日志备份的状态

+ 通过查看 `Backup CR` 的信息查看日志备份的状态。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl describe backup -n backup-test
    ```
    我们会找到描述名为 `demo1-backup-azblob` 的 `Backup CR` 的如下信息，其中 `Log Checkpoint Ts` 表示日志备份可恢复的最近时间点：
    ```
    Status:
    Backup Path:  azure://test/log-backup-test-1/
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

---

#### 停止日志备份。

+ 由于我们已经在开启日志备份的时候已经创建了名为 `demo1-backup-azblob` 的 `Backup CR`，因此可以直接更新该 `Backup CR` 的配置，来激活停止日志备份的操作，具体操作激活优先级可参考 [tidb-operator#4682](https://github.com/pingcap/tidb-operator/pull/4682)。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit backup demo1-backup-azblob -n backup-test
    ```
    在最后新增一行字段 `spec.logStop: true`，保存并退出。更新后的内容如下：
    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-azblob
      namespace: backup-test
    spec:
      backupType: log
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-folder
      logStop: true

    ```

> **提示：**
>
> 当然，我们也可以采用和启动日志备份时相同的方法来停止日志备份，并且已经被创建过的 `Backup CR` 会因此被更新。

---

#### 清理日志备份数据

+ 由于我们已经在开启日志备份的时候已经创建了名为 `demo1-backup-azblob` 的 `Backup CR`，因此可以直接更新该 `Backup CR` 的配置，来激活清理日志备份数据的操作，具体操作激活优先级可参考 [tidb-operator#4682](https://github.com/pingcap/tidb-operator/pull/4682)。执行如下操作来清理 2022-10-10T15:21:00+08:00 之前的所有日志备份数据。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit backup demo1-backup-azblob -n backup-test
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
      backupType: log
      br:
        cluster: demo1
        clusterNamespace: test1
        sendCredToTikv: true
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-folder
      logTruncateUntil: "2022-10-10T15:21:00+08:00"
    
    ```

+ 等待清理操作完成：

    ```shell
    kubectl get jobs -n backup-test
    ```

    ```
    NAME                                      COMPLETIONS   ...
    ...
    backup-demo1-backup-azblob-log-truncate   1/1           ...
    ``` 

+ 查看 `Backup CR` 的信息：

    ```shell
    kubectl describe backup -n backup-test
    ```

    ```
    ...
    Log Success Truncate Until:  2022-10-10T15:21:00+08:00
    ...
    ```

## 删除备份的 Backup CR

如果你不再需要已备份的 Backup CR，请参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。

