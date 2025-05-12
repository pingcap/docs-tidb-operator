---
title: 部署 TiDB 集群
summary: 了解如何在 Kubernetes 中部署 TiDB 集群。
category: how-to
aliases: ['/docs-cn/tidb-in-kubernetes/dev/deploy-tidb-cluster/']
---

<!-- markdownlint-disable MD007 -->

# 在 Kubernetes 中部署 TiDB 集群

本文档介绍了如何部署 TiDB 集群。

## 部署

整个 TiDB 集群包括如下组件

- PD
- TiKV
- TiDB
- TiFlash(optional)
- TiCDC(optional)

每个组件对应一个直接面向用户的 CRD

- PDGroup
- TiKVGroup
- TiDBGroup
- TiFlashGroup
- TiCDCGroup

除此之外，还有标志一个集群的 CRD `Cluster`

所有组件都通过如下字段去引用一个集群。

{{< copyable "" >}}

```yaml
spec:
  cluster:
    name: <cluster>
```

> **注意：**
>
> 暂不支持跨 Namespace 引用 Cluster，所有组件都需要部署在同一个 Kubernetes Namespace 中。
>

用户可以通过如下命令创建一个包含 PD, TiKV, TiDB 的最简 TiDB 集群。

<SimpleTab>

<div label="Cluster">

创建 Cluster

{{< copyable "" >}}

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: Cluster
metadata:
  name: basic
  namespace: db
```

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f cluster.yaml --server-side
```

</div>

<div label="PD">

创建 PD

{{< copyable "" >}}

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
  namespace: db
spec:
  cluster:
    name: basic
  replicas: 1
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

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f pd.yaml --server-side
```

</div>

<div label="TiKV">

创建 TiKV

{{< copyable "" >}}

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

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f tikv.yaml --server-side
```

</div>

<div label="TiDB">

创建 TiDB

{{< copyable "" >}}

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

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f tidb.yaml --server-side
```

</div>

</SimpleTab>

也可以将所有 yaml 文件保存到本地文件夹下，并用如下命令创建集群

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f ./cluster --server-side
```

## 版本

所有组件均可以通过如下字段配置所使用的版本

{{< copyable "" >}}

```yaml
spec:
  template:
    spec:
      version: v8.1.0
```

如果使用非官方镜像，可以使用 `image` 字段指定镜像

{{< copyable "" >}}

```yaml
spec:
  template:
    spec:
      version: v8.1.0
      image: gcr.io/xxx/tidb
```

也可以使用 `image` 字段指定非 [Semantic Version](https://semver.org/) 格式的版本

{{< copyable "" >}}

```yaml
spec:
  template:
    spec:
      version: v8.1.0
      image: gcr.io/xxx/tidb:dev
```

> **注意：**
>
> version 被用于约束组件间的升级依赖，建议始终使用镜像的真实版本
>

## 资源

所有组件均可以通过配置如下字段来设置所需的资源

{{< copyable "" >}}

```yaml
spec:
  resources:
    cpu: "4"
    memory: 8Gi
```

默认情况下，组件所声明的资源会同时应用于 [Requests 和 Limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#requests-and-limits), 即 Requests 和 Limits 会始终相等。

如果期望使用不同的 Requests 和 Limits, 可以参考 [如何 Overlay Pod 的配置](overlay.md) 进行更灵活的配置。

## 配置

所有组件均可以通过配置如下字段来设置组件所使用的 `config.toml`。

{{< copyable "" >}}

```yaml
spec:
  config: |
    [log]
    level = warn
```

> **注意：**
>
> 暂不支持验证 `config.toml` 的正确性
>

## 存储

所有组件均支持通过如下字段配置挂载的 volume

{{< copyable "" >}}

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

部分组件可以通过 `type` 指定具有特定用途的 volume，此时 `config.toml` 内的配置也会被同步修改。

{{< copyable "" >}}

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
        # data is for tikv's data dir
        - type: data
        storage: 100Gi
```

另外，volume 也支持指定 [StorageClass](https://kubernetes.io/docs/concepts/storage/storage-classes/) 和 [VolumeAttributeClass](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/), 详情可以参考 [如何配置组件的 Volume](configure-volume.md)

## 调度

所有组件都支持通过如下字段令节点均匀分布

{{< copyable "" >}}

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

也支持设置 `weight`

{{< copyable "" >}}

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

另外，也可以通过 [Overlay](overlay.md) 的方式设置 [NodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector), [Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/), [Affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) 和 [TopologySpreadConstraints](https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/)
