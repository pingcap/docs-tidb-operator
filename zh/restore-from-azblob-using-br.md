---
title: 使用 BR 恢复 Azure Blob Storage 上的备份数据
summary: 介绍如何使用 BR 恢复 Azure Blob Storage 上的备份数据。
---

# 使用 BR 恢复 Azure Blob Storage 上的备份数据

本文介绍如何将 Azure Blob Storage 上的备份数据恢复到 Kubernetes 环境中的 TiDB 集群，其中包括以下两种恢复方式：

- 全量恢复，可以将 TiDB 集群恢复到快照备份的时刻点。备份数据来自于快照备份。
- PITR 恢复，可以将 TiDB 集群恢复到历史任意时刻点。备份数据来自于快照备份和日志备份。

本文使用的恢复方式基于 TiDB Operator 的 Custom Resource Definition (CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-overview) 进行数据恢复。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

PITR 全称为 Point-in-time recovery，该功能可以让你在新集群上恢复备份集群的历史任意时刻点的快照。使用 PITR 功能恢复时需要快照备份数据和日志备份数据。在恢复时，首先将快照备份的数据恢复到 TiDB 集群中，再以快照备份的时刻点作为起始时刻点，并指定任意恢复时刻点，将日志备份数据恢复到 TiDB 集群中。

> **注意：**
>
> - BR 只支持 TiDB v3.1 及以上版本。
> - BR 的 PITR 恢复功能只支持 TiDB v6.2 及以上版本。
> - BR 恢复的数据无法被同步到下游，因为 BR 直接导入 SST/LOG 文件，而下游集群目前没有办法获得上游的 SST/LOG 文件。

## 全量恢复

本节示例将存储在 Azure Blob Storage 上指定路径 `spec.azblob.container` 存储桶中 `spec.azblob.prefix` 文件夹下的快照备份数据恢复到 namespace `test2` 中的 TiDB 集群 `demo2`。以下是具体的操作过程。

### 前置条件：完成数据备份

本节假设 Azure Blob Storage 中的桶 `my-container` 中文件夹 `my-full-backup-folder` 下存储着快照备份产生的备份数据。关于如何备份数据，请参考[使用 BR 备份 TiDB 集群数据到 Azure Blob Storage](backup-to-azblob-using-br.md)。

### 第 1 步：准备恢复环境

使用 BR 将 Azure Blob Storage 上的备份数据恢复到 TiDB 前，请按照以下步骤准备恢复环境。

1. 创建一个用于管理恢复的 namespace，这里创建了名为 `restore-test` 的 namespace。

    ```shell
    kubectl create namespace restore-test
    ```

2. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `restore-test` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    ```shell
    kubectl apply -f backup-rbac.yaml -n restore-test
    ```

3. 为刚创建的 namespace `restore-test` 授予远程存储访问权限，可以使用两种方式授予权限，可参考文档 [Azure 账号授权](grant-permissions-to-remote-storage.md#azure-账号授权)。创建成功后, namespace `restore-test` 就拥有了名为 `azblob-secret` 或 `azblob-secret-ad` 的 secret 对象。

    > **注意：**
    >
    > 授予的账户所拥有的角色至少拥有对 blob 访问的权限（例如[读取器](https://learn.microsoft.com/zh-cn/azure/role-based-access-control/built-in-roles#reader)）。
    >
    > 在创建 secret 对象的时候，你可以自定义它的名字。下文为了叙述简洁，统一使用名为 `azblob-secret` 的 secret 对象。

4. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要进行以下操作。如果你使用的 TiDB 为 v4.0.8 及以上版本，请跳过此步骤。

    1. 确保你拥有恢复数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于恢复前后调整 GC 时间。

    2. 创建 `restore-demo2-tidb-secret` secret 用于存放访问 TiDB 集群的 root 账号和密钥。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=password=${password} --namespace=test2
        ```

### 第 2 步：将指定备份数据恢复到 TiDB 集群

在 `restore-test` 这个 namespace 中产生一个名为 `demo2-restore-azblob` 的 `Restore` CR，用于恢复快照备份产生的数据：

```shell
kubectl apply -f resotre-full-azblob.yaml
```

`restore-full-azblob.yaml` 文件内容如下：

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Restore
metadata:
  name: demo2-restore-azblob
  namespace: restore-test
spec:
  br:
    cluster: demo2
    clusterNamespace: test2
    # logLevel: info
    # statusAddr: ${status_addr}
    # concurrency: 4
    # rateLimit: 0
    # timeAgo: ${time}
    # checksum: true
    # sendCredToTikv: true
  # # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # to:
  #   host: ${tidb_host}
  #   port: ${tidb_port}
  #   user: ${tidb_user}
  #   secretName: restore-demo2-tidb-secret
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-full-backup-folder
```

在配置 `restore-azblob.yaml` 文件时，请参考以下信息：

- 关于 Azure Blob Storage 相关配置，请参考 [Azure Blob Storage 存储字段介绍](backup-restore-cr.md#azure-blob-storage-存储字段介绍)。
- `.spec.br` 中的一些参数为可选项，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
- `spec.azblob.secretName`：填写你在创建 secret 对象时自定义的 secret 对象的名字，例如 `azblob-secret`。
- 如果你使用的 TiDB 为 v4.0.8 及以上版本，BR 会自动调整 `tikv_gc_life_time` 参数，不需要在 Restore CR 中配置 `spec.to` 字段。
- 更多 `Restore` CR 字段的详细解释，请参考 [Restore CR 字段介绍](backup-restore-cr.md#restore-cr-字段介绍)。

创建好 `Restore` CR 后，可通过以下命令查看恢复的状态：

```shell
kubectl get restore -n test2 -o wide
```

```
NAME                   STATUS     ...
demo2-restore-azblob   Complete   ...
```

## PITR 恢复

本节示例在 namespace `test3` 中的 TiDB 集群 `demo3` 上执行 PITR 恢复，分为以下两步：

1. 使用 `spec.pitrFullBackupStorageProvider.azblob.container` 存储桶中 `spec.pitrFullBackupStorageProvider.azblob.prefix` 文件夹下的快照备份数据，将集群恢复到快照备份的时刻点。
2. 使用 `spec.azblob.container` 存储桶中 `spec.azblob.prefix` 文件夹下的日志备份的增量数据，将集群恢复到备份集群的历史任意时刻点。

下面是具体的操作过程。

### 前置条件：完成数据备份

本节假设 Azure Blob Storage 中的桶 `my-container` 中存在两份备份数据，分别是：

- 在**日志备份期间**，进行快照备份产生的备份数据，存储在 `my-full-backup-folder-pitr` 文件夹下。
- 日志备份产生的备份数据，存储在 `my-log-backup-folder-pitr` 文件夹下。

关于如何备份数据，请参考[使用 BR 备份 TiDB 集群数据到 Azure Blob Storage](backup-to-azblob-using-br.md)。

> **注意：**
>
> 指定的恢复时间点需要在快照备份时刻点之后，日志备份 `checkpoint-ts` 之前。

### 第 1 步：准备恢复环境

使用 BR 将 Azure Blob Storage 上的备份数据恢复到 TiDB 前，请按照以下步骤准备恢复环境。

1. 创建一个用于管理恢复的 namespace，这里创建了名为 `restore-test` 的 namespace。

    ```shell
    kubectl create namespace restore-test
    ```

2. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `restore-test` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    ```shell
    kubectl apply -f backup-rbac.yaml -n restore-test
    ```

3. 为刚创建的 namespace `restore-test` 授予远程存储访问权限，可以使用两种方式授予权限，可参考文档 [Azure 账号授权](grant-permissions-to-remote-storage.md#azure-账号授权)。创建成功后, namespace `restore-test` 就拥有了名为 `azblob-secret` 或 `azblob-secret-ad` 的 secret 对象。

    > **注意：**
    >
    > 授予的账户所拥有的角色至少拥有对 blob 访问的权限（例如[读取器](https://learn.microsoft.com/zh-cn/azure/role-based-access-control/built-in-roles#reader)）。
    >
    > 在创建 secret 对象的时候，你可以自定义它的名字。下文为了叙述简洁，统一使用名为 `azblob-secret` 的 secret 对象。

### 第 2 步：将指定备份数据恢复到 TiDB 集群

本节示例中首先将快照备份恢复到集群中，因此 PITR 的恢复时刻点需要在[快照备份的时刻点](backup-to-azblob-using-br.md#查看快照备份的状态)之后，并在[日志备份的最新恢复点](backup-to-azblob-using-br.md#查看日志备份的状态)之前。具体步骤如下：

1. 在 `restore-test` 这个 namespace 中产生一个名为 `demo3-restore-azblob` 的 `Restore` CR，并指定恢复到 `2022-10-10T17:21:00+08:00`:

    ```shell
    kubectl apply -f restore-point-azblob.yaml
    ```

    `restore-point-azblob.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo3-restore-azblob
      namespace: restore-test
    spec:
      restoreMode: pitr
      br:
        cluster: demo3
        clusterNamespace: test3
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-log-backup-folder-pitr
      pitrRestoredTs: "2022-10-10T17:21:00+08:00"
      pitrFullBackupStorageProvider:
        azblob:
          secretName: azblob-secret
          container: my-container
          prefix: my-full-backup-folder-pitr
    ```

    在配置 `restore-point-azblob.yaml` 文件时，请参考以下信息：

    - `spec.restoreMode`：在进行 PITR 恢复时，需要设置值为 `pitr`。默认值为 `snapshot`，即进行全量恢复。

2. 查看恢复的状态，等待恢复操作完成：

    ```shell
    kubectl get jobs -n restore-test
    ```

    ```
    NAME                           COMPLETIONS   ...
    restore-demo3-restore-azblob   1/1           ...
    ```

    也可通过以下命令查看恢复的状态：

    ```shell
    kubectl get restore -n restore-test -o wide
    ```

    ```
    NAME                   STATUS     ...
    demo3-restore-azblob   Complete   ...
    ```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
