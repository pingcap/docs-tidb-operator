---
title: 给已有集群部署异构集群
summary: 介绍如何给已有集群部署一个异构集群,集群内的资源可以差异化部署，适配物理环境或者资源需求。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/deploy-heterogeneous-tidb-cluster/']
---

## 前置条件

* 已经存在一个 TiDB 集群,可以参考 [在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)进行部署。

## 部署异构集群

### 创建一个异构集群

{{< copyable "shell-regular" >}}

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: ${cluster_name}
spec:
  configUpdateStrategy: RollingUpdate
  version: v4.0.6
  timezone: UTC
  pvReclaimPolicy: Delete
  discovery: {}
  cluster:
    name: ${origin_cluster_name}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    # if storageClassName is not set, the default Storage Class of the Kubernetes cluster will be used
    # storageClassName: local-storage
    requests:
      storage: "1Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: {}
  tiflash:
    baseImage: pingcap/tiflash
    version: v4.0.6
    maxFailoverCount: 1
    replicas: 1
    storageClaims:
      - resources:
          requests:
            storage: 1Gi
        storageClassName: standard
```

将以上配置存为 cluster.yaml 文件，并替换 `<clusterName>` 为自己想命名的集群名字,`<origin_cluster_name>`替换为目标集群，执行以下命令创建集群：

{{< copyable "shell-regular" >}}

```shell
kubectl create cluster -f cluster.yaml
```

### 部署 监控

{{< copyable "shell-regular" >}}

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
    version: v4.0.4
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

将以上配置存为 tidbmonitor.yaml 文件，并替换 `<origin_cluster_name>` 为目标集群,`<heterogeneous_cluster_name>`替换为异构集群名称，执行以下命令创建集群：

{{< copyable "shell-regular" >}}

```shell
kubectl create cluster -f tidbmonitor.yaml
```

## 部署 TLS 异构集群

异构集群 TLS 需要重新颁发证书创建，需要保证目标集群和异构集群使用相同的CA (Certification Authority)。

参考:

- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)

我们在项目 Example 中提供了 ['heterogeneous-tls'](https://github.com/pingcap/tidb-operator/tree/master/examples/heterogeneous-tls) 示例
