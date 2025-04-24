---
title: 使用 Dumpling 备份 TiDB 数据到 Google Cloud Storage (GCS)
summary: 本文介绍如何使用 Dumpling 将 TiDB 集群数据备份到 Google Cloud Storage (GCS)。
---

# 使用 Dumpling 备份 TiDB 数据到 Google Cloud Storage (GCS)

本文档介绍如何使用 [Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview/) 将部署在 Google GKE 上的 TiDB 集群数据备份到 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs)。Dumpling 是一款数据导出工具，可将 TiDB 或 MySQL 中的数据导出为 SQL 或 CSV 格式，用于全量数据备份或导出。

## 准备 Dumpling 节点池

你可以在现有节点池中运行 Dumpling，也可以创建一个专用节点池。以下命令示例展示了如何创建一个新的节点池。请根据实际情况替换以下变量：

- `${clusterName}`：GKE 集群名称

```shell
gcloud container node-pools create dumpling \
    --cluster ${clusterName} \
    --machine-type n2-standard-4 \
    --num-nodes=1 \
    --node-labels=dedicated=dumpling
```

## 部署 Dumpling Job

### 创建凭证 ConfigMap

将从 Google Cloud Console 下载的 `service account key` 文件保存为 `google-credentials.json`，然后使用以下命令创建 ConfigMap：

```shell
kubectl -n ${namespace} create configmap google-credentials --from-file=google-credentials.json
```

### 配置 Dumpling Job

Dumpling Job 的配置文件 (`dumpling_job.yaml`) 示例如下。使用前，请替换以下变量：

- `${name}`：Job 名称
- `${namespace}`：Kubernetes 命名空间
- `${version}`：Dumpling 镜像版本
- Dumpling 的相关参数，请参考 [Dumpling 主要选项表](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview/#dumpling-主要选项表)。

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
        - name: ${name}
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
                  --threads=16 \
                  --rows=20000 \
                  --filesize=256MiB \
                  --database=test \
                  --filetype=csv \
                  --output=gcs://external/testfolder?credentials-file=/etc/config/google-credentials.json
          volumeMounts:
            - name: google-credentials
              mountPath: /etc/config
      volumes:
        - name: google-credentials
          configMap:
            name: google-credentials
      restartPolicy: Never
  backoffLimit: 0
```

### 创建 Dumpling Job

执行以下命令创建 Dumpling Job：

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster

envsubst < dumpling_job.yaml | kubectl apply -f -
```

### 查看 Dumpling Job 状态

运行以下命令查看 Dumpling Job 的 Pod 状态：

```shell
kubectl -n ${namespace} get pod ${name}
```

### 查看 Dumpling Job 日志

运行以下命令查看 Dumpling Job 的日志输出：

```shell
kubectl -n ${namespace} logs pod ${name}
```
