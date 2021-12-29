---
title: 恢复持久卷上的备份数据
summary: 介绍如何将存储在持久卷上的备份数据恢复到 TiDB 集群。
---

# 恢复持久卷上的备份数据

本文档介绍如何将存储在[持久卷](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/)上的备份数据恢复到 Kubernetes 环境中的 TiDB 集群。本文描述的持久卷指任何 [Kubernetes 支持的持久卷类型](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes)。本文以从网络文件系统 (NFS) 存储恢复数据到 TiDB 为例。

本文档介绍的恢复方法基于 TiDB Operator 的 CustomResourceDefinition (CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool/) 工具来恢复数据。

BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

如果你需要从持久卷导入备份数据到 TiDB 集群，并对数据恢复有以下要求，可使用本文介绍的恢复方案：

- 需要恢复的数据量较大，而且要求恢复速度较快
- 数据格式为 SST 文件（键值对）

> **注意：**
>
> - BR 只支持 TiDB v3.1 及以上版本。
> - BR 只能恢复从 TiDB 数据库导出的数据，无法恢复从其他数据库导出的数据。

## 第 1 步：准备恢复环境

> **注意：**
>
> 如果使用 TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，不需要在 Restore CR 中配置 `spec.to` 字段，并且可以省略以下创建 `restore-demo2-tidb-secret` secret 的步骤和[数据库账户权限](#数据库账户权限)步骤。

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) 到执行恢复的服务器。

2. 执行以下命令在 `test2` 这个命名空间中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

3. 创建 `restore-demo2-tidb-secret` secret，该 secret 存放用来访问 TiDB 服务的账号的密码：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
    ```

4. 确认可以从 Kubernetes 集群中访问用于存储备份数据的 NFS 服务器。

## 第 2 步：获取数据库权限

使用 BR 从持久卷恢复 TiDB 集群数据前，确保你拥有待恢复数据库的以下权限：

- `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：恢复前后，Restore CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

## 第 3 步：从持久卷恢复数据

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

2. 创建好 Restore CR 后，通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get rt -n test2 -owide
    ```

以上示例将存储在 NFS 上指定路径 `local://${.spec.local.volumeMount.mountPath}/${.spec.local.prefix}/` 文件夹下的备份数据恢复到 `test2` 命名空间中的 TiDB 集群 `demo2`。更多持久卷存储相关配置，参考 [Local 存储字段介绍](backup-restore-overview.md#local-存储字段介绍)。

以上示例中，`.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释，参考 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。

更多 `Restore` CR 字段的详细解释，参考 [Restore CR 字段介绍](backup-restore-overview.md#restore-cr-字段介绍)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
