---
title: 基于 AWS EBS 卷快照的恢复
summary: 介绍如何将存储在 S3 上的备份元数据以及 EBS Snapshot 恢复到 TiDB 集群。
---

# 基于 AWS EBS 卷快照的恢复

本文档介绍如何基于 AWS Elastic Block Store (EBS) 快照恢复 S3 上的备份数据到 TiDB 集群。

本文档介绍的恢复方法基于 TiDB Operator 的 CustomResourceDefinition (CRD) 实现，基于 AWS EBS snapshot 的备份包含两部分数据，TiDB 集群数据卷的 snapshot, 以及 snapshot和集群相关的备份元信息。

## 恢复原理介绍

备份数据主要包含两部分内容：

   1. 集群数据卷快照，即 AWS EBS volume snapshot，卷快照主要包含 TiDB 集群的数据卷的快照。
   2. 备份元信息，包含 TiDB 集群的数据卷和对应快照的关系信息，快照对应的备份数据的物理时间点 backupts （它可能在备份时间点之前）, 以及 TiDB 集群相关的信息。

恢复时，先创建一个 Spec.recoveryMode:true 的 TiDB 集群，再 apply restore CRD 进行恢复。

recoveryMode:true 的 TiDB 集群将会以恢复的模式来启动. 这个模式的集群将只会启动 PD 节点，同时等待 apply restore CRD 来进行恢复集群。主要的步骤如下：

1. Apply restore CRD 后，会首先启动卷的恢复工作，即从 AWS S3 中，拉取备份元数据，根据元数据信息，创建相应的卷。
2. TiDB Operator 在卷恢复工作完成后，把相应的卷挂载到 TiKV 所在的节点，并启动 TiKV.
3. TiKV 启动完成后，TiDB Operator 启动新的 Job，进行业务数据的恢复。直到所有业务数据恢复到 backupts. Job 退出。TiKV 节点重启。
4. TiDB 节点启动，集群恢复完成。

## 推荐使用场景以及限制

### 使用场景

当使用 TiDB Operator 将 TiDB 集群数据备份到 AWS S3 后，如果需要从 AWS S3 将备份的 元数据以及相关的 snapshot 恢复到 TiDB 集群，请参考本文进行恢复。

### 使用限制

- TiDB Operator 1.4 及以上的版本支持此功能
- 此功能只支持 TiDB v6.3 及以上版本。
- 只支持相同 TiKV 节点以及卷个数的恢复。即恢复集群 TiKV 个数以及卷相关的配置需要和备份集群的完全一致。
- 暂不支持 TiFlash, CDC，DM 和 binlog 相关节点的卷快照恢复

## 第 1 步：准备恢复环境

使用 TiDB Operator 将 S3 兼容存储上的备份元数据以及 EBS snapshot 恢复到 TiDB 前，请按照以下步骤准备恢复环境。

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 授予远程存储访问权限。

    - 如果要恢复的数据在 Amazon S3 上，可以使用三种权限授予方式授予权限，可参考文档 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。

## 第 2 步：准备恢复的集群

参考 [在 AWS EKS 上部署 TiDB 集群](deploy-on-aws-eks.md) 的部署 TiDB 集群和监控来部署 TiDB 集群。

在 Spec 中加入 recoveryMode: true 字段。并执行以下命令在 `test2` 这个 namespace 中创建恢复需要的 TiDB 集群相关资源：

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f tidb-cluster.yaml -n test2
```

## 第 3 步：将指定备份数据恢复到 TiDB 集群

根据上一步选择的远程存储访问授权方式，你需要使用下面对应的方法将备份数据恢复到 TiDB 集群：

+ 方法 1: 如果通过了 accessKey 和 secretKey 的方式授权，你可以按照以下说明创建 `Restore` CR 恢复集群数据：

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

+ 方法 2: 如果通过了 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `Restore` CR 恢复集群数据：

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
        backupType: full
        restoreMode: volume-snapshot
        # logLevel: info
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 3: 如果通过了 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `Restore` CR 恢复集群数据：

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
- `.spec.br` 中的一些参数为可选项，如 `logLevel`。更多 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。

创建好 `Restore` CR 后，可通过以下命令查看恢复的状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get rt -n test2 -o wide
```

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。