---
title: 使用持久卷备份与恢复 TiDB 集群
summary: 介绍如何使用持久卷备份与恢复 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/backup-to-pv-using-br/', '/docs-cn/tidb-in-kubernetes/dev/restore-from-pv-using-br/']
---

# 使用持久卷备份与恢复 TiDB 集群

本文档详细描述了如何将 Kubernetes 上 TiDB 集群的数据备份到[持久卷](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/)上, 以及如何将存储在[持久卷](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/)上的备份数据恢复到 Kubernetes 环境中的 TiDB 集群。

本文使用的备份方式基于 TiDB Operator 新版（v1.1.8 及以上）的 CustomResourceDefinition (CRD) 实现。

本文描述的持久卷指任何 [Kubernetes 支持的持久卷类型](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes)。本文将以 NFS 为例，介绍如何使用 BR 备份 TiDB 集群的数据到持久卷，以及如何将存储在持久卷上指定路径的集群备份数据恢复到 TiDB 集群。

## 使用 BR 备份 TiDB 集群到持久卷

以下示例将使用 [`BR`](https://docs.pingcap.com/zh/tidb/dev/backup-and-restore-tool) 备份 TiDB 集群数据到 NFS。

### Ad-hoc 备份

Ad-hoc 备份支持全量备份与增量备份。Ad-hoc 备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

为了更好地描述备份的使用方式，本文档提供如下备份示例。示例假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

#### Ad-hoc 备份环境准备

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的账号的密码。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
    ```

    > **注意：**
    >
    > 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，该步骤可以省略。

3. 确认可以从 Kubernetes 集群中访问用于存储备份数据的 NFS 服务器。

#### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：备份前后，backup CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

> **注意：**
>
> 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，该步骤可以省略。

#### Ad-hoc 备份过程

1. 创建 `Backup` CR，并将数据备份到 NFS：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-nfs.yaml
    ```

    `backup-nfs.yaml` 文件内容如下：

    {{< copyable "shell-regular" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-nfs
      namespace: test1
    spec:
      # # backupType: full
      # # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
      # from:
      #   host: ${tidb-host}
      #   port: ${tidb-port}
      #   user: ${tidb-user}
      #   secretName: backup-demo1-tidb-secret
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
        # statusAddr: ${status-addr}
        # concurrency: 4
        # rateLimit: 0
        # checksum: true
        # options:
        # - --lastbackupts=420134118382108673
      local:
        prefix: backup-nfs
        volume:
          name: nfs
          nfs:
            server: ${nfs_server_ip}
            path: /nfs
        volumeMount:
          name: nfs
          mountPath: /nfs
    ```

    以上示例中，`spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`。更多 `.spec.br` 字段的详细解释参考 `Backup` CR 中的 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。

    建议配置 `.spec.local.prefix` 字段，如果设置了这个字段，则会使用这个字段来拼接在持久卷的存储路径 `local://${.spec.local.volumeMount.mountPath}/${.spec.local.prefix}/`。

    自 v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考 [使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。

    更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

    该示例将 TiDB 集群的数据全量导出备份到 NFS。

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

同 [Ad-hoc 全量备份环境准备](#ad-hoc-备份环境准备)。

#### 定时全量备份过程

1. 创建 `BackupSchedule` CR，开启 TiDB 集群的定时全量备份，将数据备份到 NFS：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-nfs.yaml
    ```

    `backup-schedule-nfs.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-nfs
      namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
        # from:
        #   host: ${tidb_host}
        #   port: ${tidb_port}
        #   user: ${tidb_user}
        #   secretName: backup-demo1-tidb-secret
        br:
          cluster: demo1
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status-addr}
          # concurrency: 4
          # rateLimit: 0
          # checksum: true
        local:
          prefix: backup-nfs
          volume:
            name: nfs
            nfs:
              server: ${nfs_server_ip}
              path: /nfs
          volumeMount:
            name: nfs
            mountPath: /nfs
    ```

2. 定时全量备份创建完成后，通过以下命令查看备份的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bks -n test1 -owide
    ```

    查看定时全量备份下面所有的备份条目：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-nfs -n test1
    ```

从以上示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定 NFS 存储相关的配置，该配置与 Ad-hoc 全量备份到 NFS 的配置完全一样，可参考[Ad-hoc 全量备份过程](#ad-hoc-备份过程)。`backupSchedule` 独有的配置项可参考 [BackupSchedule CR 字段介绍](backup-restore-overview.md#backupschedule-cr-字段介绍)。

### 删除备份的 backup CR

删除备份的 backup CR 可参考 [删除备份的 backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 使用 BR 恢复持久卷上的备份数据

以下实例将使用 BR 将存储在 NFS 上的备份数据恢复到 TiDB 集群，底层通过使用 [`BR`](https://docs.pingcap.com/zh/tidb/dev/backup-and-restore-tool) 来进行集群恢复。

### 数据库账户权限

- `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：恢复前后，restore CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

> **注意：**
>
> 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，该步骤可以省略。

### 环境准备

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 创建 `restore-demo2-tidb-secret` secret，该 secret 存放用来访问 TiDB 服务的账号的密码：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
    ```

    > **注意：**
    >
    > 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，该步骤可以省略。

3. 确认可以从 Kubernetes 集群中访问用于存储备份数据的 NFS 服务器。

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
      name: demo2-restore-nfs
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
      # # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
      # to:
      #   host: ${tidb_host}
      #   port: ${tidb_port}
      #   user: ${tidb_user}
      #   secretName: restore-demo2-tidb-secret
      local:
        prefix: backup-nfs
        volume:
          name: nfs
          nfs:
            server: ${nfs_server_if}
            path: /nfs
        volumeMount:
          name: nfs
          mountPath: /nfs
    ```

    关于 BR 和持久卷的配置项可以参考 [backup-nfs.yaml](#ad-hoc-备份过程) 中的配置。

    以上示例中，`.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释参考 `Backup` CR 中的 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

    > **注意：**
    >
    > 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，无需配置 `spec.to`。

2. 创建好 `Restore` CR 后，通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get rt -n test2 -owide
    ```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
