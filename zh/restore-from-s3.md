---
title: 恢复 S3 兼容存储上的备份数据
summary: 介绍如何将兼容 S3 存储的备份数据恢复到 TiDB 集群。
category: how-to
---

# 恢复 S3 兼容存储上的备份数据

本文描述了将 Kubernetes 上通过 TiDB Operator 备份的数据恢复到 TiDB 集群的操作过程。底层通过使用 [`loader`](https://pingcap.com/docs-cn/dev/reference/tools/loader) 来恢复数据。

本文使用的恢复方式基于 TiDB Operator 新版（v1.1 及以上）的 CustomResourceDefinition (CRD) 实现。基于 Helm Charts 实现的备份和恢复方式可参考[基于 Helm Charts 实现的 TiDB 集群备份恢复](backup-and-restore-using-helm-charts.md)。

## AWS 账号的三种权限授予方式

如果使用 Amazon S3 来备份恢复集群，可以使用三种权限授予方式授予权限，参考[使用 BR 工具备份 AWS 上的 TiDB 集群](backup-to-aws-s3-using-br.md#aws-账号权限授予的三种方式)，使用 Ceph 作为后端存储测试备份恢复时，是通过 AccessKey 和 SecretKey 模式授权。

以下示例将兼容 S3 的存储（指定路径）上的备份数据恢复到 TiDB 集群。

## 环境准备

参考[环境准备](restore-from-aws-s3-using-br.md#环境准备)

## 将指定备份数据恢复到 TiDB 集群

1. 创建 Restore customer resource (CR)，将制定备份数据恢复至 TiDB 集群

+ 创建 Restore custom resource (CR)，通过 AccessKey 和 SecretKey 授权的方式将指定的备份数据恢复至 TiDB 集群：

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
      name: demo2-restore
      namespace: test2
    spec:
      backupType: full
      to:
        host: <tidb-host-ip>
        port: <tidb-port>
        user: <tidb-user>
        secretName: restore-demo2-tidb-secret
      s3:
        provider: ceph
        endpoint: http://10.233.2.161
        secretName: s3-secret
        path: s3://<path-to-backup>
      storageClassName: local-storage
      storageSize: 1Gi
    ```

+ 创建 Restore custom resource (CR)，通过 AccessKey 和 SecretKey 授权的方式将指定的备份数据恢复至 TiDB 集群：

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
      name: demo2-restore
      namespace: test2
    spec:
      backupType: full
      to:
        host: <tidb-host-ip>
        port: <tidb-port>
        user: <tidb-user>
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        secretName: s3-secret
        path: s3://<path-to-backup>
      storageClassName: local-storage
      storageSize: 1Gi
    ```

+ 创建 Restore custom resource (CR)，通过 IAM 绑定 Pod 授权的方式将指定的备份数据恢复至 TiDB 集群：

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
      name: demo2-restore
      namespace: test2
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
      spec:
        backupType: full
        to:
          host: <tidb-host-ip>
          port: <tidb-port>
          user: <tidb-user>
          secretName: restore-demo2-tidb-secret
        s3:
          provider: aws
          region: us-west-1
          path: s3://<path-to-backup>
        storageClassName: local-storage
        storageSize: 1Gi
    ```

 + 创建 Restore custom resource (CR)，通过 IAM 绑定 ServiceAccount 授权的方式将指定的备份数据恢复至 TiDB 集群：

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
      name: demo2-restore
      namespace: test2
      spec:
        backupType: full
        serviceAccount: tidb-backup-manager
        to:
          host: <tidb-host-ip>
          port: <tidb-port>
          user: <tidb-user>
          secretName: restore-demo2-tidb-secret
        s3:
          provider: aws
          region: us-west-1
          path: s3://<path-to-backup>
        storageClassName: local-storage
        storageSize: 1Gi
    ```


2. 创建好 `Restore` CR 后可通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

     ```shell
     kubectl get rt -n test2 -owide
     ```

以上示例将兼容 S3 的存储（`spec.s3.path` 路径下）中的备份数据恢复到 TiDB 集群 (`spec.to.host`)。有关兼容 S3 的存储的配置项，可以参考 [backup-s3.yaml](backup-to-s3.md#备份数据到兼容-s3-的存储)。

更多 `Restore` CR 字段的详细解释：

* `.spec.metadata.namespace`：`Restore` CR 所在的 namespace。
* `.spec.to.host`：待恢复 TiDB 集群的访问地址。
* `.spec.to.port`：待恢复 TiDB 集群的访问端口。
* `.spec.to.user`：待恢复 TiDB 集群的访问用户。
* `.spec.to.tidbSecretName`：待恢复 TiDB 集群所需凭证的 secret。
* `.spec.storageClassName`：指定恢复时所需的 PV 类型。如果不指定该项，则默认使用 TiDB Operator 启动参数中 `default-backup-storage-class-name` 指定的值（默认为 `standard`）。
* `.spec.storageSize`：指定恢复集群时所需的 PV 大小。该值应大于备份 TiDB 集群的数据大小。
