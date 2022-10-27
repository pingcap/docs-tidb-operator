---
title: 基于 AWS EBS 卷快照的恢复
summary: 介绍如何将存储在 S3 上的备份元数据以及 EBS 卷快照恢复到 TiDB 集群。
---

# 基于 AWS EBS 卷快照的恢复

本文档介绍如何基于 AWS Elastic Block Store (EBS) 快照恢复 S3 上的备份数据到 TiDB 集群。

本文档介绍的恢复方法基于 TiDB Operator 的 CustomResourceDefinition (CRD)，基于 AWS EBS 快照的备份包含两部分数据，TiDB 集群数据卷的快照，以及快照和集群相关的备份元信息。

## 使用限制

- TiDB Operator 1.4 及以上的版本支持此功能
- 此功能只支持 TiDB v6.3 及以上版本。
- 只支持相同 TiKV 节点以及卷个数的恢复。即恢复集群 TiKV 个数以及卷相关的配置需要和备份集群的完全一致。
- 暂不支持 TiFlash, CDC，DM 和 binlog 相关节点的卷快照恢复

## 第 1 步：准备恢复环境

使用 TiDB Operator 将 S3 兼容存储上的备份元数据以及 EBS 快照恢复到 TiDB 之前，请按照以下步骤准备恢复环境。

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复需要的 RBAC 相关资源：

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

3. 授予远程存储访问权限。

    如果要恢复的数据在 Amazon S3 上，可以使用三种方式授予权限，请参考 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。

## 第 2 步：准备恢复的集群

参考[在 AWS EKS 上部署 TiDB 集群](deploy-on-aws-eks.md) 部署恢复数据的集群。

在 Spec 中加入 `recoveryMode: true` 字段。并执行以下命令在 `test2` 这个命名空间中创建恢复需要的 TiDB 集群相关资源：

```shell
kubectl apply -f tidb-cluster.yaml -n test2
```

## 第 3 步：将指定备份数据恢复到 TiDB 集群

根据上一步选择的远程存储访问授权方式，你需要使用下面对应的方法将备份数据恢复到 TiDB 集群：

+ 方法 1：如果通过 accessKey 和 secretKey 授权，你可以按照以下说明创建 `Restore` CR 恢复集群数据：

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
      br:
        cluster: demo2
        clusterNamespace: test2
        backupType: full
        restoreMode: volume-snapshot
        # logLevel: info
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 2：如果通过 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `Restore` CR 恢复集群数据：

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
        backupType: full
        restoreMode: volume-snapshot
        # logLevel: info
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 3: 如果通过 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `Restore` CR 恢复集群数据：

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
        backupType: full
        restoreMode: volume-snapshot
        # logLevel: info
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

在配置 `restore-aws-s3.yaml` 文件时，请参考以下信息：

- 关于 `restoreMode` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
- 关于兼容 S3 的存储相关配置，请参考 [S3 存储字段介绍](backup-restore-cr.md#s3-存储字段介绍)。
- `.spec.br` 中的一些参数为可选项，如 `logLevel`。可根据需要决定是否配置。

创建好 `Restore` CR 后，可通过以下命令查看恢复的状态：

```shell
kubectl get rt -n test2 -o wide
```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。