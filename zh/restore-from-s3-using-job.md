---
title: 使用 TiDB Lightning 恢复 Amazon S3 兼容存储上的备份数据
summary: 介绍如何使用 TiDB Lightning 将兼容 Amazon S3 存储上的备份数据恢复到 TiDB 集群。
---

# 使用 TiDB Lightning 恢复 Amazon S3 兼容存储上的备份数据

本文档介绍如何使用 [TiDB Lightning](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-overview/) 将 Amazon S3 兼容存储上的备份数据恢复到 TiDB 集群。TiDB Lightning 是一款将全量数据高速导入到 TiDB 集群的工具，本文采用[物理导入模式](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-physical-import-mode/)。有关 TiDB Lightning 的详细使用方式和配置参数，请参阅 [TiDB Lightning 官方文档](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-overview/)。

以下示例展示了如何将兼容 Amazon S3 的存储上的备份数据恢复到 TiDB 集群。

## 准备运行 TiDB Lightning 的节点池

你可以在现有节点池中运行 TiDB Lightning，也可以创建一个专用节点池。以下是创建新节点池的配置示例，请根据实际情况替换以下变量：

- `${clusterName}`：EKS 集群名称

```yaml
# eks_lightning.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: ${clusterName}
  region: us-west-2
availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c']

nodeGroups:
  - name: lightning
    instanceType: c5.xlarge
    desiredCapacity: 1
    privateNetworking: true
    availabilityZones: ["us-west-2a"]
    labels:
      dedicated: lightning
```

执行以下命令创建节点池：

```shell
eksctl create nodegroup -f eks_lightning.yaml
```

## 部署 TiDB Lightning Job

本章节介绍如何配置、部署以及监控 TiDB Lightning Job。

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
                  --d=s3://external/testfolder \
                  --config=/etc/tidb-lightning/tidb-lightning.toml \
                  --log-file="-"
          env:
            - name: AWS_REGION
              value: ${AWS_REGION}
            - name: AWS_ACCESS_KEY_ID
              value: ${AWS_ACCESS_KEY_ID}
            - name: AWS_SECRET_ACCESS_KEY
              value: ${AWS_SECRET_ACCESS_KEY}
            - name: AWS_SESSION_TOKEN
              value: ${AWS_SESSION_TOKEN}
          volumeMounts:
            - name: config
              mountPath: /etc/tidb-lightning
            - name: sorted-kv
              mountPath: /var/lib/sorted-kv
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
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=<your-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_SESSION_TOKEN=<your-session-token> # 可选

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
