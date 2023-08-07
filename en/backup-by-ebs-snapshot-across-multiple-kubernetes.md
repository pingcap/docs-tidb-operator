---
title: Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots
summary: Learn how to back up TiDB cluster data across multiple Kubernetes to S3 based on EBS volume snapshots using BR Federation.
---

# Back Up a TiDB Cluster across Multiple Kubernetes Using EBS Volume Snapshots

This document describes how to back up the data of a TiDB cluster deployed across multiple AWS Kubernetes to AWS storage using EBS volume snapshots.

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in [BR Federation](volume-snapshot-backup-restore-across-multiple-kubernetes.md#architecture-of-br-federation) and TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to get the backup data of the TiDB cluster, and then send the data to the AWS storage. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Usage scenarios

If you have the following requirements when backing up TiDB cluster data, you can use TiDB Operator to back up the data using volume snapshots and metadata to Amazon S3:

- Minimize the impact of backup, such as keeping the impact on QPS and transaction latency less than 5%, and not utilizing cluster CPU and memory.
- Back up and restore data in a short period of time. For example, completing a backup within 1 hour and restore it within 2 hours.

If you have any other requirements, refer to [Backup and Restore Overview](backup-restore-overview.md) and select an appropriate backup method.

## Limitations

- Snapshot backup is applicable to TiDB Operator v1.5.0 or later versions and TiDB v6.5.3 or later versions.
- To use this backup method, the TiDB cluster must be deployed on AWS EC2 and use AWS EBS volumes.
- This backup method is currently not supported for TiFlash, TiCDC, DM, and TiDB Binlog nodes.

> **Note:**
>
> - After you upgrade the TiDB cluster from an earlier version to v6.5.0 or later, you might find the volume snapshot backup does not work. To address this issue, see [Backup failed after an upgrade of the TiDB cluster](backup-restore-faq.md#backup-failed-after-an-upgrade-of-the-tidb-cluster).
> - To perform volume snapshot restore, ensure that the TiKV configuration during restore is consistent with the configuration used during backup.
>     - To check consistency, download the `backupmeta` file from the backup file stored in Amazon S3, and check the `kubernetes.crd_tidb_cluster.spec` field.
>     - If this field is inconsistent, you can modify the TiKV configuration by referring to [Configure a TiDB Cluster on Kubernetes](configure-a-tidb-cluster.md).
> - If [Encryption at Rest](https://docs.pingcap.com/tidb/stable/encryption-at-rest) is enabled for TiKV KMS, ensure that the master key is enabled for AWS KMS during restore.

## Ad-hoc backup

You can either fully or incrementally back up snapshots based on AWS EBS volumes. The initial backup of a node is full backup, while subsequent backups are incremental backup.

Snapshot backup is defined in a customized `VolumeBackup` custom resource (CR) object. The BR Federation completes the backup task according to the specifications in this object.

### Step 1. Set up the environment for EBS volume snapshot backup in every data plane

**You must execute the following steps in every data plane**.

1. Download the [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) file to the backup server.

2. If you have deployed the TiDB cluster in `${namespace}`, create the RBAC-related resources required for the backup in this namespace by running the following command:

    ```shell
    kubectl apply -f backup-rbac.yaml -n ${namespace}
    ```

3. Grant permissions to access remote storage.

    To back up cluster data and save snapshot metadata to Amazon S3, you need to grant permissions to remote storage. Refer to [AWS account authorization](grant-permissions-to-remote-storage.md#aws-account-permissions) for the three available methods.

### Step 2. Back up data to S3 storage

**You must execute the following steps in the control plane**.

Depending on the authorization method you choose in the previous step for granting remote storage access, you can back up data to S3 storage using any of the following methods accordingly:

<SimpleTab>
<div label="AK/SK">

If you grant permissions by accessKey and secretKey, you can create the `VolumeBackup` CR as follows:

```shell
kubectl apply -f backup-fed.yaml
```

The `backup-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackup
metadata:
  name: ${backup-name}
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: true
    s3:
      provider: aws
      secretName: s3-secret
      region: ${region-name}
      bucket: ${bucket-name}
      prefix: ${backup-path}
    toolImage: ${br-image}
    cleanPolicy: Delete
```

</div>

<div label="IAM role with Pod">

If you grant permissions by associating Pod with IAM, you can create the `VolumeBackup` CR as follows:

```shell
kubectl apply -f backup-fed.yaml
```

The `backup-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackup
metadata:
  name: ${backup-name}
  annotations:
    iam.amazonaws.com/role: arn:aws:iam::123456789012:role/role-name
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: false
    s3:
      provider: aws
      region: ${region-name}
      bucket: ${bucket-name}
      prefix: ${backup-path}
    toolImage: ${br-image}
    cleanPolicy: Delete
```

</div>

<div label="IAM role with ServiceAccount">

If you grant permissions by associating ServiceAccount with IAM, you can create the `VolumeBackup` CR as follows:

```shell
kubectl apply -f backup-fed.yaml
```

The `backup-fed.yaml` file has the following content:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackup
metadata:
  name: ${backup-name}
spec:
  clusters:
  - k8sClusterName: ${k8s-name1}
    tcName: ${tc-name1}
    tcNamespace: ${tc-namespace1}
  - k8sClusterName: ${k8s-name2}
    tcName: ${tc-name2}
    tcNamespace: ${tc-namespace2}
  - ... # other clusters
  template:
    br:
      sendCredToTikv: false
    s3:
      provider: aws
      region: ${region-name}
      bucket: ${bucket-name}
      prefix: ${backup-path}
    toolImage: ${br-image}
    serviceAccount: tidb-backup-manager
    cleanPolicy: Delete
```

</div>
</SimpleTab>

> **Note:**
>
> The value of `spec.clusters.k8sClusterName` field in `VolumeBackup` CR must be the same as the **context name** of the kubeconfig used by the br-federation-manager.

### Step 3. View the backup status

After creating the `VolumeBackup` CR, the BR Federation automatically starts the backup process in each data plane.

To check the volume backup status, use the following command:

```shell
kubectl get vbk -n ${namespace} -o wide
```

Once the volume backup is complete, you can get the information of all the data planes in the `status.backups` field. This information can be used for volume restore.

To obtain the information, use the following command:

```shell
kubectl get vbk ${backup-name} -n ${namespace} -o yaml
```

The information is as follows:

```yaml
status:
  backups:
  - backupName: fed-{backup-name}-{k8s-name1}
    backupPath: s3://{bucket-name}/{backup-path}-{k8s-name1}
    commitTs: "ts1"
    k8sClusterName: {k8s-name1}
    tcName: {tc-name1}
    tcNamespace: {tc-namespace1}
  - backupName: fed-{backup-name}-{k8s-name2}
    backupPath: s3://{bucket-name}/{backup-path}-{k8s-name2}
    commitTs: "ts2"
    k8sClusterName: {k8s-name2}
    tcName: {tc-name2}
    tcNamespace: {tc-namespace2}
  - ... # other backups
```

### Delete the `VolumeBackup` CR

If you set `spec.template.cleanPolicy` to `Delete`, when you delete the `VolumeBackup` CR, the BR Federation will clean up the backup file and the volume snapshots on AWS.

To delete the `VolumeBackup` CR, run the following commands:

```shell
kubectl delete backup ${backup-name} -n ${namespace}
```

## Scheduled volume backup

To ensure regular backups of the TiDB cluster and prevent an excessive number of backup items, you can set a backup policy and retention policy.

This can be done by creating a `VolumeBackupSchedule` CR object that describes the scheduled snapshot backup. Each backup time point triggers a volume backup. The underlying implementation is the ad-hoc volume backup.

### Perform a scheduled volume backup

Create the `VolumeBackupSchedule` CR, and back up cluster data as described below:

```shell
kubectl apply -f volume-backup-scheduler.yaml
```

The content of `volume-backup-scheduler.yaml` is as follows:

```yaml
---
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackupSchedule
metadata:
  name: {scheduler-name}
  namespace: {namespace-name}
spec:
  #maxBackups: {number}
  #pause: {bool}
  maxReservedTime: {duration}
  schedule: {cron-expression}
  backupTemplate:
    clusters:
      - k8sClusterName: {k8s-name1}
        tcName: {tc-name1}
        tcNamespace: {tc-namespace1}
        backup:
      - k8sClusterName: {k8s-name2}
        tcName: {tc-name2}
        tcNamespace: {tc-namespace2}
      - ... # other clusters
    template:
      br:
        sendCredToTikv: false
        cleanPolicy: Delete
        resources: {}
      s3:
        provider: aws
        region: {region-name}
        bucket: {bucket-name}
        prefix: {backup-path}
      serviceAccount: tidb-backup-manager
      toolImage: {br-image}
```
