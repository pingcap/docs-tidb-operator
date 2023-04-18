---
title: 基于 AWS EBS 卷快照的备份
summary: 介绍如何基于 EBS 卷快照使用 TiDB Operator 备份 TiDB 集群数据到 S3。
---

# 基于 AWS EBS 卷快照的备份

本文介绍如何将 Kubernetes 上部署在 AWS Elastic Kubernetes Service (EKS) 的 TiDB 集群备份到 AWS S3。

本文使用的备份方式基于 TiDB Operator 的 Custom Resource Definition(CRD)，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 获取集群数据，然后再将数据上传到 AWS 的存储上。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。如果 TiDB 集群部署在 AWS EKS 上且使用了 EBS 卷，则可以使用本文描述的方法进行备份。

## 推荐使用场景以及限制

### 使用场景

如果你对数据备份有以下要求，可考虑使用 TiDB Operator 将 TiDB 集群数据以卷快照以及元数据的方式备份至 AWS S3：

- 需要备份的影响降到最小，如备份对 QPS 和事务耗时影响小于 5%，不占用集群 CPU 以及内存。
- 需要快速备份和恢复，比如 1 小时内完成备份，2 小时内完成恢复。

如有其他备份需求，参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

### 使用限制

- 要使用此功能，TiDB Operator 应为 v1.4.0 及以上，TiDB 应为 v6.3.0 及以上。
- TiDB 集群部署在 EKS 上，且使用了 AWS EBS 卷。
- 暂不支持 TiFlash、TiCDC、DM 和 TiDB Binlog 相关节点的卷快照备份。

> **注意：**
>
> - 集群从低于 v6.5.0 版本升级到 v6.5.0 时，可能无法进行卷快照备份。详细解决办法见[升级后备份无法工作](backup-restore-faq.md#升级后备份无法工作)。
> - 要进行卷快照恢复，需要确保恢复时 TiKV 的配置与备份时的配置一致。可以从备份目标 S3 中，下载 `backupmeta` 文件，检查 `kubernetes.crd_tidb_cluster.spec` 字段，确认 TiKV 的配置是否一致。如果不一致，可参考[在 Kubernetes 中配置 TiDB 集群](configure-a-tidb-cluster.md)修改 TiKV 的配置。
> - 如果集群打开了 TiKV KMS [静态加密](https://docs.pingcap.com/zh/tidb/stable/encryption-at-rest#tikv-静态加密)，则需要在恢复阶段确保 AWS KMS 服务已启用主密钥。

## 备份操作

基于 AWS EBS 卷快照备份支持全量备份和增量备份。数据备份以 AWS EBS 卷快照方式进行，同一个节点的第一次备份为全量快照备份，后续备份自动以增量方式进行。EBS 快照备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

本文档假设对部署在 Kubernetes `test1` 这个命名空间中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

### 第 1 步：准备 EBS 卷快照备份环境

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) 到执行备份的服务器。

2. 执行以下命令，在 `test1` 这个命名空间中，创建备份需要的 RBAC 相关资源：

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

3. 授予远程存储访问权限。

    如果使用 Amazon S3 来备份集群数据并保存快照元数据，可以使用三种方式授予权限，请参考 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。

### 第 2 步：备份数据到 S3 存储

根据上一步选择的远程存储访问授权方式，你需要使用下面对应的方法将数据备份到 S3 的存储上：

+ 方法 1：如果通过 accessKey 和 secretKey 授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

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
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 2：如果通过 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

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
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 3：如果通过 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

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
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

在配置 `backup-aws-s3.yaml` 文件时，请参考以下信息：

- 如果要基于卷快照进行备份，需在 `spec.br.backupMode` 中指定备份模式为 `volume-snapshot`。
- Amazon S3 的存储相关配置，请参考 [S3 存储字段介绍](backup-restore-cr.md#s3-存储字段介绍)。
- `.spec.br` 中存在一些可选参数，如 `logLevel`，可根据需要决定是否配置。

创建好 `Backup` CR 后，TiDB Operator 会根据 `Backup` CR 自动开始备份。你可以通过如下命令查看备份状态：

```shell
kubectl get bk -n test1 -o wide
```

## 删除备份的 Backup CR

备份完成后，你可能需要删除备份的 Backup CR。删除方法可参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
