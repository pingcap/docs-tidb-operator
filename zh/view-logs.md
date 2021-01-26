---
title: 查看日志
summary: 介绍如何查看 TiDB 集群各组件日志以及 TiDB 慢查询日志。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/view-logs/']
---

# 查看日志

本文档介绍如何查看 TiDB 集群各组件日志，以及 TiDB 慢查询日志。

## TiDB 集群各组件日志

通过 TiDB Operator 部署的 TiDB 各组件默认将日志输出在容器的 `stdout` 和 `stderr` 中。可以通过下面的方法查看单个 Pod 的日志：

{{< copyable "shell-regular" >}}

```shell
kubectl logs -n ${namespace} ${pod_name}
```

如果这个 Pod 由多个 Container 组成，可以查看这个 Pod 内某个 Container 的日志：

{{< copyable "shell-regular" >}}

```shell
kubectl logs -n ${namespace} ${pod_name} -c ${container_name}
```

请通过 `kubectl logs --help` 获取更多查看 Pod 日志的方法。

## TiDB 组件慢查询日志

TiDB 3.0 及以上的版本中，默认配置下，慢查询日志和应用日志区分开，可以通过名为 `slowlog` 的 sidecar 容器查看慢查询日志：

{{< copyable "shell-regular" >}}

```shell
kubectl logs -n ${namespace} ${pod_name} -c slowlog
```

> **注意：**
>
> 慢查询日志的格式与 MySQL 的慢查询日志相同，但由于 TiDB 自身的特点，其中的一些具体字段可能存在差异，因此解析 MySQL 慢查询日志的工具不一定能完全兼容 TiDB 的慢查询日志。

## 使用单独持久卷存储慢查询日志

默认配置下，TiDB Operator 会新建名称为 `slowlog` 的 `EmptyDir` 卷来存储慢查询日志，`slowlog` 卷默认挂载到 `/var/log/tidb`。如果想使用单独的持久卷来存储慢查询日志，可以通过配置 `spec.tidb.slowLogVolumeName` 单独指定存储慢查询日志的持久卷名称，并在 `spec.tidb.storageVolumes` 或 `spec.tidb.additionalVolumes` 配置持久卷信息。下面分别演示使用 `spec.tidb.storageVolumes` 和 `spec.tidb.additionalVolumes` 配置持久卷。

### Spec.tidb.storageVolumes 配置

按照如下示例配置 TiDB Cluster，TiDB Operator 将使用持久卷 `${volumeName}` 存储慢查询日志。`spec.tidb.storageVolumes` 字段的具体配置方式可参考[多盘挂载](configure-a-tidb-cluster.md#多盘挂载)。

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  version: v4.0.9
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  discovery: {}
  ...
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    separateSlowLog: true  # 可省略
    slowLogVolumeName: ${volumeName}
    storageVolumes:
      # name 必须和 slowLogVolumeName 字段的值保持一致
      - name: ${volumeName}
        storageClassName: ${storageClass}
        storageSize: "1Gi"
        mountPath: ${mountPath}
    config: {}
```

### Spec.tidb.additionalVolumes 配置

下面以 NFS 为例配置 `spec.tidb.additionalVolumes`，具体支持的持久卷类型可参考 [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes)。TiDB Operator 将使用持久卷 `${volumeName}` 存储慢查询日志。 

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  version: v4.0.9
  configUpdateStrategy: RollingUpdate
  discovery: {}
  ...
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    separateSlowLog: true  # 可省略
    slowLogVolumeName: ${volumeName}
    additionalVolumes:
    # name 必须和 slowLogVolumeName 字段的值保持一致
    - name: ${volumeName}
      nfs:
        server: 192.168.0.2
        path: /nfs
    additionalVolumeMounts:
    # name 必须和 slowLogVolumeName 字段的值保持一致
    - name: ${volumeName}
      mountPath: ${mountPath}
    config: {}
```
