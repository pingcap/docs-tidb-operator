---
title: 使用 Dumpling 备份 TiDB 数据到兼容 Amazon S3 的存储
summary: 本文介绍如何使用 Dumpling 将 TiDB 集群数据备份到兼容 Amazon S3 的存储。
---

# 使用 Dumpling 备份 TiDB 数据到兼容 Amazon S3 的存储

本文档介绍如何使用 [Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview/) 将部署在 AWS EKS 上的 TiDB 集群数据备份到兼容 Amazon S3 的存储。Dumpling 是一款数据导出工具，可将 TiDB 或 MySQL 中的数据导出为 SQL 或 CSV 格式，用于全量数据备份或导出。

## 准备 Dumpling 节点池

你可以在现有节点池中运行 Dumpling，也可以创建一个专用节点池。以下是创建新节点池的配置示例，请根据实际情况替换以下变量：

- `${clusterName}`：EKS 集群名称

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

## 部署 Dumpling Job

本章节介绍如何配置、部署以及监控 Dumpling Job。

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
                  --s3.region=${AWS_REGION} \
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

### 创建 Dumpling Job

执行以下命令创建 Dumpling Job：

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=<your-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_SESSION_TOKEN=<your-session-token> # 可选

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
