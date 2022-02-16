---
title: Deploy a Heterogeneous Cluster for an Existing TiDB Cluster
summary: Learn how to deploy a heterogeneous cluster for an existing TiDB cluster.
---

# Deploy a Heterogeneous Cluster for an Existing TiDB Cluster

This document describes how to deploy a heterogeneous cluster for an existing TiDB cluster. A heterogeneous cluster consists of nodes with different configurations from the existing TiDB cluster.

## User scenarios

This document is applicable to scenarios in which you need to create differentiated instances for an existing TiDB cluster, such as the following:

- Create TiKV clusters with different configurations and different labels for hotspot scheduling.
- Create TiDB clusters with different configurations for OLTP and OLAP queries.

## Prerequisites

You already have a TiDB cluster. If not, [deploy a TiDB cluster in Kubernetes](deploy-on-general-kubernetes.md) first.

## Deploy a heterogeneous cluster

Depending on whether you need to enable Transport Layer Security (TLS) for a heterogeneous cluster, choose one of the following methods:

- Deploy a heterogeneous cluster
- Deploy a TLS-enabled heterogeneous cluster

<SimpleTab>
<div label="non-TLS">

### Deploy a heterogeneous cluster

To deploy a heterogeneous cluster, do the following:

1. Create a cluster configuration file for the heterogeneous cluster.

    For example, save the following configuration as the `cluster.yaml` file. Replace `${heterogeneous_cluster_name}` with the desired name of your heterogeneous cluster, and replace `${origin_cluster_name}` with the name of the existing cluster.

    > **Note**:
    >
    > Comparing with the the configuration file of a normal TiDB cluster, the only difference in the configuration file of a heterogeneous TiDB cluster is that you need to additionally specify the `spec.cluster.name` field as the name of an existing TiDB cluster. According to this field, TiDB Operator adds the heterogeneous cluster to the existing TiDB cluster.

    {{< copyable "" >}}

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${heterogeneous_cluster_name}
    spec:
      configUpdateStrategy: RollingUpdate
      version: v5.3.0
      timezone: UTC
      pvReclaimPolicy: Delete
      discovery: {}
      cluster:
        name: ${origin_cluster_name}
      tikv:
        baseImage: pingcap/tikv
        maxFailoverCount: 0
        replicas: 1
        # If storageClassName is not set, the default Storage Class of the Kubernetes cluster is used.
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

    For more configurations and field meanings of TiDB cluster, see the [TiDB cluster configuration document](configure-a-tidb-cluster.md).

2. In the configuration file of your heterogeneous cluster, modify the configurations of each node according to your need.

    For example, you can modify the number of `replicas` for each component in the `cluster.yaml` file, or remove components that are not needed.

3. Create the heterogeneous cluster by running the following command. You need to replace `cluster.yaml` with the configuration filename of your heterogeneous cluster.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create -f cluster.yaml -n ${namespace}
    ```

    If the output shows `tidbcluster.pingcap.com/${heterogeneous_cluster_name} created`, the execution is successful. Then, TiDB Operator will create the TiDB cluster with the configurations according to the cluster configuration file.

</div>

<div label="TLS">

### Deploy a TLS-enabled heterogeneous cluster

To enable TLS for a heterogeneous cluster, you need to explicitly declare the TLS configuration, issue the certificates using the same certification authority (CA) as the target cluster and create new secrets with the certificates.

If you want to issue the certificate using `cert-manager`, choose the same `Issuer` as that of the target cluster to create your `Certificate`.

For detailed procedures to create certificates for the heterogeneous cluster, refer to the following two documents:

- [Enable TLS between TiDB Components](enable-tls-between-components.md)
- [Enable TLS for the MySQL Client](enable-tls-for-mysql-client.md)

After creating certificates, take the following steps to deploy a TLS-enabled heterogeneous cluster.

1. Create a cluster configuration file for the heterogeneous cluster.

    For example, save the following configuration as the `cluster.yaml` file. Replace `${heterogeneous_cluster_name}` with the desired name of your heterogeneous cluster, and replace `${origin_cluster_name}` with the name of the existing cluster.

    > **Note**:
    >
    > Comparing with the the configuration file of a normal TiDB cluster, the only difference in the configuration file of a heterogeneous TiDB cluster is that you need to additionally specify the `spec.cluster.name` field as the name of an existing TiDB cluster. According to this field, TiDB Operator adds the heterogeneous cluster to the existing TiDB cluster.

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${heterogeneous_cluster_name}
    spec:
      tlsCluster:
        enabled: true
      configUpdateStrategy: RollingUpdate
      version: v5.3.0
      timezone: UTC
      pvReclaimPolicy: Delete
      discovery: {}
      cluster:
        name: ${origin_cluster_name}
      tikv:
        baseImage: pingcap/tikv
        maxFailoverCount: 0
        replicas: 1
        # If storageClassName is not set, the default Storage Class of the Kubernetes cluster is used.
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

    In the configuration file, `spec.tlsCluster.enabled`controls whether to enable TLS between the components and `spec.tidb.tlsClient.enabled`controls whether to enable TLS for the MySQL client.

    - For more configurations of a TLS-enabled heterogeneous cluster, see the ['heterogeneous-tls'](https://github.com/pingcap/tidb-operator/tree/master/examples/heterogeneous-tls) example.
    - For more configurations and field meanings of a TiDB cluster, see the [TiDB cluster configuration document](configure-a-tidb-cluster.md).

2. In the configuration file of your heterogeneous cluster, modify the configurations of each node according to your need.

    For example, you can modify the number of `replicas` for each component in the `cluster.yaml` file, or remove components that are not needed.

3. Create the TLS-enabled heterogeneous cluster by running the following command. You need to replace `cluster.yaml` with the configuration filename of the heterogeneous cluster.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create -f cluster.yaml -n ${namespace}
    ```

    If the output shows `tidbcluster.pingcap.com/${heterogeneous_cluster_name} created`, the execution is successful. Then, TiDB Operator will create the TiDB cluster with the configurations according to your cluster configuration file.

</div>
</SimpleTab>

### Deploy a cluster monitoring component

If you need to deploy a monitoring component for a heterogeneous cluster, take the following steps to add the heterogeneous cluster name to the TidbMonitor CR file of an existing TiDB cluster.

1. Edit the TidbMonitor Custom Resource (CR) of the existing TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tm ${cluster_name} -n ${namespace}
    ```

2. Replace `${heterogeneous_cluster_name}` with the desired name of your heterogeneous cluster, and replace `${origin_cluster_name}` with the name of the existing cluster. For example:

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
        version: v5.3.0
    reloader:
        baseImage: pingcap/tidb-monitor-reloader
        version: v1.0.1
    imagePullPolicy: IfNotPresent
    ```
