---
title: 使用 Dumpling 备份 TiDB 集群数据到 GCS
summary: 介绍如何使用 Dumpling 备份 TiDB 集群数据到 GCS。
category: how-to
aliases: ['/docs-cn/tidb-in-kubernetes/dev/backup-to-gcs-using-job/']
---

# 使用 Dumpling 备份 TiDB 集群数据到 GCS

本文档介绍如何将 Google GKE 上 TiDB 集群的数据备份到 [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs)  上。[Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview/) 是一款数据导出工具，该工具可以把存储在 TiDB/MySQL 中的数据导出为 SQL 或者 CSV 格式，可以用于完成逻辑上的全量备份或者导出。

## 准备运行 Dumpling 的节点池

你可以在已有节点池运行 Dumpling，以下为创建新节点池命令示例。请替换 ${clusterName} 为 GKE 集群名字，并根据实际情况替换对应字段。

```shell
gcloud container node-pools create dumpling --cluster ${clusterName} --machine-type n2-standard-4 --num-nodes=1 --node-labels=dedicated=dumpling
```

## 部署 Dumpling job 任务

为凭证创建 configmap，google-credentials.json 文件存放用户从 Google Cloud console 上下载的 service account key。具体操作参考 [Google Cloud 官方文档](https://cloud.google.com/docs/authentication/client-libraries)。

```shell
kubectl -n ${namespace) create configmap google-credentials --from-file=google-credentials.json
```

在节点池部署 Dumpling job 任务，以下为配置示例，请根据实际情况替换对应字段：

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

执行以下命令创建 Dumpling job 任务：

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster

envsubst < dumpling_job.yaml | kubectl apply -f -
```

查看 Dumpling job 任务：

```shell
kubectl -n $(namespace) get pod $(name)
```

查看 Dumpling job 任务日志：

```shell
kubectl -n $(namespace) logs pod $(name)
```
