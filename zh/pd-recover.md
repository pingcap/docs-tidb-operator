---
title: 使用 PD Recover 恢复 PD 集群
summary: 使用 PD Recover 恢复 PD 集群
category: reference
---

# 使用 PD Recover 恢复 PD 集群

[PD Recover](https://pingcap.com/docs-cn/stable/reference/tools/pd-recover) 是对 PD 进行灾难性恢复的工具，用于恢复无法正常启动或服务的 PD 集群。

## 下载 pd-recover

下载 TiDB 官方安装包：

{{< copyable "shell-regular" >}}

```
wget https://download.pingcap.org/tidb-${version}-linux-amd64.tar.gz
```

`${version}` 是 TiDB 集群版本，例如，`v4.0.0-rc`。

解压安装包：

{{< copyable "shell-regular" >}}

```
tar -xzf tidb-${version}-linux-amd64.tar.gz
```

`pd-recover` 在 `tidb-${version}-linux-amd64/bin` 目录下。

## 使用 pd-recover 恢复 PD 集群

### 获取 Cluster ID

{{< copyable "shell-regular" >}}

```
kubectl get tc ${cluster_name} -n ${namespace} -o='go-template={{.status.clusterID}}{{"\n"}}'
```

示例：

```
kubectl get tc test -n test -o='go-template={{.status.clusterID}}{{"\n"}}'
6821434242797747735
```

### 获取 Alloc ID

Alloc ID 是 TiKV 或者 TiFlash 分配的 StoreID。

{{< copyable "shell-regular" >}}

```
kubectl get tc ${cluster_name} -n ${namespace} -o='go-template={{range .status.tikv.stores}}{{.id}}{{"\n"}}{{end}}'
```

如果集群中部署了 TiFlash，还需要查看 TiFlash 的 StoreID：

{{< copyable "shell-regular" >}}

```
kubectl get tc ${cluster_name} -n ${namespace} -o='go-template={{range .status.tiflash.stores}}{{.id}}{{"\n"}}{{end}}'
```

示例：

```
kubectl get tc test -n test -o='go-template={{range .status.tikv.stores}}{{.id}}{{"\n"}}{{end}}'
1
47
69
```

使用 `pd-recover` 恢复 PD 集群时，需要指定 `alloc-id`，`alloc-id` 的值需要是一个比当前最大的 `Alloc ID` 更大的值。

### 恢复 PD 集群 Pod

通过如下命令设置 `spec.pd.replicas` 为 `0`：

{{< copyable "shell-regular" >}}

```
kubectl edit tc ${cluster_name} -n ${namespace}
```

由于此时 PD 集群异常，TiDB Operator 无法将上面的改动同步到 PD Statefulset，所以需要通过如下命令设置 PD Statefulset `spec.replicas` 为 `0`：

{{< copyable "shell-regular" >}}

```
kubectl edit sts ${cluster_name}-pd -n ${namespace}
```

通过如下命令确认 PD Pod 已经被删除：

{{< copyable "shell-regular" >}}

```
kubectl get pod -n ${namespace}
```

确认所有 PD Pod 已经被删除后，通过如下命令删除 PD Pod 绑定的 PVC：

{{< copyable "shell-regular" >}}

```
kubectl delete pvc -l app.kubernetes.io/component=pd,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
```

PVC 删除完成后，扩容 PD 集群至一个 Pod。

通过如下命令设置 `spec.pd.replicas` 为 `1`：

{{< copyable "shell-regular" >}}

```
kubectl edit tc ${cluster_name} -n ${namespace}
```

由于此时 PD 集群异常，TiDB Operator 无法将上面的改动同步到 PD Statefulset，所以需要通过如下命令设置 PD Statefulset `spec.replicas` 为 `1`：

{{< copyable "shell-regular" >}}

```
kubectl edit sts ${cluster_name}-pd -n ${namespace}
```

通过如下命令确认 PD Pod 已经启动：

{{< copyable "shell-regular" >}}

```
kubectl get pod -n ${namespace}
```

### 使用 pd-recover 恢复集群

通过 `port-forward` 暴露 PD 服务：

{{< copyable "shell-regular" >}}

```
kubectl port-forward -n ${namespace} svc/${cluster_name}-pd 2379:2379
```

打开一个**新**终端标签或窗口，进入到 `pd-recover` 所在的目录，使用 `pd-recover` 恢复 PD 集群：

{{< copyable "shell-regular" >}}

```
./pd-recover -endpoints http://127.0.0.1:2379 -cluster-id ${cluster_id} -alloc-id ${alloc_id}
```

`${cluster_id}` 是[获取 Cluster ID](#获取-cluster-id) 步骤中获取的 Cluster ID，`${alloc_id}` 是一个比[获取 Alloc ID](#获取-alloc-id) 步骤中获取的最大的 `Alloc ID` 更大的值。

`pd-recover` 命令执行成功后，会打印如下输出：

```
recover success! please restart the PD cluster
```

回到 `port-forward` 命令所在窗口，按 `Ctrl + C` 停止并退出。

### 重启 PD Pod

{{< copyable "shell-regular" >}}

```
kubectl delete pod ${cluster_name}-pd-0 -n ${namespace}
```

Pod 正常启动后，通过 `port-forward` 暴露 PD 服务：

{{< copyable "shell-regular" >}}

```
kubectl port-forward -n ${namespace} svc/${cluster_name}-pd 2379:2379
```

打开一个**新**终端标签或窗口，通过如下命令确认 Cluster ID 为设置的 ID：

{{< copyable "shell-regular" >}}

```
curl 127.0.0.1:2379/pd/api/v1/cluster
```

回到 `port-forward` 命令所在窗口，按 `Ctrl + C` 停止并退出。

### 扩容 PD 集群

通过如下命令设置 `spec.pd.replicas` 为期望的 Pod 数量：

{{< copyable "shell-regular" >}}

```
kubectl edit tc ${cluster_name} -n ${namespace}
```

### 重启 TiDB 和 TiKV

{{< copyable "shell-regular" >}}

```
kubectl delete pod -l app.kubernetes.io/component=tidb,app.kubernetes.io/instance=${cluster_name} -n ${namespace} && 
kubectl delete pod -l app.kubernetes.io/component=tikv,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
```
