---
title: 存储卷配置
summary: 介绍如何为组件配置存储卷，以及如何修改已创建的存储卷。
---

# 存储卷配置

本文档将详细介绍如何在 TiDB Operator 中为不同组件配置存储卷。

## 基本概念

在 TiDB Operator 中，存储卷（Volume）是为各组件提供持久化存储的资源。PD、TiKV、TiFlash 等组件都需要配置适当的存储卷来存储数据。存储卷配置遵循以下结构：

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

其中：

- `name`：卷的名称，在同一组件内必须唯一
- `mounts`：定义卷的挂载信息，包括：
    - `type`：挂载类型，不同组件支持不同的类型
    - `mountPath`：可选，指定挂载路径，如不指定则使用默认路径
    - `subPath`：可选，指定卷的子路径
- `storage`：存储容量，如 "100Gi"
- `storageClassName`：可选，指定 Kubernetes 存储类
- `volumeAttributesClassName`：可选，指定卷属性类，用于修改卷的属性（Kubernetes 1.29+ 特性）

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
kind: TidbGroup
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

与配置存储卷时类似，通过修改组件 Group CR 中的 `volumes.storage` 字段，TiDB Operator 会更新对应的 PVC 来调整卷大小。

> **注意：**
>
> - 只有使用的 StorageClass 的 `allowVolumeExpansion` 为 `true` 时，才能修改存储大小。
> - 只支持扩容，不支持缩容。

### 修改存储卷属性

对于底层使用云厂商存储的 TiDB 集群，TiDB Operator 支持两种方式修改存储卷的属性（例如：修改 IOPS 和吞吐量）：

- Kubernetes 原生方式（推荐）
- 云厂商 API 方式

#### Kubernetes 原生方式

Kubernetes 原生方式是指通过 [Volume Attributes Classes](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/) 修改卷的属性。

此功能是 Kubernetes 1.29 中的 Alpha 特性，默认是禁用的，需要参考官方文档开启；同时需要在 TiDB 集群中启用 VolumeAttributeClass 功能开关：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  featureGates:
    - name: VolumeAttributeClass
```

启用后，用户可以通过创建一个 VolumeAttributesClass：

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

然后通过修改组件 Group CR 中的 `volumes.volumeAttributesClassName` 字段来使用该 VolumeAttributesClass，从而实现修改卷的属性：

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

### 云厂商 API 方式

当未启用 `VolumeAttributesClass` 功能开关时，TiDB Operator 会使用云厂商的 API 直接修改底层存储卷。目前支持以下云厂商存储卷的修改：

1. **AWS EBS**：使用 AWS EC2 API 修改 EBS 卷的大小、IOPS 和吞吐量
2. **Azure Disk**：使用 Azure API 修改 Managed Disk 的大小、IOPS 和吞吐量

> **注意：**
>
> - 使用云厂商 API 方式时，需要确保 TiDB Operator 有足够的云厂商相关权限。

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

用户可以创建一个更高 IOPS 和吞吐量的 StorageClass：

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

然后修改组件 Group CR 中的 `.spec.template.spec.volumes.storageClassName` 字段为 `gp3-4000-400`，TiDB Operator 会自动调用云厂商 API 修改底层存储卷的属性。

由于 PVC 的 StorageClass 不能直接修改，TiDB Operator 会在 PVC 上添加以下注解来跟踪修改状态：

- `spec.tidb.pingcap.com/revision`：规格修改版本号
- `spec.tidb.pingcap.com/storage-class`：期望的存储类
- `spec.tidb.pingcap.com/storage-size`：期望的存储大小
- `status.tidb.pingcap.com/revision`：当前的修改版本号
- `status.tidb.pingcap.com/storage-class`：当前的存储类
- `status.tidb.pingcap.com/storage-size`：当前的存储大小

## 常见问题

**Q: 如何为不同的 TiKV 实例配置不同的存储大小？**

A: 目前在同一个 TiKVGroup 中的所有实例会使用相同的存储配置。如果需要不同的配置，可以创建多个 TiKVGroup。

**Q: 为什么我的存储卷修改没有立即生效？**

A: 某些云厂商对卷修改有冷却期限制（如 AWS EBS 为 6 小时）。此外，文件系统扩容可能需要一些时间才能完成。
