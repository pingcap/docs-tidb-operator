---
title: 使用 TiDB Lightning 恢复 Blob 存储上的备份数据
summary: 了解如何使用 TiDB Lightning 将 Blob 存储上的备份数据恢复到 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/restore-from-blob-using-job/']
---

# 使用 TiDB Lightning 恢复 Blob 存储上的备份数据

本文档介绍如何将 Blob 存储上的备份数据恢复到 TiDB 集群。 TiDB Lightning 是一款将全量数据高速导入到 TiDB 集群的工具，本文采用物理导入方式，具体 TiDB Lightning 使用方式和配置参数请参阅[TiDB Lightning 相关文档](https://docs.pingcap.com/zh/tidb/stable/tidb-lightning-overview/)。

以下示例将 Blob 的存储上的备份数据恢复到 TiDB 集群。

## 准备运行 TiDB Lightning 的节点池

你可以在已有节点池运行 TiDB Lightning，以下为创建新节点池命令示例，替换 ${clusterName} 为 AKS 集群名字，替换 ${resourceGroup} 为资源组名字，并根据实际情况替换对应字段。

{{< copyable "shell-regular" >}}

```shell
az aks nodepool add --name lightning \
    --cluster-name ${clusterName} \
    --resource-group ${resourceGroup} \
    --zones 1 2 3 \
    --node-count 1 \
    --labels dedicated=lightning
```

## 部署 TiDB Lightning job 任务

在节点池部署 TiDB Lightning job 任务，以下为配置示例，根据实际情况替换对应字段

{{< copyable "" >}}

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
                  --d=azure://external/testfolder?account-name=${accountname}&account-key=${accountkey} \
                  --config=/etc/tidb-lightning/tidb-lightning.toml \
                  --log-file="-"
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

执行以下命令创建 TiDB Lightning job 任务，请根据实际情况调整 storage 磁盘大小：

{{< copyable "shell-regular" >}}

```shell
export name=lightning
export version=v8.5.1
export namespace=tidb-cluster
export storageClassName=
export storage=250G
export accountname=
export accountkey=

envsubst < lightning_job.yaml | kubectl apply -f -
```

查看 TiDB Lightning job 任务

{{< copyable "shell-regular" >}}

```shell
kubectl -n $(namespace) get pod $(name)
```

查看 TiDB Lightning job 任务日志

{{< copyable "shell-regular" >}}

```shell
kubectl -n $(namespace) logs pod $(name)
```
