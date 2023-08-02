---
title: Restore a TiDB Cluster across multiple Kubernetes from EBS Volume Snapshots
summary: Learn how to restore a TiDB cluster across multiple Kubernetes from EBS Volume Snapshots.
aliases: ['/docs/tidb-in-kubernetes/dev/restore-by-ebs-snapshot-across-multiple-kubernetes/']
---

# Restore a TiDB Cluster across multiple Kubernetes from EBS Volume Snapshots

This document describes how to restore backup data in AWS EBS snapshots to a TiDB cluster across multiple Kubernetes.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in BR Federation Manager and TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Limitations

- Snapshot restore is applicable to TiDB Operator v1.5.0 or above, and TiDB v6.5.3 or above.
- Snapshot restore only supports restoring to a cluster with the same number of TiKV nodes and volumes configuration. That is, the number of TiKV nodes and volume configurations of TiKV nodes are identical between the restore cluster and backup cluster.
- Snapshot restore is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.
- Snapshot restore creates volumes with the default configuration (3000IOPS/125 MB) of GP3. To perform restore using other configurations, you can specify the volume type or configuration, such as `--volume-type=gp3`, `--volume-iops=7000`, or `--volume-throughput=400`.

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

### Complete the volume backup

To restore a TiDB cluster across multiple Kubernetes from EBS snapshots, you should have a completed `VolumeBackup`. For steps of performing snapshot backup, refer to [Back Up a TiDB Cluster across multiple Kubernetes Using EBS Volume Snapshots](backup-by-ebs-snapshot-across-multiple-kubernetes.md).

### Prepare the restore clusters

Deploy a TiDB cluster across multiple Kubernetes to which you want to restore data. See [Deploy a TiDB Cluster across Multiple Kubernetes Clusters](deploy-tidb-cluster-across-multiple-kubernetes.md). **Note, You need add the `recoveryMode: true` field to spec of `TidbCluster`**.

## Restore process

### Step 1. Set up the environment for EBS volume snapshot restore in every data plane

**You must execute the steps below in every data plane**.

1. Download the file [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) to the restore server.

2. Supposed that you deploy the TiDB cluster in `${namespace}`, create the RBAC-related resources required for the restore in this namespace by running the following command.

   {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n ${namespace}
    ```

3. Grant permissions to access remote storage.

   To restore data from EBS snapshots, you need to grant permissions to remote storage. Three ways are available. See [AWS account authorization](grant-permissions-to-remote-storage.md#aws-account-permissions).

### Step 2. Restore backup data to the TiDB cluster

**You must execute the steps below in the control plane**. Based on the authorization method you selected in the previous step to grant remote storage access, you can restore data to TiDB using any of the following methods accordingly:

+ Method 1: If you grant permissions by accessKey and secretKey, you can create the `VolumeRestore` CR as follows:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-fed.yaml
    ```

    The `restore-fed.yaml` file has the following content:

    {{< copyable "shell-regular" >}}

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
      - ...
      template:
        br:
          sendCredToTikv: true
        toolImage: ${br-image}
    ```

+ Method 2: If you grant permissions by associating Pod with IAM, you can create the `VolumeRestore` CR as follows:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-fed.yaml
    ```

    The `restore-fed.yaml` file has the following content:

    {{< copyable "shell-regular" >}}

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
      - ...
      template:
        br:
          sendCredToTikv: false
        toolImage: ${br-image}
    ```

+ Method 3: If you grant permissions by associating ServiceAccount with IAM, you can create the `VolumeRestore` CR as follows:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-fed.yaml
    ```

    The `restore-fed.yaml` file has the following content:

    {{< copyable "shell-regular" >}}

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
      - ...
      template:
        br:
          sendCredToTikv: false
        toolImage: ${br-image}
        serviceAccount: tidb-backup-manager
    ```

After creating the `VolumeRestore` CR, you can check the restore status using the following command:

{{< copyable "shell-regular" >}}

```shell
kubectl get vrt -n ${namespace} -o wide
```
