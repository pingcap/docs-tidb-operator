---
title: 为已有 TiDB 集群部署异构集群
summary: 本文档介绍如何为已有的 TiDB 集群部署一个异构集群。
---

# 为已有 TiDB 集群部署异构集群

本文介绍如何为已有的 TiDB 集群部署一个异构集群。异构集群是与已有 TiDB 集群不同配置的节点构成的集群。

## 适用场景

适用于基于已有的 TiDB 集群需要创建一个差异化配置的实例节点的场景，例如：

- 创建不同配置不同 Label 的 TiKV 集群用于热点调度
- 创建不同配置的 TiDB 集群分别用于 OLTP 和 OLAP 查询

## 前置条件

已经存在一个 TiDB 集群。如果尚未部署 TiDB 集群，可以参考[在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)进行部署。

## 部署异构集群

依据你是否需要为异构集群开启 TLS （Transport Layer Security，安全传输层协议），请选择以下方案之一：

- 部署未开启 TLS 的异构集群
- 部署开启 TLS 的异构集群

<SimpleTab>
<div label="非 TLS">

要部署一个未开启 TLS 的异构集群，请进行以下操作：

1. 为异构集群新建一个集群配置文件。

    执行以下指令创建异构集群配置文件，其中 `origin_cluster_name` 为要加入的原集群名称，`heterogeneous_cluster_name` 为异构集群名称，为了后续在 TidbMonitor 的 Grafana 中同时查看原集群和异构集群的监控数据，请以原集群名称为前缀对异构集群进行命名。

    > **注意**:
    >
    > 相比于普通 TiDB 集群配置文件，异构集群配置文件的唯一区别是，你需要额外配置 `spec.cluster.name` 字段为已有的 TiDB 集群名。通过此字段，TiDB Operator 会将该异构集群加入到已有的 TiDB 集群。

    {{< copyable "" >}}

    ```bash
    origin_cluster_name=basic
    heterogeneous_cluster_name=basic-heterog
    cat > cluster.yaml << EOF
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${heterogeneous_cluster_name}
    spec:
      configUpdateStrategy: RollingUpdate
      version: v6.5.0
      timezone: UTC
      pvReclaimPolicy: Delete
      discovery: {}
      cluster:
        name: ${origin_cluster_name}
      tikv:
        baseImage: pingcap/tikv
        maxFailoverCount: 0
        replicas: 1
        # 如果不设置 storageClassName，TiDB Operator 将使用 Kubernetes 集群默认的 Storage Class
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
    EOF
    ```

    TiDB 集群更多的配置项和字段含义，请参考 [TiDB 集群配置文档](configure-a-tidb-cluster.md)。

2. 依据需要，修改异构集群配置文件中各节点的配置项。

    例如，你可以修改 `cluster.yaml` 文件中各组件的 `replicas` 数量，或者删除不需要的组件。

3. 执行以下命令创建异构集群。你需要将 `cluster.yaml` 替换为你的异构集群配置文件名。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create -f cluster.yaml -n ${namespace}
    ```

    如果输出提示 `tidbcluster.pingcap.com/${heterogeneous_cluster_name} created`，表示执行成功。TiDB Operator 会根据集群配置文件，创建对应配置的 TiDB 集群。

</div>

<div label="TLS">

开启异构集群 TLS 需要显示声明，需要创建新的 `Secret` 证书文件，使用和目标集群相同的 CA (Certification Authority) 颁发。如果使用 `cert-manager` 方式，需要使用和目标集群相同的 `Issuer` 来创建 `Certificate`。

为异构集群创建证书的详细步骤，可参考以下文档：

- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)

创建证书后，要部署一个开启 TLS 的异构集群，请进行以下操作：

1. 为异构集群新建一个集群配置文件。

    例如，将如下配置存为 `cluster.yaml` 文件，并替换 `${heterogeneous_cluster_name}` 为自己想命名的异构集群名字，`${origin_cluster_name}` 替换为想要加入的已有集群名称。

    > **注意**:
    >
    > 相比于普通 TiDB 集群配置文件，异构集群配置文件的唯一区别是，你需要额外配置 `spec.cluster.name` 字段为已有的 TiDB 集群名。通过此字段，TiDB Operator 会将该异构集群加入到已有的 TiDB 集群。

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${heterogeneous_cluster_name}
    spec:
      tlsCluster:
        enabled: true
      configUpdateStrategy: RollingUpdate
      version: v6.5.0
      timezone: UTC
      pvReclaimPolicy: Delete
      discovery: {}
      cluster:
        name: ${origin_cluster_name}
      tikv:
        baseImage: pingcap/tikv
        maxFailoverCount: 0
        replicas: 1
        # 如果不设置 storageClassName，TiDB Operator 将使用 Kubernetes 集群默认的 Storage Class
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

    其中，`spec.tlsCluster.enabled` 表示组件间是否开启 TLS，`spec.tidb.tlsClient.enabled` 表示 MySQL 客户端是否开启 TLS。

    - 详细的异构 TLS 集群配置示例，请参阅 [`heterogeneous-tls`](https://github.com/pingcap/tidb-operator/tree/master/examples/heterogeneous-tls)。

    - TiDB 集群更多的配置项和字段含义，请参考 [TiDB 集群配置文档](configure-a-tidb-cluster.md)。

2. 依据需要，修改异构集群配置文件中各节点的配置项。

    例如，你可以修改 `cluster.yaml` 文件中各组件的 `replicas` 数量或者删除不需要的组件。

3. 执行以下命令创建开启 TLS 的异构集群。你需要将 `cluster.yaml` 替换为你的异构集群配置文件名。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create -f cluster.yaml -n ${namespace}
    ```

    如果执行成功，输出会提示 `tidbcluster.pingcap.com/${heterogeneous_cluster_name} created`。TiDB Operator 会根据集群配置文件，创建对应配置的 TiDB 集群。

</div>
</SimpleTab>

## 部署集群监控

如果你需要为异构集群部署监控，请在已有 TiDB 集群的 TidbMonitor CR 文件增加异构集群名。具体操作如下：

1. 编辑已有 TiDB 集群的 TidbMonitor Custom Resource (CR)：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tm ${cluster_name} -n ${namespace}
    ```

2. 参考以下示例，替换 `${origin_cluster_name}` 为想要加入的集群名称，替换 `${heterogeneous_cluster_name}` 为异构集群名称：

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
        version: v2.27.1
    grafana:
        baseImage: grafana/grafana
        version: 7.5.11
    initializer:
        baseImage: pingcap/tidb-monitor-initializer
        version: v6.5.0
    reloader:
        baseImage: pingcap/tidb-monitor-reloader
        version: v1.0.1
    prometheusReloader:
        baseImage: quay.io/prometheus-operator/prometheus-config-reloader
        version: v0.49.0
    imagePullPolicy: IfNotPresent
    ```
