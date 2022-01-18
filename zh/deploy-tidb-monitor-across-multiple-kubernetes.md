---
title: 跨多个 Kubernetes 集群监控 TiDB 集群
summary: 介绍如何对跨多个 Kubernetes 集群的 TiDB 集群进行监控，并集成到常见 Prometheus 多集群监控体系中
---

# 跨多个 Kubernetes 集群监控 TiDB 集群

本文档介绍如何对跨多个 Kubernetes 集群的 TiDB 集群进行监控，以及如何与几种社区常见的 Prometheus 多集群监控方式进行集成，从而实现统一全局视图进行监控数据访问。

## Push 方式

### 部署架构图

本文档以 Thanos 为例，如果使用了其他兼容 Prometheus Remote API 的中心化存储方案（如 Cortex、M3DB、Grafana Cloud 等），只需对 Thanos 相关组件进行替换即可。

![push-thanos-receive.png](/media/push-thanos-receive.png)

### 前置条件

多个 Kubernetes 集群间的组件满足以下条件：

- 各 Kubernetes 集群上的 Prometheus(TidbMonitor) 组件有能力访问 Thanos Receiver 组件。
- Grafana 组件有能力访问 Thanos Query 组件。

### 部署 TiDB 集群监控

根据不同 TiDB 集群所在的 Kubernetes 集群设置以下环境变量，其中 `cluster_name` 为TiDB集群名称， `cluster_namespace` 为TiDB集群所在的命名空间， `kubernetes_cluster_name` 为自定义的 kubernetes 集群名称，在标识 Prometheus 的 `externallabels` 中使用， `storageclass_name` 设置为当前集群中的存储， `remote_write_url` 为 `thanos-receiver` （或其他兼容 Prometheus remote API）组件的 host ，关于 thanos 部署方案参考 [kube-thanos](https://github.com/thanos-io/kube-thanos) 以及 [Example](https://github.com/pingcap/tidb-operator/tree/master/examples/monitor-prom-remotewrite)。

{{< copyable "shell-regular" >}}

```sh
cluster_name="cluster1"
cluster_namespace="pingcap"
kubernetes_cluster_name="kind-cluster-1"
storageclass_name="local-storage"
remote_write_url="http://thanos-receiver:19291/api/v1/receive"
```

执行以下指令，创建 `TidbMonitor` ：

{{< copyable "shell-regular" >}}

```sh
cat << EOF | kubectl apply -n ${cluster_namespace} -f -
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: ${cluster_name}
spec:
  clusters:
  - name: ${cluster_name}
    namespace: ${cluster_namespace}
  externalLabels:
    #kubernetes indicates the k8s cluster name, you can change the label's name on your own, but you should notice that `cluster` label has been used by tidb already. For more information, please refer to issue https://github.com/pingcap/tidb-operator/issues/4219.
    kubernetes: ${kubernetes_cluster_name}
    #add other meta labels here
    #region: us-east-1
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v5.2.1
  persistent: true
  storage: 5Gi
  storageClassName: ${storageclass_name}
  prometheus:
    baseImage: prom/prometheus
    logLevel: info
    remoteWrite:
    - url: ${remote_write_url}
    retentionTime: 2h
    version: v2.27.1
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

## Pull 方式

<SimpleTab>
<div label="Thanos Query">

### 使用 Thanos Query

#### 部署架构图

为每个 prometheus(TidbMonitor) 组件部署 thanos sidecar，并使用 thanos-query 组件进行聚合查询，其中 thanos-store、 S3 等组件在不需要对监控数据做长期存储时可以选择不部署。

![pull-thanos-query.png](/media/pull-thanos-query.png)

#### 前置条件

需要配置 Kubernetes 的网络和 DNS，使得 Kubernetes 集群满足以下条件：

- Thanos Query 组件有能力访问各 Kubernetes 集群上的 Prometheus(TidbMonitor) 组件的 Pod IP。
- Thanos Query 组件有能力访问各 Kubernetes 集群上的 Prometheus(TidbMonitor) 组件的 Pod FQDN。

#### 部署 TiDB 集群监控

根据不同 TiDB 集群所在的 Kubernetes 集群设置以下环境变量，其中 `cluster_name`为TiDB集群名称， `cluster_namespace` 为TiDB集群所在的命名空间， `kubernetes_cluster_name` 为自定义的 kubernetes 集群名称，在标识 Prometheus 的 `externallabels` 中使用， `storageclass_name` 设置为当前集群中的存储，关于 thanos 部署方案参考 [kube-thanos](https://github.com/thanos-io/kube-thanos) 以及 [Example](https://github.com/pingcap/tidb-operator/tree/master/examples/monitor-with-thanos)。

{{< copyable "shell-regular" >}}

```sh
cluster_name="cluster1"
cluster_namespace="pingcap"
kubernetes_cluster_name="kind-cluster-1"
storageclass_name="local-storage"
```

执行以下指令，创建 `TidbMonitor`：

{{< copyable "shell-regular" >}}

```sh
cat << EOF | kubectl apply -n ${cluster1_namespace} -f -
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: ${cluster1_name}
spec:
  clusters:
  - name: ${cluster1_name}
    namespace: ${cluster1_namespace}
  externalLabels:
    #kubernetes indicates the k8s cluster name, you can change the label's name on your own, but you should notice that `cluster` label has been used by tidb already. For more information, please refer to issue https://github.com/pingcap/tidb-operator/issues/4219.
    kubernetes: ${kubernetes_cluster1_name}
    #add other meta labels here
    #region: us-east-1
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v5.2.1
  persistent: true
  storage: 20Gi
  storageClassName: ${storageclass_name}
  prometheus:
    baseImage: prom/prometheus
    logLevel: info
    version: v2.27.1
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  thanos:
    baseImage: quay.io/thanos/thanos
    version: v0.22.0
    #enable config below if long-term storage is needed.
    #objectStorageConfig:
    #  key: objectstorage.yaml
    #  name: thanos-objectstorage
  imagePullPolicy: IfNotPresent
```

</div>

<div label="Federation">

### 使用 Prometheus Federation

#### 部署架构图

使用 Federation Prometheus Server 作为数据统一存储与查询的入口，建议在数据规模较小的环境下使用。

![pull-prom-federation.png](/media/pull-prom-federation.png)

#### 前置条件

需要配置 Kubernetes 的网络和 DNS，使得 Kubernetes 集群满足以下条件：

- Federation Prometheus 组件有能力访问各 Kubernetes 集群上的 Prometheus(TidbMonitor) 组件的 Pod IP。
- Federation Prometheus 组件有能力访问各 Kubernetes 集群上的 Prometheus(TidbMonitor) 组件的 Pod FQDN。

#### 部署 TiDB 集群监控

根据不同 TiDB 集群所在的 Kubernetes 集群设置以下环境变量，其中 `cluster_name` 为TiDB集群名称， `cluster_namespace` 为TiDB集群所在的命名空间， `kubernetes_cluster_name` 为自定义的 kubernetes 集群名称，在标识 Prometheus 的 `externallabels` 中使用， `storageclass_name` 设置为当前集群中的存储。

{{< copyable "shell-regular" >}}

```sh
cluster_name="cluster1"
cluster_namespace="pingcap"
kubernetes_cluster_name="kind-cluster-1"
storageclass_name="local-storage"
```

执行以下指令，创建 `TidbMonitor` ：

{{< copyable "shell-regular" >}}

```sh
cat << EOF | kubectl apply -n ${cluster1_namespace} -f -
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: ${cluster1_name}
spec:
  clusters:
  - name: ${cluster1_name}
    namespace: ${cluster1_namespace}
  externalLabels:
    #kubernetes indicates the k8s cluster name, you can change the label's name on your own, but you should notice that `cluster` label has been used by tidb already. For more information, please refer to issue https://github.com/pingcap/tidb-operator/issues/4219.
    kubernetes: ${kubernetes_cluster1_name}
    #add other meta labels here
    #region: us-east-1
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v5.2.1
  persistent: true
  storage: 20Gi
  storageClassName: ${storageclass_name}
  prometheus:
    baseImage: prom/prometheus
    logLevel: info
    version: v2.27.1
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

### 配置 Federation Prometheus

关于 Federation 方案，参考[federation文档](https://prometheus.io/docs/prometheus/latest/federation/#hierarchical-federation)。部署完成后修改 Prometheus 采集配置，添加需要汇总的 Prometheus(TiDBMonitor) 的 host 信息。

```
scrape_configs:
  - job_name: 'federate'
    scrape_interval: 15s

    honor_labels: true
    metrics_path: '/federate'

    params:
      'match[]':
        - '{job="prometheus"}'
        - '{__name__=~"job:.*"}'

    static_configs:
      - targets:
        - 'source-prometheus-1:9090'
        - 'source-prometheus-2:9090'
        - 'source-prometheus-3:9090'
```

</div>
</SimpleTab>