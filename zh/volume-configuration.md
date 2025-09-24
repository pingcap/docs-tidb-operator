---
title: 存储卷配置
summary: 介绍如何为 TiDB 集群各组件配置存储卷，以及如何修改已创建的存储卷。
---

# 存储卷配置

本文档介绍如何在 TiDB Operator 中为 TiDB 集群的各组件配置存储卷，以及如何修改已创建的存储卷。

## 概述

在 TiDB Operator 中，存储卷 (Volume) 为 TiDB 集群中的各组件提供持久化存储。PD、TiKV 和 TiFlash 等组件都需要配置存储卷以保存其数据。存储卷配置的结构如下：

```yaml
volumes:
- name: <卷名称>
  mounts:
  - type: <挂载类型>
    mountPath: <挂载路径>
    subPath: <子路径>
  storage: <存储大小>
  storageClassName: <存储类名称>
  volumeAttributesClassName: <卷属性类名称>
```

参数说明：

- `name`：卷的名称，在同一组件内必须唯一。
- `mounts`：定义卷的挂载信息，包括：
    - `type`：指定挂载类型，不同组件支持的类型不同。
    - `mountPath`：（可选）指定挂载路径。如果未指定，将使用默认路径。
    - `subPath`：（可选）指定卷内子路径。
- `storage`：存储容量，例如 `100Gi`。
- `storageClassName`：（可选）指定 Kubernetes 存储类名称。
- `volumeAttributesClassName`：（可选）指定卷属性类，用于修改卷的属性。此功能仅 Kubernetes 1.29 及以上版本支持。

## 组件特定的存储卷配置

### PD 存储卷配置

PD 组件支持的挂载类型：

- `data`：PD 数据目录，默认路径为 `/var/lib/pd`

示例配置：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
spec:
  template:
    spec:
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 20Gi
```

### TiKV 存储卷配置

TiKV 组件支持的挂载类型：

- `data`：TiKV 数据目录，默认路径为 `/var/lib/tikv`

示例配置：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiKVGroup
metadata:
  name: tikv
spec:
  template:
    spec:
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 100Gi
```

### TiDB 存储卷配置

TiDB 组件支持的挂载类型：

- `data`：TiDB 数据目录，默认路径为 `/var/lib/tidb`
- `slowlog`：TiDB 慢日志目录，默认路径为 `/var/log/tidb`

示例配置：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: tidb
spec:
  template:
    spec:
      volumes:
      - name: slowlog
        mounts:
          - type: slowlog
        storage: 10Gi
```

### TiFlash 存储卷配置

TiFlash 组件支持的挂载类型：

- `data`：TiFlash 数据目录，默认路径为 `/var/lib/tiflash`

示例配置：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiFlashGroup
metadata:
  name: tiflash
spec:
  template:
    spec:
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 100Gi
```

## 修改存储卷

### 修改存储大小

通过修改组件 Group CR 中 `volumes.storage` 字段，TiDB Operator 会自动更新对应的 PVC 以调整存储大小。

> **注意：**
>
> - 只有当所使用的 StorageClass 的 `allowVolumeExpansion` 设置为 `true` 时，才能修改存储大小。
> - 只支持扩容，不支持缩容。

### 修改存储卷属性

对于底层使用云厂商存储的 TiDB 集群，TiDB Operator 支持以下两种方式修改存储卷的属性（例如 IOPS 和吞吐量）：

- （推荐）[Kubernetes 原生方式](#方式一kubernetes-原生方式)
- [云厂商 API 方式](#方式二云厂商-api)

#### 方式一：Kubernetes 原生方式

Kubernetes 原生方式是指通过 [Volume Attributes Classes](https://kubernetes.io/zh-cn/docs/concepts/storage/volume-attributes-classes/) 功能修改卷的属性。

**前提条件：**

- Kubernetes 1.29 及以上版本。
- 已开启 Kubernetes 的 [Volume Attributes Classes](https://kubernetes.io/zh-cn/docs/concepts/storage/volume-attributes-classes/) 功能。

使用 Kubernetes 原生方式修改卷属性的操作步骤如下：

1. 在 TiDB 集群中启用 `VolumeAttributesClass` 功能开关：

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: basic
    spec:
      featureGates:
        - name: VolumeAttributesClass
    ```

2. 创建 `VolumeAttributesClass` 资源：

    ```yaml
    apiVersion: storage.k8s.io/v1beta1
    kind: VolumeAttributesClass
    metadata:
      name: silver
    driverName: pd.csi.storage.gke.io
    parameters:
      provisioned-iops: "3000"
      provisioned-throughput: "50"
    ```

3. 通过修改组件 Group CR 中的 `volumes.volumeAttributesClassName` 字段来使用步骤 2 中创建的 `VolumeAttributesClass`，从而修改卷的属性：

    ```yaml
    spec:
      template:
        spec:
          volumes:
          - name: data
            mounts:
            - type: data
            storage: 100Gi
            volumeAttributesClassName: silver
    ```

#### 方式二：云厂商 API

> **注意：**
>
> 使用云厂商 API 方式时，你需要为 TiDB Operator 配置相应的云厂商权限。

未启用 `VolumeAttributesClass` 功能时，TiDB Operator 会调用云厂商的 API 直接修改存储卷属性。目前支持对以下云厂商存储卷的修改：

- **AWS EBS**：使用 AWS EC2 API 修改 EBS 卷的大小、IOPS 和吞吐量。
- **Azure Disk**：使用 Azure API 修改 Managed Disk 的大小、IOPS 和吞吐量。

以 AWS EBS 为例，假设当前存储卷的配置为：

```yaml
spec:
  template:
    spec:
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 100Gi
        storageClassName: gp3-2000-100
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3-2000-100
parameters:
  csi.storage.k8s.io/fstype: ext4
  encrypted: "true"
  iops: "2000"
  throughput: "100"
  type: gp3
provisioner: ebs.csi.aws.com
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

你可以创建一个更高 IOPS 和吞吐量的 StorageClass：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3-4000-400
parameters:
  csi.storage.k8s.io/fstype: ext4
  encrypted: "true"
  iops: "4000"
  throughput: "400"
  type: gp3
provisioner: ebs.csi.aws.com
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

然后，将组件 Group CR 中的 `.spec.template.spec.volumes.storageClassName` 字段修改为 `gp3-4000-400`，TiDB Operator 会自动调用云厂商 API 执行修改。

由于 PVC 的 StorageClass 不能直接修改，TiDB Operator 会在 PVC 上添加以下注解来跟踪修改状态：

- `spec.tidb.pingcap.com/revision`：期望的修改版本号
- `spec.tidb.pingcap.com/storage-class`：期望的存储类
- `spec.tidb.pingcap.com/storage-size`：期望的存储大小
- `status.tidb.pingcap.com/revision`：当前的修改版本号
- `status.tidb.pingcap.com/storage-class`：当前的存储类
- `status.tidb.pingcap.com/storage-size`：当前的存储大小

## 常见问题

### 如何为不同的 TiKV 实例配置不同的存储大小？

同一个 TiKVGroup 中的所有实例使用相同的存储配置。如果你需要为不同的 TiKV 实例配置不同的存储，可以创建多个 TiKVGroup。

### 为什么存储卷修改没有立即生效？

存储卷修改未立即生效可能有以下原因：

- 部分云厂商对卷修改存在冷却期限制，例如 AWS EBS 有 6 小时冷却期。
- 文件系统扩容可能需要一些时间才能完成。
