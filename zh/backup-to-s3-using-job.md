---
title: 使用 Dumpling 备份 TiDB 集群数据到兼容 S3 的存储
summary: 介绍如何使用 Dumpling 备份 TiDB 集群数据到兼容 S3 的存储。
---

# 使用 Dumpling 备份 TiDB 集群数据到兼容 S3 的存储

本文档介绍如何使用 [Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview/) 将 AWS EKS 上 TiDB 集群的数据备份到兼容 S3 的存储上。Dumpling 是一款数据导出工具，可以把存储在 TiDB 或 MySQL 中的数据导出为 SQL 或 CSV 格式，可以用于完成逻辑上的全量数据备份或者导出。

## 准备运行 Dumpling 的节点池

你可以在已有节点池运行 Dumpling，以下为创建新节点池配置示例，替换 ${clusterName} 为 EKS 集群名字，并根据实际情况替换对应字段。

{{< copyable "" >}}

```yaml
# eks_dumpling.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: ${clusterName}
  region: us-west-2
availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c']

nodeGroups:
  - name: dumpling
    instanceType: c5.xlarge
    desiredCapacity: 1
    privateNetworking: true
    availabilityZones: ["us-west-2a"]
    labels:
      dedicated: dumpling
```

执行以下命令创建节点池：

```shell
eksctl create nodegroup -f eks_dumpling.yaml
```

## 部署 Dumpling job 任务

在节点池部署 Dumpling job 任务，以下为配置示例，根据实际情况替换对应字段。

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
                  --output=s3://bucket-path/
          env:
            - name: AWS_REGION
              value: ${AWS_REGION}
            - name: AWS_ACCESS_KEY_ID
              value: ${AWS_ACCESS_KEY_ID}
            - name: AWS_SECRET_ACCESS_KEY
              value: ${AWS_SECRET_ACCESS_KEY}
            - name: AWS_SESSION_TOKEN
              value: ${AWS_SESSION_TOKEN}
      restartPolicy: Never
  backoffLimit: 0
```

执行以下命令创建 Dumpling job 任务：

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_SESSION_TOKEN=

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
