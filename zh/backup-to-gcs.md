---
title: 使用 Dumpling 备份 TiDB 集群数据到 GCS
summary: 介绍如何使用 Dumpling 将 TiDB 集群数据备份到 Google Cloud Storage (GCS)。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/backup-to-gcs/']
---

# 使用 Dumpling 备份 TiDB 集群数据到 GCS

本文档详细描述了如何将 Kubernetes 上 TiDB 集群的数据备份到 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/) 上。本文档中的“备份”，均是指全量备份（Ad-hoc 全量备份和定时全量备份），底层通过使用 [`Dumpling`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview) 获取集群的逻辑备份，然后再将备份数据上传到远端 GCS。

本文使用的备份方式基于 TiDB Operator 新版（v1.1 及以上）的 CustomResourceDefinition (CRD) 实现。

## 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：备份前后，Backup CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间
* SELECT
* RELOAD
* LOCK TABLES
* REPLICATION CLIENT

## Ad-hoc 全量备份

Ad-hoc 全量备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

为了更好地描述备份的使用方式，本文档提供如下备份示例。示例假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

### Ad-hoc 全量备份环境准备

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 远程存储访问授权。

    参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#gcs-账号授权)授权访问 GCS 远程存储。

3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的 root 账号和密钥。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

### 备份数据到 GCS

创建 `Backup` CR，并将数据备份到 GCS：

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f backup-gcs.yaml
```

`backup-gcs.yaml` 文件内容如下：

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-gcs
  namespace: test1
spec:
  from:
    host: ${tidb_host}
    port: ${tidb_port}
    user: ${tidb_user}
    secretName: backup-demo1-tidb-secret
  gcs:
    secretName: gcs-secret
    projectId: ${project_id}
    bucket: ${bucket}
    # prefix: ${prefix}
    # location: us-east1
    # storageClass: STANDARD_IA
    # objectAcl: private
    # bucketAcl: private
# dumpling:
#  options:
#  - --threads=16
#  - --rows=10000
#  tableFilter:
#  - "test.*"
  storageClassName: local-storage
  storageSize: 10Gi
```

以上示例将 TiDB 集群的数据全量导出备份到 GCS。GCS 配置中的 `location`、`objectAcl`、`bucketAcl`、`storageClass` 项均可以省略。GCS 存储相关配置参考 [GCS 存储字段介绍](backup-restore-overview.md#gcs-存储字段介绍)。

以上示例中的 `.spec.dumpling` 表示 Dumpling 相关的配置，可以在 `options` 字段指定 Dumpling 的运行参数，详情见 [Dumpling 使用文档](https://docs.pingcap.com/zh/tidb/dev/dumpling-overview#dumpling-主要参数表)；默认情况下该字段可以不用配置。当不指定 Dumpling 的配置时，`options` 字段的默认值如下：

```
options:
- --threads=16
- --rows=10000
```

更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

创建好 `Backup` CR 后，可通过以下命令查看备份状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -n test1 -owide
```

## 定时全量备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。下面是创建定时全量备份的具体步骤：

### 定时全量备份环境准备

同 [Ad-hoc 全量备份环境准备](#ad-hoc-全量备份环境准备)。

### 定时全量备份数据到 GCS

创建 `BackupSchedule` CR 开启 TiDB 集群的定时全量备份，将数据备份到 GCS：

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
  namespace: test1
spec:
  #maxBackups: 5
  #pause: true
  maxReservedTime: "3h"
  schedule: "*/2 * * * *"
  backupTemplate:
    from:
      host: ${tidb_host}
      port: ${tidb_port}
      user: ${tidb_user}
      secretName: backup-demo1-tidb-secret
    gcs:
      secretName: gcs-secret
      projectId: ${project_id}
      bucket: ${bucket}
      # prefix: ${prefix}
      # location: us-east1
      # storageClass: STANDARD_IA
      # objectAcl: private
      # bucketAcl: private
  # dumpling:
  #  options:
  #  - --threads=16
  #  - --rows=10000
  #  tableFilter:
  #  - "test.*"
    # storageClassName: local-storage
    storageSize: 10Gi
```

定时全量备份创建完成后，可以通过以下命令查看定时全量备份的状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bks -n test1 -owide
```

查看定时全量备份下面所有的备份条目：

{{< copyable "shell-regular" >}}

 ```shell
 kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-gcs -n test1
 ```

从以上示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定集群及远程存储相关的配置，字段和 Backup CR 中的 `spec` 一样，详细介绍可参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。`backupSchedule` 独有的配置项具体介绍可参考 [BackupSchedule CR 字段介绍](backup-restore-overview.md#backupschedule-cr-字段介绍)。

> **注意：**
>
> TiDB Operator 会创建一个 PVC，这个 PVC 同时用于 Ad-hoc 全量备份和定时全量备份，备份数据会先存储到 PV，然后再上传到远端存储。如果备份完成后想要删掉这个 PVC，可以参考[删除资源](cheat-sheet.md#删除资源)先把备份 Pod 删掉，然后再把 PVC 删掉。
>
> 假如备份并上传到远端存储成功，TiDB Operator 会自动删除本地的备份文件。如果上传失败，则本地备份文件将被保留。

## 删除备份的 Backup CR

删除备份的 Backup CR 可参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
