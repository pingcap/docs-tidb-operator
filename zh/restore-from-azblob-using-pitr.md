---
title: 使用 PITR 恢复 Azure Blob Storage 上的备份数据
summary: 介绍如何使用 PITR 恢复 Azure Blob Storage 上的备份数据。
---

# 使用 PITR 恢复 Azure Blob Storage 上的备份数据

本文介绍如何将 Azure Blob Storage 上的 LOG 备份数据恢复到 Kubernetes 环境中的 TiDB 集群。

本文使用的备份方式基于 TiDB Operator 的 Custom Resource Definition(CRD) 实现，底层使用 BR 的 PITR 功能，让 TiKV 监听增量数据，然后再将数据上传到 Azure Blob Storage 上。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。PITR 全称为 Point-in-time recovery，使用该功能可以让你在新集群上恢复备份集群的历史任意时刻点的快照。

## 使用场景

当使用 BR 的 PITR 功能将 TiDB 集群数据备份到 Azure Blob Storage 后，如果需要从 Azure Blob Storage 将备份的 LOG（键值对）文件恢复到 TiDB 集群，请参考本文使用 BR 的 PITR 功能进行恢复。

> **注意：**
>
> - BR 的 PITR 功能只支持 TiDB v6.2 及以上版本。

## 使用流程

本节将介绍使用 PITR 恢复功能的具体流程。

### 前置条件

本文假设 Azure Blob Storage 中的桶 `my-container` 中存在两份备份数据，分别是：

1. 在日志备份期间进行[全量备份](backup-to-azblob-using-br.md)产生的备份数据，存储在 `my-folder-full` 文件夹下；
2. 日志备份产生的备份数据，存储在 `my-folder` 文件夹下。

本文示例在 namespace `test2` 中的 TiDB 集群 `demo2` 上首先通过全量备份数据恢复到全量备份的时间点，然后通过日志备份的增量数据恢复到备份集群的历史任意时刻点。

### 准备 Ad-hoc 备份环境

Ad-hoc 备份支持 PITR 功能的启动和停止日志备份任务、恢复任意时间点和清理日志备份数据等操作。

要进行 Ad-hoc 备份，你需要创建一个自定义的 `Backup` custom resource (CR) 对象来描述本次备份。创建好 `Backup` 对象后，TiDB Operator 根据这个对象自动完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。具体流程如下：

1. 创建一个用于管理恢复的 namespace，这里创建了名为 `restore-test` 的 namespace。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create namespace restore-test
    ```

2. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `restore-test` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n restore-test
    ```

3. 为刚创建的 namespace `restore-test` 授予远程存储访问权限，可以使用两种方式授予权限，可参考文档 [Azure 账号授权](grant-permissions-to-remote-storage.md#azure-账号授权)。创建成功后, namespace `restore-test` 就拥有了名为 `azblob-secret` 或 `azblob-secret-ad` 的 secret 对象。

> **注意：**
>
> 授予的账户所拥有的角色至少拥有对 blob 访问的权限（例如[读取器](https://learn.microsoft.com/zh-cn/azure/role-based-access-control/built-in-roles#reader)）。
>
> 下文为了叙述简洁，统一使用名为 `azblob-secret` 的 secret 对象。

### 将指定备份数据恢复到 TiDB 集群

1. 在 `restore-test` 这个 namespace 中产生一个名为 `restore-pitr-1` 的 `Backup CR`，并指定恢复到 `2022-10-10T17:21:00+08:00`。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-azblob.yaml
    ```

    `restore-azblob.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
    name: restore-pitr-1
    namespace: restore-test
    spec:
    restoreMode: pitr
    br:
        cluster: demo2
        clusterNamespace: test2
    azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-folder
    pitrRestoredTs: "2022-10-10T17:21:00+08:00" 
    pitrFullBackupStorageProvider:
        azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-folder-full
    
    ```

2. 等待恢复操作完成：

    ```shell
    kubectl get jobs -n restore-test
    ```

    ```
    NAME                     COMPLETIONS   ...
    restore-restore-pitr-1   1/1           ...
    ```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
