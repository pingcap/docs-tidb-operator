---
title: 使用 BR 工具恢复 GCS 上的备份数据
summary: 介绍如何使用 BR 工具将存储在 GCS 上的备份数据恢复到 TiDB 集群。
category: how-to
---

# 使用 BR 工具恢复 GCS 上的备份数据

本文描述了如何将存储在 GCS 存储的备份的数据恢复到 Kubernetes 环境中的 TiDB 集群的操作过程。底层通过使用 [`BR`](https://pingcap.com/docs-cn/v3.1/reference/tools/br/br) 来进行集群恢复。

本文使用的恢复方式基于 TiDB Operator 新版（v1.1 及以上）的 CustomResourceDefinition (CRD) 实现。

以下示例将存储在 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/) 上指定路径上的集群备份数据恢复到 TiDB 集群。

## 环境准备

1. 下载文件 [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建恢复所需的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 创建 `gcs-secret` secret。该 secret 存放用于访问 GCS 的凭证。`google-credentials.json` 文件存放用户从 GCP console 上下载的 service account key。具体操作参考 [GCP 官方文档](https://cloud.google.com/docs/authentication/getting-started)。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic gcs-secret --from-file=credentials=./google-credentials.json -n test1
	```

3. 创建 `restore-demo2-tidb-secret` secret，该 secret 存放用来访问 TiDB 集群的 root 账号和密钥：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
    ```

## 将指定备份数据恢复到 TiDB 集群

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
        # enableTLSClient: false
        # logLevel: info
        # statusAddr: <status-addr>
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: <time>
        # checksum: true
        # sendCredToTikv: true
      to:
        host: <tidb-host-ip>
        port: <tidb-port>
        user: <tidb-user>
        secretName: restore-demo2-tidb-secret
      gcs:
        projectId: <your-project-id>
        secretName: gcs-secret
        bucket: <my-bucket>
	    prefix: <my-folder>
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

2. 创建好 `Restore` CR 后可通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

     ```shell
     kubectl get rt -n test2 -owide
     ```

以上示例将存储在 GCS 上指定路径 `spec.gcs.bucket` 存储桶中 `spec.gcs.prefix`文件夹下的备份数据恢复到 TiDB 集群 `spec.to.host`。关于 GCS 的配置项可以参考 [backup-gcs.yaml](backup-to-gcs-br.md#备份数据到-gcs) 中的配置。

更多 `Restore` CR 字段的详细解释如下：

* `.spec.metadata.namespace`： `Restore` CR 所在的 namespace。
* `.spec.to.host`：待恢复 TiDB 集群的访问地址。
* `.spec.to.port`：待恢复 TiDB 集群访问的端口。
* `.spec.to.user`：待恢复 TiDB 集群的访问用户。
* `.spec.to.tidbSecretName`：待恢复 TiDB 集群所需凭证的 secret。
* `.spec.storageClassName`：指定恢复时所需的 PV 类型。如果不指定该项，则默认使用 TiDB Operator 启动参数中 `default-backup-storage-class-name` 指定的值（默认为 `standard`）。
* `.spec.storageSize`：恢复集群时指定所需的 PV 大小。该值应大于备份 TiDB 集群数据的大小。
