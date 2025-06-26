---
title: Storage Volume Configuration
summary: Learn how to configure storage volumes for TiDB cluster components and how to modify existing storage volumes.
---

# Storage Volume Configuration

This document describes how to configure storage volumes for TiDB cluster components in TiDB Operator and how to modify existing storage volumes.

## Overview

In TiDB Operator, storage volumes provide persistent storage for TiDB cluster components. Components such as PD, TiKV, and TiFlash require configured volumes to store data. The structure for configuring a volume is as follows:

```yaml
volumes:
- name: <volume-name>
  mounts:
  - type: <mount-type>
    mountPath: <mount-path>
    subPath: <sub-path>
  storage: <storage-size>
  storageClassName: <storage-class-name>
  volumeAttributesClassName: <volume-attributes-class-name>
```

Field descriptions:

- `name`: the name of the volume, which must be unique within the same component.
- `mounts`: defines the mount information for the volume, including:
    - `type`: specifies the mount type. Supported types vary by component.
    - `mountPath` (optional): specifies the mount path. If not specified, the default path is used.
    - `subPath` (optional): specifies the sub-path within the volume.
- `storage`: specifies the storage capacity, such as `100Gi`.
- `storageClassName` (optional): specifies the name of the Kubernetes storage class.
- `volumeAttributesClassName` (optional): specifies the volume attributes class for modifying volume attributes. This feature is supported in Kubernetes 1.29 and later versions.

## Component-specific volume configuration

### PD storage volume configuration

Supported mount types for PD:

- `data`: PD data directory. The default path is `/var/lib/pd`.

Example:

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

### TiKV storage volume configuration

Supported mount types for TiKV:

- `data`: TiKV data directory. The default path is `/var/lib/tikv`.

Example:

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

### TiDB storage volume configuration

Supported mount types for TiDB:

- `data`: TiDB data directory. The default path is `/var/lib/tidb`.
- `slowlog`: TiDB slow log directory. The default path is `/var/log/tidb`.

Example:

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

### TiFlash storage volume configuration

Supported mount types for TiFlash:

- `data`: TiFlash data directory. The default path is `/var/lib/tiflash`.

Example:

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

## Modify storage volumes

### Modify the storage size

By modifying the `volumes.storage` field in the component group CR, TiDB Operator automatically updates the corresponding PVC to adjust the storage size.

> **Note:**
>
> - You can only modify storage size when the `allowVolumeExpansion` setting of the StorageClass in use is set to `true`.
> - Only volume scale-out is supported. Scale-in is not supported.

### Change volume attributes

For TiDB clusters that use cloud provider storages, TiDB Operator supports the following two methods to modify storage volume attributes (such as IOPS and throughput):

- (Recommended) [Kubernetes native method](#method-1-kubernetes-native)
- [Cloud provider API](#method-2-cloud-provider-api)

#### Method 1: Kubernetes native

The Kubernetes native method uses the [Volume Attributes Classes](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/) feature to modify volume attributes.

**Prerequisites:**

- Kubernetes 1.29 or later versions.
- The [Volume Attributes Classes](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/) feature of Kubernetes is enabled.

To modify volume attributes using the Kubernetes native method, perform the following:

1. Enable the `VolumeAttributesClass` feature in the `TidbCluster` CR:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: basic
    spec:
      featureGates:
        - name: VolumeAttributesClass
    ```

2. Create a `VolumeAttributesClass` resource:

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

3. Modify volume attributes by modifying the `volumes.volumeAttributesClassName` field in the component group CR to use the `VolumeAttributesClass` created in step 2:

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

#### Method 2: cloud provider API

> **Note:**
>
> When using the cloud provider API method, you need to configure the corresponding cloud provider permissions for TiDB Operator.

When the `VolumeAttributesClass` feature is not enabled, TiDB Operator calls cloud provider APIs directly to modify storage volume attributes. Currently, modifications to the following cloud provider storage volumes are supported:

- **AWS EBS**: modify EBS volume size, IOPS, and throughput using the AWS EC2 API.
- **Azure Disk**: modify Managed Disk size, IOPS, and throughput using the Azure API.

Using AWS EBS as an example, assume that the current storage volume configuration is:

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

You can create a StorageClass with higher IOPS and throughput:

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

Then, modify the `.spec.template.spec.volumes.storageClassName` field in the component group CR to `gp3-4000-400`. TiDB Operator automatically calls cloud provider APIs to perform the modification.

Because the StorageClass of a PVC cannot be modified directly, TiDB Operator adds the following annotations to the PVC to track the update:

- `spec.tidb.pingcap.com/revision`: desired spec revision number.
- `spec.tidb.pingcap.com/storage-class`: desired storage class.
- `spec.tidb.pingcap.com/storage-size`: desired storage size.
- `status.tidb.pingcap.com/revision`: current spec revision number.
- `status.tidb.pingcap.com/storage-class`: current storage class.
- `status.tidb.pingcap.com/storage-size`: current storage size.

## FAQ

### How do I configure different storage sizes for different TiKV instances?

All instances in the same `TiKVGroup` share the same storage configuration. To configure different storage for different TiKV instances, you can create multiple `TiKVGroups` resources.

### Why does the volume modification not take effect immediately?

Storage volume modifications might not take effect immediately for the following reasons:

- Some cloud providers have cooldown period restrictions for volume modifications. For example, AWS EBS has a 6-hour cooldown period.
- File system expansion might take some time to complete.
