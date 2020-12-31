---
title: 使用 TiDB Lightning 恢复 TiDB 集群数据
summary: 介绍如何使用 TiDB Lightning 将存储在远程存储上的备份数据恢复到 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/restore-from-gcs/', '/docs-cn/tidb-in-kubernetes/dev/restore-from-s3/']
---
# 使用 TiDB Lightning 恢复 TiDB 集群数据

本文描述了将 Kubernetes 上通过 TiDB Operator 备份的数据恢复到 TiDB 集群的操作过程。底层通过使用 [TiDB Lightning](https://pingcap.com/docs/stable/how-to/get-started/tidb-lightning/#tidb-lightning-tutorial) 来进行集群恢复。

本文使用的恢复方式基于 TiDB Operator 新版（v1.1 及以上）的 CustomResourceDefinition (CRD) 实现。下面分别介绍恢复 GCS 和兼容 S3 的存储上的备份数据的操作方式。

## 使用 TiDB Lightning 恢复 GCS 上的备份数据

以下示例将存储在 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/) 上指定路径上的集群备份数据恢复到 TiDB 集群。

### 环境准备

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 存储访问授权

    如果使用 GCS 来备份恢复集群，可以使用服务账号密钥授予权限，参考 [GCS 账号授权](grant-permissions-to-remote-storage.md#GCS-账号授权) 授权访问 GCS 远程存储；

3. 创建 `restore-demo2-tidb-secret` secret，该 secret 存放用来访问 TiDB 集群的 root 账号和密钥：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=${password} --namespace=test2
    ```

### 数据库账户权限

| 权限 | 作用域 |
|:----|:------|
| SELECT | Tables |
| INSERT | Tables |
| UPDATE | Tables |
| DELETE | Tables |
| CREATE | Databases, tables |
| DROP | Databases, tables |
| ALTER | Tables |

### 将指定备份数据恢复到 TiDB 集群

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
      name: demo2-restore
      namespace: test2
    spec:
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        path: gcs://${backup_path}
      # storageClassName: local-storage
      storageSize: 1Gi
    ```

2. 创建好 `Restore` CR 后可通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

     ```shell
     kubectl get rt -n test2 -owide
     ```

以上示例将存储在 GCS 上指定路径 `spec.gcs.path` 的备份数据恢复到 TiDB 集群 `spec.to.host`。关于 GCS 的配置项可以参考 [backup-gcs.yaml](backup-using-dumpling.md#备份数据到-GCS) 中的配置。

更多 `Restore` CR 字段的详细解释如下：

* `.spec.metadata.namespace`： `Restore` CR 所在的 namespace。
* `.spec.to.host`：待恢复 TiDB 集群的访问地址。
* `.spec.to.port`：待恢复 TiDB 集群访问的端口。
* `.spec.to.user`：待恢复 TiDB 集群的访问用户。
* `.spec.to.tidbSecretName`：待恢复 TiDB 集群所需凭证的 secret。
* `.spec.storageClassName`：指定恢复时所需的 PV 类型。
* `.spec.storageSize`：恢复集群时指定所需的 PV 大小。该值应大于备份 TiDB 集群数据的大小。

> **注意：**
>
> TiDB Operator 会创建一个 PVC，用于数据恢复，备份数据会先从远端存储下载到 PV，然后再进行恢复。如果恢复完成后想要删掉这个 PVC，可以参考[删除资源](cheat-sheet.md#删除资源)先把恢复 Pod 删掉，然后再把 PVC 删掉。

## 使用 TiDB Lightning 恢复 S3 兼容存储上的备份数据

以下示例将兼容 S3 的存储（指定路径）上的备份数据恢复到 TiDB 集群。

### 环境准备

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 存储访问授权

    如果使用 Amazon S3 来恢复集群，可以使用三种权限授予方式授予权限，参考 [AWS 账号授权](grant-permissions-to-remote-storage.md#AWS-账号授权) 授权访问兼容 S3 的远程存储；使用 Ceph 作为后端存储测试恢复时，是通过 AccessKey 和 SecretKey 模式授权，设置方式可参考 [通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-AccessKey-和-SecretKey-授权)。

3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的用户所对应的密码。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

### 数据库账户权限

| 权限 | 作用域 |
|:----|:------|
| SELECT | Tables |
| INSERT | Tables |
| UPDATE | Tables |
| DELETE | Tables |
| CREATE | Databases, tables |
| DROP | Databases, tables |
| ALTER | Tables |

### 将指定备份数据恢复到 TiDB 集群

> **注意：**
>
> 由于 `rclone` 存在[问题](https://rclone.org/s3/#key-management-system-kms)，如果使用 Amazon S3 存储备份，并且 Amazon S3 开启了 `AWS-KMS` 加密，需要在本节示例中的 yaml 文件里添加如下 `spec.s3.options` 配置以保证备份恢复成功：
>
> ```yaml
> spec:
>   ...
>   s3:
>     ...
>     options:
>     - --ignore-checksum
> ```

1. 创建 Restore customer resource (CR)，将制定备份数据恢复至 TiDB 集群

    + 创建 Restore custom resource (CR)，通过 AccessKey 和 SecretKey 授权的方式将指定的备份数据由 Ceph 恢复至 TiDB 集群：

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
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: ceph
            endpoint: ${endpoint}
            secretName: s3-secret
            path: s3://${backup_path}
          # storageClassName: local-storage
          storageSize: 1Gi
        ```

    + 创建 Restore custom resource (CR)，通过 AccessKey 和 SecretKey 授权的方式将指定的备份数据由 Amazon S3 恢复至 TiDB 集群：

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
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: aws
            region: ${region}
            secretName: s3-secret
            path: s3://${backup_path}
          # storageClassName: local-storage
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
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: aws
            region: ${region}
            path: s3://${backup_path}
          # storageClassName: local-storage
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
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: aws
            region: ${region}
            path: s3://${backup_path}
          # storageClassName: local-storage
          storageSize: 1Gi
        ```

2. 创建好 `Restore` CR 后，可通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get rt -n test2 -owide
    ```

以上示例将兼容 S3 的存储（`spec.s3.path` 路径下）中的备份数据恢复到 TiDB 集群 (`spec.to.host`)。有关兼容 S3 的存储的配置项，可以参考 [备份数据到兼容 S3 的存储](backup-using-dumpling.md#备份数据到兼容-S3-的存储)。

更多 `Restore` CR 字段的详细解释：

* `.spec.metadata.namespace`：`Restore` CR 所在的 namespace。
* `.spec.to.host`：待恢复 TiDB 集群的访问地址。
* `.spec.to.port`：待恢复 TiDB 集群的访问端口。
* `.spec.to.user`：待恢复 TiDB 集群的访问用户。
* `.spec.to.secretName`：存储 `.spec.to.user` 用户的密码的 secret。
* `.spec.storageClassName`：指定恢复时所需的 PV 类型。
* `.spec.storageSize`：指定恢复集群时所需的 PV 大小。该值应大于 TiDB 集群备份的数据大小。

> **注意：**
>
> TiDB Operator 会创建一个 PVC，用于数据恢复，备份数据会先从远端存储下载到 PV，然后再进行恢复。如果恢复完成后想要删掉这个 PVC，可以参考[删除资源](cheat-sheet.md#删除资源)先把恢复 Pod 删掉，然后再把 PVC 删掉。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。