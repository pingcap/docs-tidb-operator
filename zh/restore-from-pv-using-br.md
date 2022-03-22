---
title: 恢复持久卷上的备份数据
summary: 介绍如何将存储在持久卷上的备份数据恢复到 TiDB 集群。
---

# 恢复持久卷上的备份数据

本文档介绍如何将存储在[持久卷](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/)上的备份数据恢复到 Kubernetes 环境中的 TiDB 集群。本文描述的持久卷指任何 [Kubernetes 支持的持久卷类型](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes)。本文以从网络文件系统 (NFS) 存储恢复数据到 TiDB 为例。

本文档介绍的恢复方法基于 TiDB Operator 的 CustomResourceDefinition (CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool/) 工具来恢复数据。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

当使用 BR 将 TiDB 集群数据备份到持久卷后，如果需要从持久卷将备份的 SST (键值对) 文件恢复到 TiDB 集群，请参考本文使用 BR 进行恢复。

> **注意：**
>
> - BR 只支持 TiDB v3.1 及以上版本。
> - BR 恢复的数据无法被同步到下游，因为 BR 直接导入 SST 文件，而下游集群目前没有办法获得上游的 SST 文件。

## 第 1 步：准备恢复环境

使用 BR 将 PV 上的备份数据恢复到 TiDB 前，请按照以下步骤准备恢复环境。

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/v1.3.2/manifests/backup/backup-rbac.yaml) 到执行恢复的服务器。

2. 执行以下命令在 `test2` 这个命名空间中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

3. 确认可以从 Kubernetes 集群中访问用于存储备份数据的 NFS 服务器。

4. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要进行以下操作。如果你使用的 TiDB 为 v4.0.8 及以上版本，你可以跳过此步骤。

    1. 确保你拥有恢复数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于恢复前后调整 GC 时间。

    2. 创建 `restore-demo2-tidb-secret` secret：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
        ```

## 第 2 步：从持久卷恢复数据

1. 创建 Restore custom resource (CR)，将指定的备份数据恢复至 TiDB 集群：

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
      # # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
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

    在配置 `restore.yaml` 文件时，请参考以下信息：

    - 以上示例中，存储在 NFS 上 `local://${.spec.local.volume.nfs.path}/${.spec.local.prefix}/` 文件夹下的备份数据，被恢复到 `test2` 命名空间中的 TiDB 集群 `demo2`。更多持久卷存储相关配置，参考 [Local 存储字段介绍](backup-restore-cr.md#local-存储字段介绍)。

    - `.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释，参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。

    - 如果使用 TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，不需要在 Restore CR 中配置 `spec.to` 字段。

    - 更多 `Restore` CR 字段的详细解释，参考 [Restore CR 字段介绍](backup-restore-cr.md#restore-cr-字段介绍)。

2. 创建好 Restore CR 后，通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get rt -n test2 -owide
    ```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
