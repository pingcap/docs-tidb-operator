---
title: Restore a TiDB Cluster across Multiple Kubernetes from EBS Volume Snapshots
summary: Learn how to restore a TiDB cluster across multiple Kubernetes from EBS Volume Snapshots.
---

# Restore a TiDB Cluster across Multiple Kubernetes from EBS Volume Snapshots

This document describes how to restore backup data in AWS EBS snapshots to a TiDB cluster across multiple Kubernetes.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in BR Federation Manager and TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Limitations

- Snapshot restore is applicable to TiDB Operator v1.5.0 or later versions and TiDB v6.5.3 or later versions.
- You can use snapshot restore only to restore data to a cluster with the same number of TiKV nodes and volumes configuration. That is, the number of TiKV nodes and volume configurations of TiKV nodes are identical between the restore cluster and backup cluster.
- Snapshot restore is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.
- Snapshot restore creates volumes with the default configuration (3000 IOPS/125 MB) of GP3. To perform restore using other configurations, you can specify the volume type or configuration, such as `--volume-type=gp3`, `--volume-iops=7000`, or `--volume-throughput=400`.

  ```yaml
  spec:
    template:
      br:
        sendCredToTikv: false
        options:
        - --volume-type=gp3
        - --volume-iops=7000
        - --volume-throughput=400
      serviceAccount: tidb-backup-manager
      toolImage: pingcap/br:v7.1.0
   ```

## Prerequisites

Before restoring a TiDB cluster across multiple Kubernetes from EBS volume snapshots, you need to complete the following preparations.

- Complete the volume backup

    For detailed steps, refer to [Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots](backup-by-ebs-snapshot-across-multiple-kubernetes.md).

- Prepare the restore cluster

    - Deploy a TiDB cluster across multiple Kubernetes that you want to restore data to. For detailed steps, refer to [Deploy a TiDB Cluster across Multiple Kubernetes Clusters](deploy-tidb-cluster-across-multiple-kubernetes.md).
    - When deploying the TiDB cluster, add the `recoveryMode: true` field to the spec of `TidbCluster`.

## Restore process

### Step 1. Set up the environment for EBS volume snapshot restore in every data plane

**You must execute the following steps in every data plane**.

1. Download the [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) file to the restore server.

2. Supposed that you deploy the TiDB cluster in `${namespace}`, create the RBAC-related resources required for the restore in this namespace by running the following command.

    ```shell
    kubectl apply -f backup-rbac.yaml -n ${namespace}
    ```

3. Grant permissions to access remote storage.

    To restore data from EBS snapshots, you need to grant permissions to remote storage. Three ways are available. Refer to [AWS account authorization](grant-permissions-to-remote-storage.md#aws-account-permissions) for the three available methods.

### Step 2. Restore data to the TiDB cluster

**You must execute the following steps in the control plane**.

Depending on the authorization method you choose in the previous step for granting remote storage access, you can restore data to TiDB using any of the following methods accordingly:

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
    toolImage: ${br-image}
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
    toolImage: ${br-image}
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
    toolImage: ${br-image}
    serviceAccount: tidb-backup-manager
```

</div>
</SimpleTab>

### Step 3. View the restore status

After creating the `VolumeRestore` CR, the restore process automatically start.

To check the restore status, use the following command:

```shell
kubectl get vrt -n ${namespace} -o wide
```