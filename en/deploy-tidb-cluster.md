---
title: Deploy a TiDB Cluster on Kubernetes
summary: Learn how to deploy a TiDB cluster on Kubernetes.
---

# Deploy a TiDB Cluster on Kubernetes

This document describes how to deploy a TiDB cluster on Kubernetes.

## Prerequisites

- TiDB Operator is [deployed](deploy-tidb-operator.md).

## Configure the TiDB cluster

A TiDB cluster consists of the following components. Each component is managed by a corresponding [Custom Resource Definition (CRD)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions):

| Component | CRD |
|----------|-----------|
| [PD](https://docs.pingcap.com/tidb/stable/tidb-scheduling/) | `PDGroup` |
| [TiKV](https://docs.pingcap.com/tidb/stable/tidb-storage/) | `TiKVGroup` |
| [TiDB](https://docs.pingcap.com/tidb/stable/tidb-computing/) | `TiDBGroup` |
| [TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy-overview/) (optional) | `TiProxyGroup` |
| [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash-overview/) (optional) | `TiFlashGroup` |
| [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview/) (optional) | `TiCDCGroup` |

In the following steps, you will define a TiDB cluster using the `Cluster` CRD. Then, in each component CRD, specify the `cluster.name` field to associate the component with the cluster.

```yaml
spec:
  cluster:
    name: <cluster>
```

Before deploying the cluster, prepare a YAML file for each component. The following lists some example configurations:

- PD: [`pd.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/01-pd.yaml)
- TiKV: [`tikv.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/02-tikv.yaml)
- TiDB: [`tidb.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/03-tidb.yaml)
- TiFlash: [`tiflash.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/04-tiflash.yaml)
- TiCDC: [`ticdc.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/05-ticdc.yaml)

### Configure component version

Use the `version` field to specify the component version:

```yaml
spec:
  template:
    spec:
      version: v8.1.0
```

To use a custom image, set the `image` field:

```yaml
spec:
  template:
    spec:
      version: v8.1.0
      image: gcr.io/xxx/tidb
```

If the version does not follow [semantic versioning](https://semver.org/), you can specify it using the `image` field:

```yaml
spec:
  template:
    spec:
      version: v8.1.0
      image: gcr.io/xxx/tidb:dev
```

> **Note:**
>
> TiDB Operator determines upgrade dependencies between components based on the `version` field. To avoid upgrade failures, ensure the image version is correct.

### Configure resources

Use the `spec.resources` field to define the CPU and memory resources for a component:

```yaml
spec:
  resources:
    cpu: "4"
    memory: 8Gi
```

By default, the same values apply to both [requests and limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#requests-and-limits).

To set different values for requests and limits, use the [Overlay](overlay.md) feature.

### Configure component parameters

Use the `spec.config` field to define `config.toml` settings:

```yaml
spec:
  config: |
    [log]
    level = warn
```

> **Note:**
>
> Validation of `config.toml` content is not currently supported. Make sure your configuration is correct.

### Configure volumes

Use the `spec.volumes` field to define mounted volumes for a component:

```yaml
spec:
  template:
    spec:
      volumes:
      - name: test
        mounts:
        - mountPath: "/test"
        storage: 100Gi
```

Some components support a `type` field to specify a volume's purpose. Related fields in `config.toml` are updated automatically. For example:

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiKVGroup
...
spec:
  template:
    spec:
      volumes:
      - name: data
        mounts:
        # data is for TiKV's data dir
        - type: data
        storage: 100Gi
```

You can also specify a [StorageClass](https://kubernetes.io/docs/concepts/storage/storage-classes/) and [VolumeAttributeClass](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/). For details, see [Volume Configuration](volume-configuration.md).

### Configure scheduling policies

Use the `spec.schedulePolicies` field to distribute components evenly across nodes:

```yaml
spec:
  schedulePolicies:
  - type: EvenlySpread
    evenlySpread:
      topologies:
      - topology:
          topology.kubernetes.io/zone: us-west-2a
      - topology:
          topology.kubernetes.io/zone: us-west-2b
      - topology:
          topology.kubernetes.io/zone: us-west-2c
```

To assign weights to topologies, use the `weight` field:

```yaml
spec:
  schedulePolicies:
  - type: EvenlySpread
    evenlySpread:
      topologies:
      - weight: 2
        topology:
          topology.kubernetes.io/zone: us-west-2a
      - topology:
          topology.kubernetes.io/zone: us-west-2b
```

You can also configure the following scheduling options using the [Overlay](overlay.md) feature:

- [NodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector)
- [Toleration](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)
- [TopologySpreadConstraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)

## Deploy the TiDB cluster

After preparing the YAML files for each component, deploy the TiDB cluster by following these steps:

1. Create a namespace:

    > **Note:**
    >
    > Cross-namespace references for `Cluster` resources are not supported. Make sure to deploy all components in the same namespace.

    ```shell
    kubectl create namespace db
    ```

2. Deploy the TiDB cluster:

    Option 1: Deploy each component individually. The following example shows how to deploy a TiDB cluster with PD, TiKV, and TiDB.

    <SimpleTab>

    <div label="Cluster">

    The following is an example configuration for the `Cluster` CRD:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: basic
      namespace: db
    ```

    Create the `Cluster` CRD:

    ```shell
    kubectl apply -f cluster.yaml --server-side
    ```

    </div>

    <div label="PD">

    The following is an example configuration for the PD component:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: PDGroup
    metadata:
      name: pd
      namespace: db
    spec:
      cluster:
        name: basic
      replicas: 3
      template:
        metadata:
          annotations:
            author: pingcap
        spec:
          version: v8.1.0
          volumes:
          - name: data
            mounts:
            - type: data
            storage: 20Gi
    ```

    Create the PD component:

    ```shell
    kubectl apply -f pd.yaml --server-side
    ```

    </div>

    <div label="TiKV">

    The following is an example configuration for the TiKV component:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
      namespace: db
    spec:
      cluster:
        name: basic
      replicas: 3
      template:
        metadata:
          annotations:
            author: pingcap
        spec:
          version: v8.1.0
          volumes:
          - name: data
            mounts:
            - type: data
            storage: 100Gi
    ```

    Create the TiKV component:

    ```shell
    kubectl apply -f tikv.yaml --server-side
    ```

    </div>

    <div label="TiDB">

    The following is an example configuration for the TiDB component:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiDBGroup
    metadata:
      name: tidb
      namespace: db
    spec:
      cluster:
        name: basic
      replicas: 2
      service:
        type: ClusterIP
      template:
        metadata:
          annotations:
            author: pingcap
        spec:
          version: v8.1.0
    ```

    Create the TiDB component:

    ```shell
    kubectl apply -f tidb.yaml --server-side
    ```

    </div>

    </SimpleTab>

    Option 2: Deploy all components at once. You can save all component YAML files in a local directory and execute the following command:

    ```shell
    kubectl apply -f ./<directory> --server-side
    ```

3. Check the status of the TiDB cluster:

    ```shell
    kubectl get cluster -n db
    kubectl get group -n db
    ```
