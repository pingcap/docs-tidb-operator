---
title: 为已有 TiDB 集群部署异构集群
summary: 本文档介绍如何为已有的 TiDB 集群部署一个异构集群。
---

# 为已有 TiDB 集群部署异构集群

本文介绍如何为已有的 TiDB 集群部署一个异构集群。异构集群，指的是与已有 TiDB 集群不同配置的节点构成的集群。

## 使用场景

基于已经存在的一个 TiDB 集群，如果你需要创建一个差异化配置的实例节点满足不同场景的需要，可使用本文介绍的部署方案。

示例场景：

- 创建不同配置不同 Label 的 TiKV 集群用于热点调度
- 创建不同配置的 TiDB 集群分别用于 TP 和 AP 查询

## 前置条件

* 已经存在一个 TiDB 集群。

如果尚未部署 TiDB 集群，可以参考 [在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)进行部署。

## 部署异构集群

1. 为异构集群新建一个集群配置文件。

    例如，将如下配置存为 `cluster.yaml` 文件，并替换 `${heterogeneous_cluster_name}` 为自己想命名的异构集群名字，替换 `${origin_cluster_name}` 为想要加入的已有集群名称。

    > **注意**:
    >
    > 相比于普通 TiDB 的集群配置文件，异构集群配置文件的唯一区别是，你需要配置 `spec.cluster.name` 字段将该异构集群加入到已有的 TiDB 集群。

    {{< copyable "" >}}

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
    name: ${heterogeneous_cluster_name}
    spec:
    configUpdateStrategy: RollingUpdate
    version: v5.2.1
    timezone: UTC
    pvReclaimPolicy: Delete
    discovery: {}
    cluster:
        name: ${origin_cluster_name}
    tikv:
        baseImage: pingcap/tikv
        maxFailoverCount: 0
        replicas: 1
        # if storageClassName is not set, the default Storage Class of the Kubernetes cluster will be used
        # storageClassName: local-storage
        requests:
        storage: "100Gi"
        config: {}
    tidb:
        baseImage: pingcap/tidb
        maxFailoverCount: 0
        replicas: 1
        service:
        type: ClusterIP
        config: {}
    tiflash:
        baseImage: pingcap/tiflash
        maxFailoverCount: 0
        replicas: 1
        storageClaims:
        - resources:
            requests:
                storage: 100Gi
    ```

2. 依据你要对异构集群的各节点进行的差异化设置，修改 `cluster.yaml` 文件中的其他配置项。

3. 执行以下命令创建集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create -f cluster.yaml -n ${namespace}
    ```

### 部署集群监控

1. 编辑 TidbMonitor Custom Resource (CR)：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tm ${cluster_name} -n ${namespace}
    ```

2. 基于现有的 TidbMonitor CR 文件，替换 `${origin_cluster_name}` 为想要加入的集群名称，替换 `${heterogeneous_cluster_name}` 为异构集群名称：

    {{< copyable "" >}}

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbMonitor
    metadata:
    name: heterogeneous
    spec:
    clusters:
        - name: ${origin_cluster_name}
        - name: ${heterogeneous_cluster_name}
    prometheus:
        baseImage: prom/prometheus
        version: v2.11.1
    grafana:
        baseImage: grafana/grafana
        version: 6.1.6
    initializer:
        baseImage: pingcap/tidb-monitor-initializer
        version: v5.2.1
    reloader:
        baseImage: pingcap/tidb-monitor-reloader
        version: v1.0.1
    imagePullPolicy: IfNotPresent
    ```

## 部署 TLS 异构集群

开启异构集群 TLS 需要显示声明，需要创建新的 `Secret` 证书文件，使用和目标集群相同的 CA (Certification Authority) 颁发。如果使用 `cert-manager` 方式，需要使用和目标集群相同的 `Issuer` 来创建 `Certificate`。

为异构集群创建证书的详细步骤，可参考以下文档：

- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)

### 创建一个异构 TLS 集群

将如下配置存为 `cluster.yaml` 文件，并替换 `${heterogeneous_cluster_name}` 为自己想命名的异构集群名字，`${origin_cluster_name}` 替换为想要加入的已有集群名称:

{{< copyable "" >}}

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: ${heterogeneous_cluster_name}
spec:
  tlsCluster:
    enabled: true
  configUpdateStrategy: RollingUpdate
  version: v5.2.1
  timezone: UTC
  pvReclaimPolicy: Delete
  discovery: {}
  cluster:
    name: ${origin_cluster_name}
  tikv:
    baseImage: pingcap/tikv
    maxFailoverCount: 0
    replicas: 1
    # if storageClassName is not set, the default Storage Class of the Kubernetes cluster will be used
    # storageClassName: local-storage
    requests:
      storage: "100Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    maxFailoverCount: 0
    replicas: 1
    service:
      type: ClusterIP
    config: {}
    tlsClient:
      enabled: true
  tiflash:
    baseImage: pingcap/tiflash
    maxFailoverCount: 0
    replicas: 1
    storageClaims:
      - resources:
          requests:
            storage: 100Gi
```

`spec.tlsCluster.enabled` 表示组件间是否开启 TLS，`spec.tidb.tlsClient.enabled` 表示 MySQL 客户端是否开启 TLS。

执行以下命令创建开启 TLS 的异构集群：

{{< copyable "shell-regular" >}}

```shell
kubectl create -f cluster.yaml -n ${namespace}
```

详细的异构 TLS 集群配置示例，请参阅 ['heterogeneous-tls'](https://github.com/pingcap/tidb-operator/tree/master/examples/heterogeneous-tls)。
