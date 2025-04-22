---
title: 使用 TiDB Lightning 恢复 Google Cloud Storage (GCS) 上的备份数据
summary: 介绍如何使用 TiDB Lightning 将存储在 Google Cloud Storage (GCS) 上的备份数据恢复到 TiDB 集群。
---

# 使用 TiDB Lightning 恢复 Google Cloud Storage (GCS) 上的备份数据

本文档介绍如何使用 [TiDB Lightning](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-overview/) 将 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/) 上的备份数据恢复到 TiDB 集群。TiDB Lightning 是一款将全量数据高速导入到 TiDB 集群的工具，本文采用[物理导入模式](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-physical-import-mode/)。有关 TiDB Lightning 的详细使用方式和配置参数，请参阅 [TiDB Lightning 官方文档](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-overview/)。

以下示例展示了如何将 GCS 上的备份数据恢复到 TiDB 集群。

## 准备运行 TiDB Lightning 的节点池

你可以在现有节点池中运行 TiDB Lightning，也可以创建一个专用节点池。以下命令示例展示了如何创建一个新的节点池，请根据实际情况替换以下变量：

- `${clusterName}`：GKE 集群名称

```shell
gcloud container node-pools create lightning \
    --cluster ${clusterName} \
    --machine-type n2-standard-4 \
    --num-nodes=1 \
    --node-labels=dedicated=lightning
```

## 部署 TiDB Lightning Job

### 创建凭证 ConfigMap

将从 Google Cloud Console 下载的 `service account key` 文件保存为 `google-credentials.json`，然后使用以下命令创建 ConfigMap：

```shell
kubectl -n ${namespace} create configmap google-credentials --from-file=google-credentials.json
```

### 配置 TiDB Lightning Job

以下是 TiDB Lightning Job 的配置文件 (`lightning_job.yaml`) 示例，请根据实际情况替换以下变量：

- `${name}`：Job 名称
- `${namespace}`：Kubernetes 命名空间
- `${version}`：TiDB Lightning 镜像版本
- `${storageClassName}`：存储类名称
- `${storage}`：存储大小
- TiDB Lightning 的相关参数，请参考 [TiDB Lightning 配置参数](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-configuration/)。

```yaml
# lightning_job.yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ${name}-sorted-kv
  namespace: ${namespace}
spec:
  storageClassName: ${storageClassName}
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: ${storage}
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${name}
  namespace: ${namespace}
data:
  config-file: |
    [lightning]
    level = "info"
    
    [checkpoint]
    enable = true
  
    [tidb]
    host = "basic-tidb"
    port = 4000
    user = "root"
    password = ""
    status-port = 10080
    pd-addr = "basic-pd:2379"
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ${name}
  namespace: ${namespace}
  labels:
    app.kubernetes.io/component: lightning
spec:
  template:
    spec:
      nodeSelector:
        dedicated: lightning
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app.kubernetes.io/component
                operator: In
                values:
                - lightning
            topologyKey: kubernetes.io/hostname
      containers:
        - name: tidb-lightning
          image: pingcap/tidb-lightning:${version}
          command:
            - /bin/sh
            - -c
            - |
              /tidb-lightning \
                  --status-addr=0.0.0.0:8289 \
                  --backend=local \
                  --sorted-kv-dir=/var/lib/sorted-kv \
                  --d=gcs://external/testfolder?credentials-file=/etc/config/google-credentials.json \
                  --config=/etc/tidb-lightning/tidb-lightning.toml \
                  --log-file="-"
          volumeMounts:
            - name: config
              mountPath: /etc/tidb-lightning
            - name: sorted-kv
              mountPath: /var/lib/sorted-kv
            - name: google-credentials
              mountPath: /etc/config
      volumes:
        - name: config
          configMap:
            name: ${name}
            items:
            - key: config-file
              path: tidb-lightning.toml
        - name: sorted-kv
          persistentVolumeClaim:
            claimName: ${name}-sorted-kv
        - name: google-credentials
          configMap:
            name: google-credentials
      restartPolicy: Never
  backoffLimit: 0
```

### 创建 TiDB Lightning Job

执行以下命令创建 TiDB Lightning Job：

```shell
export name=lightning
export version=v8.5.1
export namespace=tidb-cluster
export storageClassName=<your-storage-class>
export storage=250G

envsubst < lightning_job.yaml | kubectl apply -f -
```

### 查看 TiDB Lightning Job 状态

运行以下命令查看 TiDB Lightning Job 的 Pod 状态：

```shell
kubectl -n ${namespace} get pod ${name}
```

### 查看 TiDB Lightning Job 日志

运行以下命令查看 TiDB Lightning Job 的日志输出：

```shell
kubectl -n ${namespace} logs pod ${name}
```
