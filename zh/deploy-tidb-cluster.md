---
title: 在 Kubernetes 上部署 TiDB 集群
summary: 了解如何在 Kubernetes 环境中部署 TiDB 集群。
---

# 在 Kubernetes 上部署 TiDB 集群

本文介绍如何在 Kubernetes 环境中部署 TiDB 集群。

## 前提条件

- TiDB Operator [部署](deploy-tidb-operator.md)完成。

## 配置 TiDB 集群

TiDB 集群包含以下组件，每个组件由对应的 [Custom Resource Definition (CRD)](https://kubernetes.io/zh-cn/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions) 进行管理：

| 组件名称 | CRD 名称 |
|----------|-----------|
| [PD](https://docs.pingcap.com/zh/tidb/stable/tidb-scheduling/) | `PDGroup` |
| [TiKV](https://docs.pingcap.com/zh/tidb/stable/tidb-storage/) | `TiKVGroup` |
| [TiDB](https://docs.pingcap.com/zh/tidb/stable/tidb-computing/) | `TiDBGroup` |
| [TiProxy](https://docs.pingcap.com/zh/tidb/stable/tiproxy-overview/)（可选） | `TiProxyGroup` |
| [TiFlash](https://docs.pingcap.com/zh/tidb/stable/tiflash-overview/)（可选） | `TiFlashGroup` |
| [TiCDC](https://docs.pingcap.com/zh/tidb/stable/ticdc-overview/)（可选） | `TiCDCGroup` |

在下面的步骤中，你将通过 `Cluster` CRD 定义一个 TiDB 集群，然后在各组件的 CRD 配置中，通过指定以下 `cluster.name` 字段将其关联到该集群。

```yaml
spec:
  cluster:
    name: <cluster>
```

在部署 TiDB 集群之前，你需要为每个组件准备对应的 YAML 配置文件，以下是部分配置示例：

- PD 组件：[`pd.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/01-pd.yaml)
- TiKV 组件：[`tikv.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/02-tikv.yaml)
- TiDB 组件：[`tidb.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/03-tidb.yaml)
- TiFlash 组件：[`tiflash.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/04-tiflash.yaml)
- TiCDC 组件：[`ticdc.yaml`](https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/v2.0.0-alpha.6/examples/basic/05-ticdc.yaml)

### 设置组件版本

通过 `version` 字段指定组件版本：

```yaml
spec:
  template:
    spec:
      version: v8.1.0
```

如需使用非官方镜像，可通过 `image` 字段指定：

```yaml
spec:
  template:
    spec:
      version: v8.1.0
      image: gcr.io/xxx/tidb
```

如果要使用的版本不符合[语义化版本 (Semantic Version)](https://semver.org/) 格式，也可通过 `image` 字段指定：

```yaml
spec:
  template:
    spec:
      version: v8.1.0
      image: gcr.io/xxx/tidb:dev
```

> **注意：**
>
> TiDB Operator 会根据 `version` 字段判断组件之间的升级依赖关系。为避免升级失败，请确保指定的镜像版本准确无误。

### 配置资源

通过 `spec.resources` 字段配置组件所需的资源：

```yaml
spec:
  resources:
    cpu: "4"
    memory: 8Gi
```

> **注意：**
>
> - 默认情况下，配置的资源会同时应用于 [Requests 和 Limits](https://kubernetes.io/zh-cn/docs/concepts/configuration/manage-resources-containers/#requests-and-limits)，即 Requests 与 Limits 使用相同的资源配置。
> - 如需分别设置 Requests 和 Limits，请使用 [Overlay](overlay.md) 进行配置。

### 配置组件参数

通过 `spec.config` 字段设置组件的 `config.toml` 参数：

```yaml
spec:
  config: |
    [log]
    level = warn
```

> **注意：**
>
> 暂不支持校验 `config.toml` 配置的合法性，请确保配置内容正确。

### 配置存储卷

通过 `spec.volumes` 为组件配置挂载的存储卷 (volume)：

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

部分组件支持使用 `type` 字段指定特定用途的 volume。此时，`config.toml` 中的相关配置也会自动更新，例如：

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

此外，volume 支持指定 [StorageClass](https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/) 和 [VolumeAttributeClass](https://kubernetes.io/zh-cn/docs/concepts/storage/volume-attributes-classes/)。详情参考[存储卷配置](volume-configuration.md)。

### 配置调度策略

通过 `spec.schedulePolicies` 字段将组件均匀分布到不同节点：

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

如需为拓扑设置权重，可设置 `weight` 字段：

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

你还可以使用 [Overlay](overlay.md) 配置以下调度选项：

- [NodeSelector](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector)
- [Toleration](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Affinity](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)
- [TopologySpreadConstraints](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/topology-spread-constraints/)

## 部署 TiDB 集群

在准备好 TiDB 集群各组件的 YAML 配置文件后，按照以下步骤部署 TiDB 集群：

1. 创建命名空间 Namespace：

    > **注意：**
    >
    > 暂不支持跨 Namespace 引用 `Cluster`。请确保所有组件部署在同一个 Kubernetes Namespace 中。

    ```shell
    kubectl create namespace db
    ```

2. 部署 TiDB 集群：

    方法一：各个组件分别部署（以部署一个包含 PD、TiKV 和 TiDB 组件的 TiDB 集群为例）

    <SimpleTab>

    <div label="Cluster">

    `Cluster` CRD 的示例配置如下：

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: basic
      namespace: db
    ```

    创建 `Cluster`：

    ```shell
    kubectl apply -f cluster.yaml --server-side
    ```

    </div>

    <div label="PD">

    PD 组件的示例配置如下：

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

    创建 PD 组件：

    ```shell
    kubectl apply -f pd.yaml --server-side
    ```

    </div>

    <div label="TiKV">

    TiKV 组件的示例配置如下：

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

    创建 TiKV 组件：

    ```shell
    kubectl apply -f tikv.yaml --server-side
    ```

    </div>

    <div label="TiDB">

    TiDB 组件的示例配置如下：

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

    创建 TiDB 组件：

    ```shell
    kubectl apply -f tidb.yaml --server-side
    ```

    </div>

    </SimpleTab>

    方法二：将以上各组件的 YAML 文件保存在本地目录中，然后使用以下命令一次性部署 TiDB 集群

    ```shell
    kubectl apply -f ./<directory> --server-side
    ```

3. 查看 TiDB 集群各组件的运行状态：

    ```shell
    kubectl get cluster -n db
    kubectl get group -n db
    ```
