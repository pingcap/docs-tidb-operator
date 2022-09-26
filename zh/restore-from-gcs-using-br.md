---
title: 使用 BR 恢复 GCS 上的备份数据
summary: 介绍如何使用 BR 将存储在 GCS 上的备份数据恢复到 TiDB 集群。
---

# 使用 BR 恢复 GCS 上的备份数据

本文介绍如何将存储在 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/) 上的 SST 备份数据恢复到 Kubernetes 环境中的 TiDB 集群。

本文使用的恢复方式基于 TiDB Operator 新版（v1.1 及以上）的 CustomResourceDefinition (CRD) 实现，底层通过使用 [BR](https://docs.pingcap.com/zh/tidb/dev/backup-and-restore-tool) 来进行集群恢复。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

当使用 BR 将 TiDB 集群数据备份到 GCS 后，如果需要从 GCS 将备份的 SST（键值对）文件恢复到 TiDB 集群，请参考本文使用 BR 进行恢复。

> **注意：**
>
> - BR 只支持 TiDB v3.1 及以上版本。
> - BR 恢复的数据无法被同步到下游，因为 BR 直接导入 SST 文件，而下游集群目前没有办法获得上游的 SST 文件。

本文假设将存储在 GCS 上指定路径 `spec.gcs.bucket` 存储桶中 `spec.gcs.prefix` 文件夹下的备份数据恢复到 namespace `test2` 中的 TiDB 集群 `demo2`。

## 第 1 步：准备恢复环境

使用 BR 将 GCS 上的备份数据恢复到 TiDB 前，你需要准备恢复环境，并拥有数据库的相关权限。

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 授予远程存储访问权限。

    参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#gcs-账号授权)，授权访问 GCS 远程存储。

3. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要进行以下操作。如果你使用的 TiDB 为 v4.0.8 及以上版本，请跳过此步骤。

    1. 确保你拥有恢复数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于恢复前后调整 GC 时间。

    2. 创建 `restore-demo2-tidb-secret` secret 用于存放访问 TiDB 集群的 root 账号和密钥：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
        ```

## 第 2 步：将指定备份数据恢复到 TiDB 集群

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
      # # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      # to:
      #   host: ${tidb_host}
      #   port: ${tidb_port}
      #   user: ${tidb_user}
      #   secretName: restore-demo2-tidb-secret
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        bucket: ${bucket}
        prefix: ${prefix}
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

    在配置 `restore.yaml` 文件时，请参考以下信息：

    - 关于 GCS 存储相关配置，请参考 [GCS 存储字段介绍](backup-restore-cr.md#gcs-存储字段介绍)。
    - `.spec.br` 中的一些参数为可选项，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
    - 如果你使用的 TiDB 为 v4.0.8 及以上版本，BR 会自动调整 `tikv_gc_life_time` 参数，不需要在 Restore CR 中配置 `spec.to` 字段。
    - 更多 `Restore` CR 字段的详细解释，请参考 [Restore CR 字段介绍](backup-restore-cr.md#restore-cr-字段介绍)。

2. 创建好 `Restore` CR 后，通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

     ```shell
     kubectl get rt -n test2 -owide
     ```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
