---
title: 使用 TiDB Lightning 恢复 GCS 上的备份数据
summary: 介绍如何使用 TiDB Lightning 将存储在 GCS 上的备份数据恢复到 TiDB 集群。
---

# 使用 TiDB Lightning 恢复 GCS 上的备份数据

本文档介绍如何将 Google Cloud Storage (GCS) 存储上的备份数据恢复到 TiDB 集群。TiDB Lightning 是一款将全量数据高速导入到 TiDB 集群的工具，本文采用[物理导入模式](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-physical-import-mode/)。具体 TiDB Lightning 使用方式和配置参数，请参阅 [TiDB Lightning 相关文档](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-overview/)。

以下示例将 GCS 的存储上的备份数据恢复到 TiDB 集群。

## 准备运行 TiDB Lightning 的节点池

你可以在已有节点池运行 TiDB Lightning，以下为创建新节点池命令示例，替换 ${clusterName} 为 GKE 集群名字，并根据实际情况替换对应字段。

```shell
gcloud container node-pools create lightning --cluster ${clusterName} --machine-type n2-standard-4 --num-nodes=1 --node-labels=dedicated=lightning
```

## 部署 TiDB Lightning job 任务

为凭证创建 configmap，google-credentials.json 文件存放用户从 Google Cloud console 上下载的 service account key。具体操作参考 [Google Cloud 官方文档](https://cloud.google.com/docs/authentication/client-libraries)。

```shell
kubectl -n ${namespace) create configmap google-credentials --from-file=google-credentials.json
```

在节点池部署 TiDB Lightning job 任务，以下为配置示例，根据实际情况替换对应字段。

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

执行以下命令创建 TiDB Lightning job 任务，请根据实际情况调整 storage 磁盘大小：

```shell
export name=lightning
export version=v8.5.1
export namespace=tidb-cluster
export storageClassName=
export storage=250G

envsubst < lightning_job.yaml | kubectl apply -f -
```

查看 TiDB Lightning job 任务：

```shell
kubectl -n $(namespace) get pod $(name)
```

查看 TiDB Lightning job 任务日志

{{< copyable "shell-regular" >}}

```shell
kubectl -n $(namespace) logs pod $(name)
```
