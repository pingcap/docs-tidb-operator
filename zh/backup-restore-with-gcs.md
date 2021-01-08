---
title: 使用 GCS 远程存储备份与恢复 TiDB 集群数据
summary: 介绍如何使用 GCS 远程存储备份与恢复 TiDB 集群数据。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/backup-to-gcs/', '/docs-cn/tidb-in-kubernetes/dev/restore-from-gcs/', '/docs-cn/tidb-in-kubernetes/dev/backup-to-gcs/', '/docs-cn/tidb-in-kubernetes/dev/backup-to-gcs-using-br/', '/docs-cn/tidb-in-kubernetes/dev/restore-from-gcs-using-br/']
---

# 使用 GCS 远程存储备份与恢复 TiDB 集群数据

本文档详细描述了如何使用 Dumpling 、BR 将 Kubernetes 上的 TiDB 集群数据备份到 GCS 远程存储，以及如何使用 TiDB Lightning 、BR 将存储在 GCS 远程存储的备份数据恢复到 TiDB 集群。

本文使用的备份方式基于 TiDB Operator 新版（v1.1 及以上）的 CustomResourceDefinition (CRD) 实现。

## 使用 Dumpling 备份 TiDB 集群到 GCS

以下示例将备份 TiDB 集群数据到 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/)，本节中的“备份”，均是指全量备份（Ad-hoc 全量备份和定时全量备份），底层通过使用 [`Dumpling`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview) 获取集群的逻辑备份，然后再将备份数据上传到远程存储。

### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：备份前后，backup CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间
* SELECT
* RELOAD
* LOCK TABLES
* REPLICATION CLIENT

### Ad-hoc 全量备份

Ad-hoc 全量备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

为了更好地描述备份的使用方式，本文档提供如下备份示例。示例假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

#### Ad-hoc 全量备份到 GCS 环境准备

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 存储访问授权

    参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#gcs-账号授权) 授权访问 GCS 远程存储。

3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的 root 账号和密钥。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

#### 备份数据到 GCS

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

以上示例将 TiDB 集群的数据全量导出备份到 GCS。GCS 配置中的 `location`、`objectAcl`、`bucketAcl`、`storageClass` 项均可以省略。

配置中的 `projectId` 代表 GCP 上用户项目的唯一标识。具体获取该标识的方法可参考 [GCP 官方文档](https://cloud.google.com/resource-manager/docs/creating-managing-projects)。

GCS 支持以下几种 `storageClass` 类型：

* `MULTI_REGIONAL`
* `REGIONAL`
* `NEARLINE`
* `COLDLINE`
* `DURABLE_REDUCED_AVAILABILITY`

如果不设置 `storageClass`，则默认使用 `COLDLINE`。这几种存储类型的详细介绍可参考 [GCS 官方文档](https://cloud.google.com/storage/docs/storage-classes)。

GCS 支持以下几种 object access-control list (ACL) 策略：

* `authenticatedRead`
* `bucketOwnerFullControl`
* `bucketOwnerRead`
* `private`
* `projectPrivate`
* `publicRead`

如果不设置 object ACL 策略，则默认使用 `private` 策略。这几种访问控制策略的详细介绍可参考 [GCS 官方文档](https://cloud.google.com/storage/docs/access-control/lists)。

GCS 支持以下几种 bucket ACL 策略：

* `authenticatedRead`
* `private`
* `projectPrivate`
* `publicRead`
* `publicReadWrite`

如果不设置 bucket ACL 策略，则默认策略为 `private`。这几种访问控制策略的详细介绍可参考 [GCS 官方文档](https://cloud.google.com/storage/docs/access-control/lists)。

创建好 `Backup` CR 后，可通过以下命令查看备份状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -n test1 -owide
```

以上示例中，`.spec.dumpling` 指定 Dumpling 相关的配置，可以在 `options` 字段指定 Dumpling 的运行参数，详情见 [Dumpling 使用文档](https://docs.pingcap.com/zh/tidb/dev/dumpling-overview#dumpling-主要参数表)；默认情况下该字段可以不用配置。当不指定 Dumpling 的配置时，`options` 字段的默认值如下：

```
options:
- --threads=16
- --rows=10000
```

GCS 存储相关配置参考 [GCS 存储字段介绍](backup-restore-overview.md#gcs-存储字段介绍)，更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

### 定时全量备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。下面是创建定时全量备份的具体步骤：

#### 定时全量备份环境准备

同 [Ad-hoc 全量备份到 GCS 环境准备](#ad-hoc-全量备份到-gcs-环境准备)。

#### 定时全量备份到 GCS

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

从以上示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定 GCS 存储相关的配置，该配置与 Ad-hoc 全量备份到 GCS 的配置完全一样，可参考[备份数据到 GCS](#备份数据到-gcs)。`backupSchedule` 独有的配置项可参考 [BackupSchedule CR 字段介绍](backup-restore-overview.md#backupschedule-cr-字段介绍)。

> **注意：**
>
> TiDB Operator 会创建一个 PVC，这个 PVC 同时用于 Ad-hoc 全量备份和定时全量备份，备份数据会先存储到 PV，然后再上传到远端存储。如果备份完成后想要删掉这个 PVC，可以参考[删除资源](cheat-sheet.md#删除资源)先把备份 Pod 删掉，然后再把 PVC 删掉。
>
> 假如备份并上传到远端存储成功，TiDB Operator 会自动删除本地的备份文件。如果上传失败，则本地备份文件将被保留。

### 删除备份的 backup CR

删除备份的 backup CR 可参考 [删除备份的 backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 使用 TiDB Lightning 恢复 GCS 上的备份数据

以下示例将存储在 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/) 上指定路径上的集群备份数据恢复到 TiDB 集群，底层通过使用 [TiDB Lightning](https://pingcap.com/docs/stable/how-to/get-started/tidb-lightning/#tidb-lightning-tutorial) 来进行集群恢复。

### 环境准备

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 存储访问授权

    如果使用 GCS 来备份恢复集群，可以使用服务账号密钥授予权限，参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#gcs-账号授权) 授权访问 GCS 远程存储；

3. 创建 `restore-demo2-tidb-secret` secret，该 secret 存放用来访问 TiDB 集群的 root 账号和密钥：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=${password} --namespace=test2
    ```

### 数据库账户权限

| 权限 | 作用域 |
|:----|:------|
| SELECT | Tables |
| INSERT | Tables |
| UPDATE | Tables |
| DELETE | Tables |
| CREATE | Databases, tables |
| DROP | Databases, tables |
| ALTER | Tables |

### 将指定备份数据恢复到 TiDB 集群

1. 创建 restore custom resource (CR)，将指定的备份数据恢复至 TiDB 集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore.yaml
    ```

    `restore.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore
      namespace: test2
    spec:
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        path: gcs://${backup_path}
      # storageClassName: local-storage
      storageSize: 1Gi
    ```

2. 创建好 `Restore` CR 后可通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

     ```shell
     kubectl get rt -n test2 -owide
     ```

以上示例将存储在 GCS 上指定路径 `spec.gcs.path` 的备份数据恢复到 TiDB 集群 `spec.to.host`。关于 GCS 的配置项可以参考 [backup-gcs.yaml](#备份数据到-gcs) 中的配置。

GCS 存储相关配置参考 [GCS 存储字段介绍](backup-restore-overview.md#gcs-存储字段介绍)，更多 `Restore` CR 字段的详细解释参考 [Restore CR 字段介绍](backup-restore-overview.md#restore-cr-字段介绍)。

> **注意：**
>
> TiDB Operator 会创建一个 PVC，用于数据恢复，备份数据会先从远端存储下载到 PV，然后再进行恢复。如果恢复完成后想要删掉这个 PVC，可以参考[删除资源](cheat-sheet.md#删除资源)先把恢复 Pod 删掉，然后再把 PVC 删掉。

## 使用 BR 备份 TiDB 集群到 GCS

以下示例将备份 TiDB 集群数据到 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/)，[`BR`](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 会在底层获取集群的逻辑备份，然后再将备份数据上传到远程存储。

### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：备份前后，backup CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

### Ad-hoc 备份

Ad-hoc 备份支持全量备份与增量备份。Ad-hoc 备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

为了更好地描述备份的使用方式，本文档提供如下备份示例。示例假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

#### Ad-hoc 备份到 GCS 环境准备

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 存储访问授权

    GCS 账号授权方式参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#gcs-账号授权)。

3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的 root 账号和密钥。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
    ```

    > **注意：**
    >
    > 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，该步骤可以省略。

#### Ad-hoc 备份过程

1. 创建 `Backup` CR，并将数据备份到 GCS：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-gcs.yaml
    ```

    `backup-gcs.yaml` 文件内容如下：

    {{< copyable "shell-regular" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-gcs
      namespace: test1
    spec:
      # backupType: full
      # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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
        projectId: ${project-id}
        secretName: gcs-secret
        bucket: ${bucket}
        prefix: ${prefix}
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

    以上示例中，`spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释参考 `Backup` CR 中的 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。

    自 v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考 [使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。

    该示例将 TiDB 集群的数据全量导出备份到 GCS。`spec.gcs` 中的一些参数项均可省略，如 `location`、`objectAcl`、`storageClass`。更多 GCS 存储相关配置参考 [GCS 存储字段介绍](backup-restore-overview.md#gcs-存储字段介绍)。

    更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

    > **注意:**
    >
    > 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，无需配置 `spec.from`。

2. 创建好 `Backup` CR 后，可通过以下命令查看备份状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -n test1 -owide
    ```

### 定时全量备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。下面是创建定时全量备份的具体步骤：

#### 定时全量备份环境准备

同 [Ad-hoc 全量备份到 GCS 环境准备](#ad-hoc-备份到-gcs-环境准备)。

#### 定时全量备份过程

1. 创建 `BackupSchedule` CR，开启 TiDB 集群的定时全量备份，将数据备份到 GCS：

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
        # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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
          projectId: ${project-id}
          bucket: ${bucket}
          prefix: ${prefix}
          # location: us-east1
          # storageClass: STANDARD_IA
          # objectAcl: private
    ```

2. 定时全量备份创建完成后，通过以下命令查看备份的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bks -n test1 -owide
    ```

    查看定时全量备份下面所有的备份条目：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-gcs -n test1
    ```

从以上示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定 GCS 存储相关的配置，该配置与 Ad-hoc 全量备份到 GCS 的配置完全一样，可参考[Ad-hoc 全量备份过程](#ad-hoc-备份过程)。`backupSchedule` 独有的配置项可参考 [BackupSchedule CR 字段介绍](backup-restore-overview.md#backupschedule-cr-字段介绍)。

### 删除备份的 backup CR

删除备份的 backup CR 可参考 [删除备份的 backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 使用 BR 恢复 GCS 上的备份数据

以下示例使用 BR 将存储在 GCS 上指定路径的集群备份数据恢复到 TiDB 集群。

### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：恢复前后，restore CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

### 环境准备

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 存储访问授权

    GCS 账号授权方式参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#gcs-账号授权)。

3. 创建 `restore-demo2-tidb-secret` secret，该 secret 存放用来访问 TiDB 集群的 root 账号和密钥：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
    ```

    > **注意：**
    >
    > 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，该步骤可以省略。

### 恢复过程

1. 创建 restore custom resource (CR)，将指定的备份数据恢复至 TiDB 集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore.yaml
    ```

    `restore.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-gcs
      namespace: test2
    spec:
      # backupType: full
      br:
        cluster: demo2
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status-addr}
        # concurrency: 4
        # rateLimit: 0
        # checksum: true
        # sendCredToTikv: true
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      gcs:
        projectId: ${project-id}
        secretName: gcs-secret
        bucket: ${bucket}
        prefix: ${prefix}
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

2. 创建好 `Restore` CR 后，通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

     ```shell
     kubectl get rt -n test2 -owide
     ```

> **注意：**
>
> 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，无需配置 `spec.to`.

以上示例将存储在 GCS 上指定路径 `spec.gcs.bucket` 存储桶中 `spec.gcs.prefix`文件夹下的备份数据恢复到 TiDB 集群 `spec.to.host`。关于 BR、GCS 的配置项可以参考 [backup-gcs.yaml](#ad-hoc-备份过程) 中的配置。

以上示例中，`.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`，更多 `.spec.br` 字段的详细解释参考 `Backup` CR 中的 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。

GCS 存储相关配置参考 [GCS 存储字段介绍](backup-restore-overview.md#gcs-存储字段介绍)。更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。