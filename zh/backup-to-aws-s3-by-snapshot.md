---
title: 基于 Snapshot 备份 TiDB 集群到 S3
summary: 介绍如何基于 Snapshot 使用 TiDB Operator 备份 TiDB 集群数据到 S3。
---

# 基于 Snapshot 备份 TiDB 集群到 S3

本文档介绍如何将 Kubernetes 上 部署在 AWS EBS 上的 TiDB 集群的数据备份到 S3。

本文档介绍的备份方法基于 TiDB Operator 的 CustomResourceDefinition (CRD) 实现，在 AWS EKS 上 部署的 TiDB 集群，使用 AWS EBS 卷，能够支持卷的 snapshot，可以使用本文描述的方法来进行 TiDB 集群的备份。

## 备份原理介绍

备份数据主要包含两部分内容：

   1. AWS EBS volume snapshot，卷快照主要包含 TiDB 集群的数据卷的快照。数据卷有 raft log 卷，和 data 卷。 raft log 卷存储 raft log 信息，data 卷存储事务数据。
   2. 备份元信息，包含 TiDB 集群的数据卷和对应快照的关系信息，集群级别的 resolved-ts, 以及 TiDB 集群想关的信息。

备份时，先停止 PD 相关的调度, 再获取 TiDB 集群全局一致性事务时间点集群级别的 resolved-ts，再发起 AWS EBS snapshot, 调用 AWS 服务为数据卷创建 snapshot. 当 snapshot 完成后，退出备份并保存集群备份元信息。

## 使用场景以及限制

如果你对数据备份有以下要求，可考虑使用 TiDB Operator 将 TiDB 集群数据以卷 snapshot 以及元数据的方式备份至 AWS S3：

- 需要备份的影响降到最小，如备份时 QPS < 5%，集群 CPU 以及内存占用足够小。
- 需要定期备份，且备份时间短。

如有其他备份需求，参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

> **限制**
>
> - TiDB Operator 只支持 TiDB v6.3 及以上版本。
> - TiDB 集群部署在 EKS 上，且使用的 AWS EBS 卷支持 snapshot
> - 使用此方法备份出的数据只能恢复到 TiDB 数据库中，无法恢复到其他数据库中。

## 基于 Snapshot 备份 TiDB 集备份

基于 AWS EBS Snapshot 备份支持全量备份与增量备份。数据备份以 AWS EBS snapshot 方式进行，同一个节点的第一次备份为全量 snapshot 备份，后续 snapshot 备份自动以增量方式进行。EBS Snapshot 备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

本文档假设对部署在 Kubernetes `test1` 这个命名空间中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

### 第 1 步：准备 EBS Snapshot 备份环境

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) 到执行备份的服务器。

2. 执行以下命令，在 `test1` 这个命名空间中，创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

3. 授予远程存储访问权限。

    - 如果使用 Amazon S3 来备份集群元数据，可以使用三种方式授予权限，可参考文档 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。

### 第 2 步：备份数据到兼容 S3 的存储

根据上一步选择的远程存储访问授权方式，你需要使用下面对应的方法将数据导出到兼容 S3 的存储上：

+ 方法 1：如果通过了 accessKey 和 secretKey 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    `backup-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      backupType: full
      backupMode: volume-snapshot
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
        # timeAgo: ${time}
        # options:
        # - --check-requirements=false
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 2：如果通过了 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    `backup-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      backupMode: volume-snapshot
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
        # timeAgo: ${time}
        # options:
        # - --check-requirements=false
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 3：如果通过了 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    `backup-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      backupType: full
      backupMode: volume-snapshot
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
        # timeAgo: ${time}
        # options:
        # - --check-requirements=false
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

在配置 `backup-aws-s3.yaml` 文件时，请参考以下信息：

- 自 TiDB Operator v1.1.6 版本起，如果需要基于卷 snapshot 的备份，只需要在 `spec.br.backupMode` 中指定备份模式 `volume-snapshot` 即可。
- Amazon S3 的存储相关配置，请参考 [S3 存储字段介绍](backup-restore-cr.md#s3-存储字段介绍)。
- `.spec.br` 中的一些参数是可选的，例如 `logLevel`、`statusAddr` 等。完整的 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
- 更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

创建好 `Backup` CR 后，TiDB Operator 会根据 `Backup` CR 自动开始备份。你可以通过如下命令查看备份状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -n test1 -o wide
```

## 删除备份的 Backup CR

备份完成后，你可能需要删除备份的 Backup CR。删除方法可参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
