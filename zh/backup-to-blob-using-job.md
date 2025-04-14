---
title: 使用 Dumpling 备份 TiDB 集群数据到 Blob 的存储
summary: 介绍如何使用 Dumpling 备份 TiDB 集群数据到 Blob 的存储。
---

# 使用 Dumpling 备份 TiDB 集群数据到 Blob 的存储

本文档介绍如何将 Azure AKS 上 TiDB 集群的数据备份到 Blob 的存储上。[Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview/) 是一款数据导出工具，该工具可以把存储在 TiDB/MySQL 中的数据导出为 SQL 或者 CSV 格式，可以用于完成逻辑上的全量备份或者导出。

## 准备运行 Dumpling 的节点池

你可以在已有节点池运行 Dumpling，以下为创建新节点池命令示例，替换 ${clusterName} 为 AKS 集群名字，替换 ${resourceGroup} 为资源组名字，并根据实际情况替换对应字段。

{{< copyable "shell-regular" >}}

```shell
az aks nodepool add --name dumpling \
    --cluster-name ${clusterName} \
    --resource-group ${resourceGroup} \
    --zones 1 2 3 \
    --node-count 1 \
    --labels dedicated=dumpling
```

## 部署 Dumpling job 任务

在节点池部署 Dumpling job 任务，以下为配置示例，根据实际情况替换对应字段

{{< copyable "" >}}

```yaml
# dumpling_job.yaml
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ${name}
  namespace: ${namespace}
  labels:
    app.kubernetes.io/component: dumpling
spec:
  template:
    spec:
      nodeSelector:
        dedicated: dumpling
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app.kubernetes.io/component
                operator: In
                values:
                - dumpling
            topologyKey: kubernetes.io/hostname
      containers:
        - name: $(name)
          image: pingcap/dumpling:${version}
          command:
            - /bin/sh
            - -c
            - |
              /dumpling \
                  --host=basic-tidb \
                  --port=4000 \
                  --user=root \
                  --password='' \
                  --s3.region=us-west-2 \
                  --threads=16 \
                  --rows=20000 \
                  --filesize=256MiB \
                  --database=test \
                  --filetype=csv \
                  --output=azure://external/testfolder?account-name=${accountname}&account-key=${accountkey}
      restartPolicy: Never
  backoffLimit: 0
```

执行以下命令创建 Dumpling job 任务：

{{< copyable "shell-regular" >}}

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster
export accountname=
export accountkey=

envsubst < dumpling_job.yaml | kubectl apply -f -
```

查看 Dumpling job 任务

{{< copyable "shell-regular" >}}

```shell
kubectl -n $(namespace) get pod $(name)
```

查看 Dumpling job 任务日志

{{< copyable "shell-regular" >}}

```shell
kubectl -n $(namespace) logs pod $(name)
```
