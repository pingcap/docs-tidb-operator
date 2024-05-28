---
title: Restore a TiDB Cluster across Multiple Kubernetes from EBS Volume Snapshots
summary: Learn how to restore a TiDB cluster across multiple Kubernetes from EBS Volume Snapshots.
---

# Restore a TiDB Cluster across Multiple Kubernetes from EBS Volume Snapshots

This document describes how to restore backup data in AWS EBS snapshots to a TiDB cluster across multiple Kubernetes clusters.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in [BR Federation](br-federation-architecture.md#br-federation-architecture-and-processes) and TiDB Operator. [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) (Backup & Restore) is a command-line tool for distributed backup and recovery of the TiDB cluster data. For the underlying implementation, BR restores the data.

> **Note**
>
> Before you restore data, make sure that you have [deployed BR Federation](deploy-br-federation.md).

## Limitations

- Snapshot restore is applicable to TiDB Operator v1.5.1 or later versions and TiDB v6.5.4 or later versions.
- You can use snapshot restore only to restore data to a cluster with the same number of TiKV nodes and volumes configuration. That is, the number of TiKV nodes and volume configurations of TiKV nodes are identical between the restore cluster and backup cluster.
- Snapshot restore is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.

## Prerequisites

Before restoring a TiDB cluster across multiple Kubernetes clusters from EBS volume snapshots, you need to complete the following preparations.

- Complete the volume backup

    For detailed steps, refer to [Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots](backup-by-ebs-snapshot-across-multiple-kubernetes.md).

- Prepare the restore cluster

    - Deploy a TiDB cluster across multiple Kubernetes clusters that you want to restore data to. For detailed steps, refer to [Deploy a TiDB Cluster across Multiple Kubernetes Clusters](deploy-tidb-cluster-across-multiple-kubernetes.md).
    - When deploying the TiDB cluster, add the `recoveryMode: true` field to the spec of `TidbCluster`.

> **Note:**
> 
> The EBS volume restored from snapshots might have high latency before it is initialized. This can impact the performance of a restored TiDB cluster. See details in [Create a volume from a snapshot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-creating-volume.html#ebs-create-volume-from-snapshot).
> 
> It is recommended that you configure `spec.template.warmup: sync` to initialize TiKV volumes automatically during the restoration process.

## Restore process

### Step 1. Set up the environment for EBS volume snapshot restore in every data plane

**You must execute the following steps in every data plane**.

1. Download the [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/v1.6.0/manifests/backup/backup-rbac.yaml) file to the restore server.

2. Create the RBAC-related resources required for the restore by running the following command. Note that the RBAC-related resources must be put in the same `${namespace}` as the TiDB cluster. 

    ```shell
    kubectl apply -f backup-rbac.yaml -n ${namespace}
    ```

3. Grant permissions to access remote storage.

    To restore data from EBS snapshots, you need to grant permissions to remote storage. Three ways are available. Refer to [AWS account authorization](grant-permissions-to-remote-storage.md#aws-account-permissions) for the three available methods.

### Step 2. Restore data to the TiDB cluster

**You must execute the following steps in the control plane**.

Depending on the authorization method you choose in the previous step for granting remote storage access, you can restore data to TiDB using any of the following methods accordingly:

> **Note:**
>
> Snapshot restore creates volumes with the default configuration (3000 IOPS/125 MB/s) of GP3. To perform restore using other configurations, you can specify the volume type or configuration, such as `--volume-type=gp3`, `--volume-iops=7000`, or `--volume-throughput=400`, and they are shown in the following examples.

<SimpleTab>
<div label="AK/SK">

If you grant permissions by accessKey and secretKey, you can create the `VolumeRestore` CR as follows:

```shell
kubectl apply -f restore-fed.yaml
```

The `restore-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeRestore
metadata:
  name: ${restore-name}
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
    backup:
      s3:
        provider: aws
        secretName: s3-secret
        region: ${region-name}
        bucket: ${bucket-name}
        prefix: ${backup-path1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
    backup:
      s3:
        provider: aws
        secretName: s3-secret
        region: ${region-name}
        bucket: ${bucket-name}
        prefix: ${backup-path2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: true
      options:
      - --volume-type=gp3
      - --volume-iops=7000
      - --volume-throughput=400
    toolImage: ${br-image}
    warmup: sync
    warmupImage: ${wamrup-image}
```

</div>

<div label="IAM role with Pod">

If you grant permissions by associating Pod with IAM, you can create the `VolumeRestore` CR as follows:

```shell
kubectl apply -f restore-fed.yaml
```

The `restore-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeRestore
metadata:
  name: ${restore-name}
  annotations:
    iam.amazonaws.com/role: arn:aws:iam::123456789012:role/role-name
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
    backup:
      s3:
        provider: aws
        region: ${region-name}
        bucket: ${bucket-name}
        prefix: ${backup-path1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
    backup:
      s3:
        provider: aws
        region: ${region-name}
        bucket: ${bucket-name}
        prefix: ${backup-path2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: false
      options:
      - --volume-type=gp3
      - --volume-iops=7000
      - --volume-throughput=400
    toolImage: ${br-image}
    warmup: sync
    warmupImage: ${wamrup-image}
```

</div>

<div label="IAM role with ServiceAccount">

If you grant permissions by associating ServiceAccount with IAM, you can create the `VolumeRestore` CR as follows:

```shell
kubectl apply -f restore-fed.yaml
```

The `restore-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeRestore
metadata:
  name: ${restore-name}
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
    backup:
      s3:
        provider: aws
        region: ${region-name}
        bucket: ${bucket-name}
        prefix: ${backup-path1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
    backup:
      s3:
        provider: aws
        region: ${region-name}
        bucket: ${bucket-name}
        prefix: ${backup-path2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: false
      options:
      - --volume-type=gp3
      - --volume-iops=7000
      - --volume-throughput=400
    toolImage: ${br-image}
    serviceAccount: tidb-backup-manager
    warmup: sync
    warmupImage: ${warmup-image}
```

</div>
</SimpleTab>

### Step 3. View the restore status

After creating the `VolumeRestore` CR, the restore process automatically start.

To check the restore status, use the following command:

```shell
kubectl get vrt -n ${namespace} -o wide
```
