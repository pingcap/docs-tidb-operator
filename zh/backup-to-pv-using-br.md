---
title: 备份 TiDB 集群到持久卷
summary: 介绍如何使用 BR 备份 TiDB 集群数据到持久卷。
---

# 备份 TiDB 集群到持久卷

本文档介绍如何将 Kubernetes 上 TiDB 集群的数据备份到[持久卷](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/)上。本文描述的持久卷，指任何 [Kubernetes 支持的持久卷类型](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes)。本文以备份数据到网络文件系统 (NFS) 存储为例。

本文档介绍的备份方法基于 TiDB Operator 的 CustomResourceDefinition (CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool/) 工具获取集群数据，然后再将备份数据存储到持久卷。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

如果你对数据备份有以下要求，可考虑使用 BR 将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)或[定时全量备份](#定时全量备份)的方式备份至持久卷：

- 需要备份的数据量较大，而且要求备份速度较快
- 需要直接备份数据的 SST 文件（键值对）

如有其他备份需求，参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

> **注意：**
>
> - BR 只支持 TiDB v3.1 及以上版本。
> - 使用 BR 备份出的数据只能恢复到 TiDB 数据库中，无法恢复到其他数据库中。

## Ad-hoc 备份

Ad-hoc 备份支持全量备份与增量备份。Ad-hoc 备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

本文档假设对部署在 Kubernetes `test1` 这个命名空间中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

### 第 1 步：准备 Ad-hoc 备份环境

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/v1.2.0/manifests/backup/backup-rbac.yaml) 到执行备份的服务器。

2. 执行以下命令，在 `test1` 这个命名空间中，创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

3. 确认可以从 Kubernetes 集群中访问用于存储备份数据的 NFS 服务器，并且你已经配置了 TiKV 挂载跟备份任务相同的 NFS 共享目录到相同的本地目录。TiKV 挂载 NFS 的具体配置方法可以参考如下配置：

    ```yaml
    spec:
      tikv:
        additionalVolumes:
        # Specify volume types that are supported by Kubernetes, Ref: https://kubernetes.io/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes
        - name: nfs
          nfs:
            server: 192.168.0.2
            path: /nfs
        additionalVolumeMounts:
        # This must match `name` in `additionalVolumes`
        - name: nfs
          mountPath: /nfs
    ```

4. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要进行以下操作。如果你使用的 TiDB 为 v4.0.8 及以上版本，你可以跳过此步骤。

    1. 确保你拥有备份数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于备份前后调整 GC 时间。

    2. 创建 `backup-demo1-tidb-secret` secret 用于存放访问 TiDB 集群的用户所对应的密码。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
        ```

### 第 2 步：备份数据到持久卷

1. 创建 `Backup` CR，并将数据备份到 NFS：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-nfs.yaml
    ```

    `backup-nfs.yaml` 文件内容如下，该示例将 TiDB 集群的数据全量导出备份到 NFS：

    {{< copyable "" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-nfs
      namespace: test1
    spec:
      # # backupType: full
      # # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
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

    在配置 `backup-nfs.yaml` 文件时，请参考以下信息：

    - 如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考[使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。

    - `.spec.local` 表示持久卷相关配置，详细解释参考 [Local 存储字段介绍](backup-restore-cr.md#local-存储字段介绍)。

    - `spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`。更多 `.spec.br` 字段的详细解释参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。

    - 如果你使用的 TiDB 为 v4.0.8 及以上版本, BR 会自动调整 `tikv_gc_life_time` 参数，不需要配置 `spec.tikvGCLifeTime` 和 `spec.from` 字段。

    - 更多 `Backup` CR 字段的详细解释，参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

2. 创建好 `Backup` CR 后，TiDB Operator 会根据 `Backup` CR 自动开始备份。你可以通过以下命令查看备份状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -n test1 -owide
    ```

## 定时全量备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。下面是创建定时全量备份的具体步骤：

### 第 1 步：准备定时全量备份环境

同 [Ad-hoc 备份环境准备](#第-1-步准备-ad-hoc-备份环境)。

### 第 2 步：定时全量备份数据到持久卷

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
        # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
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

    从以上 `backup-schedule-nfs.yaml` 文件配置示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。

    * `backupSchedule` 独有的配置项具体介绍可参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。
    * `backupTemplate` 指定集群及远程存储相关的配置，字段和 Backup CR 中的 `spec` 一样，详细介绍可参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

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

## 删除备份的 Backup CR

备份完成后，你可能需要删除备份的 Backup CR。删除方法可参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
