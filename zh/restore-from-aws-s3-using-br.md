---
title: 使用 BR 恢复 S3 兼容存储上的备份数据
summary: 介绍如何使用 BR 恢复 Amazon S3 兼容存储上的备份数据。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/restore-from-aws-s3-using-br/']
---

# 使用 BR 恢复 S3 兼容存储上的备份数据

本文介绍如何将 S3 兼容存储上的 SST 备份数据恢复到 AWS Kubernetes 环境中的 TiDB 集群，

本文使用的恢复方式基于 TiDB Operator 的 Custom Resource Definition (CRD) 实现，底层使用 [BR](https://pingcap.com/docs-cn/stable/br/backup-and-restore-tool/) 进行数据恢复。

BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

当使用 BR 将 TiDB 集群数据备份到 Amazon S3 后，如果需要从 Amazon S3 将备份的 SST （键值对） 文件恢复到 TiDB 集群，请参考本文使用 BR 进行恢复。

> **注意：**
>
> - BR 只支持 TiDB v3.1 及以上版本。
> - BR 恢复的数据无法被同步到下游，因为 BR 直接导入 SST 文件，而下游集群目前没有办法获得上游的 SST 文件。

本文假设将存储在 Amazon S3 上指定路径 `spec.s3.bucket` 存储桶中 `spec.s3.prefix` 文件夹下的备份数据恢复到 namespace `test2` 中的 TiDB 集群 `demo2`。下面是具体的操作过程。

## 第 1 步：准备恢复环境

使用 BR 将 S3 兼容存储上的备份数据恢复到 TiDB 前，请按照以下步骤准备恢复环境。

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 授予远程存储访问权限。

    - 如果要恢复的数据在 Amazon S3 上，可以使用三种权限授予方式授予权限，可参考文档 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。
    - 如果要恢复的数据在其他兼容 S3 的存储上，例如 Ceph、MinIO，可以使用 AccessKey 和 SecretKey 模式授权，可参考文档[通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-accesskey-和-secretkey-授权)。

3. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要进行以下操作。如果你使用的 TiDB 为 v4.0.8 及以上版本，请跳过此步骤。

    1. 确保你拥有恢复数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于恢复前后调整 GC 时间。

    2. 创建 `restore-demo2-tidb-secret` secret 用于存放访问 TiDB 集群的 root 账号和密钥。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=password=${password} --namespace=test2
        ```

## 第 2 步：将指定备份数据恢复到 TiDB 集群

根据上一步选择的远程存储访问授权方式，你需要使用下面对应的方法将备份数据恢复到 TiDB：

+ 方法 1: 创建 `Restore` CR，通过 accessKey 和 secretKey 授权的方式恢复集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f resotre-aws-s3.yaml
    ```

    `restore-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
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
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 2: 创建 `Restore` CR，通过 IAM 绑定 Pod 授权的方式备份集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    `restore-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      br:
        cluster: demo2
        sendCredToTikv: false
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 3: 创建 `Restore` CR，通过 IAM 绑定 ServiceAccount 授权的方式备份集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    `restore-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
    spec:
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo2
        sendCredToTikv: false
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

在配置 `restore-aws-s3.yaml` 文件时，请参考以下信息：

- 关于兼容 S3 的存储相关配置，请参考 [S3 存储字段介绍](backup-restore-overview.md#s3-存储字段介绍)。
- `.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。
- 如果你使用的 TiDB 为 v4.0.8 及以上版本，BR 会自动调整 `tikv_gc_life_time` 参数，不需要在 Restore CR 中配置 `spec.to` 字段。
- 更多 `restore` CR 字段的详细解释，请参考 [Restore CR 字段介绍](backup-restore-overview.md#restore-cr-字段介绍)。

创建好 `Restore` CR 后，可通过以下命令查看恢复的状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get rt -n test2 -o wide
```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
