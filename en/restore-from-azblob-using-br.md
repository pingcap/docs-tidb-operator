---
title: Restore Data from Azure Blob Storage Using BR
summary: Learn how to restore data from Azure Blob Storage using BR.
---

# Restore Data from Azure Blob Storage Using BR

This document describes how to restore the backup data stored in Azure Blob Storage to a TiDB cluster on Kubernetes, including two restoration methods:

- Full restoration. This method takes the backup data of snapshot backup and restores a TiDB cluster to the time point of the snapshot backup.
- Point-in-time recovery (PITR). This method takes the backup data of both snapshot backup and log backup and restores a TiDB cluster to any point in time.

The restore method described in this document is implemented based on Custom Resource Definition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

PITR enables you to restore a new TiDB cluster to any point in time of the backup cluster. To use PITR, you need the backup data of snapshot backup and log backup. During the restoration, the snapshot backup data is first restored to the TiDB cluster, and then the log backup data between the snapshot backup time point and the specified point in time is restored to the TiDB cluster.

> **Note:**
>
> - BR is only applicable to TiDB v3.1 or later releases.
> - PITR is only applicable to TiDB v6.3 or later releases.
> - Data restored by BR cannot be replicated to a downstream cluster, because BR directly imports SST and LOG files to TiDB and the downstream cluster currently cannot access the upstream SST and LOG files.

## Full restoration

This section provides an example about how to restore the backup data from the `spec.azblob.prefix` folder of the `spec.azblob.container` bucket on Azure Blob Storage to the `demo2` TiDB cluster in the `test2` namespace. The following are the detailed steps.

### Prerequisites: Complete the snapshot backup

In this example, the `my-full-backup-folder` folder in the `my-container` bucket of Azure Blob Storage stores the snapshot backup data. For steps of performing snapshot backup, refer to [Back up Data to Azure Blob Storage Using BR](backup-to-azblob-using-br.md).

### Step 1: Prepare the restoration environment

Before restoring backup data on Azure Blob Storage to TiDB using BR, take the following steps to prepare the restore environment:

1. Create the required role-based access control (RBAC) resources:

    ```shell
    kubectl apply -n test2 -f - <<EOF
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: tidb-backup-manager
      labels:
        app.kubernetes.io/component: tidb-backup-manager
    rules:
    - apiGroups: [""]
      resources: ["events"]
      verbs: ["*"]
    - apiGroups: ["br.pingcap.com"]
      resources: ["*"]
      verbs: ["get", "watch", "list", "update"]
    ---
    kind: ServiceAccount
    apiVersion: v1
    metadata:
      name: tidb-backup-manager
    ---
    kind: RoleBinding
    apiVersion: rbac.authorization.k8s.io/v1
    metadata:
      name: tidb-backup-manager
      labels:
        app.kubernetes.io/component: tidb-backup-manager
    subjects:
    - kind: ServiceAccount
      name: tidb-backup-manager
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: Role
      name: tidb-backup-manager
    EOF
    ```

2. Refer to [Grant permissions to an Azure account](grant-permissions-to-remote-storage.md#grant-permissions-to-an-azure-account) to grant access to remote storage. Azure provides two methods for granting permissions. After successful authorization, a Secret object named `azblob-secret` or `azblob-secret-ad` should exist in the namespace.

    > **Note:**
    >
    > - The authorized account must have at least write access to Blob data, such as the [Contributor](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#contributor) role.
    > - When creating the Secret object, you can customize its name. For demonstration purposes, this document uses `azblob-secret` as the example Secret name.

### Step 2: Restore the backup data to a TiDB cluster

Create a `Restore` CR named `demo2-restore-azblob` in the `test2` namespace to restore cluster data as follows:

```shell
kubectl apply -n test2 -f restore-full-azblob.yaml
```

The content of `restore-full-azblob.yaml` is as follows:

```yaml
---
apiVersion: br.pingcap.com/v1alpha1
kind: Restore
metadata:
  name: demo2-restore-azblob
  namespace: test2
spec:
  br:
    cluster: demo2
    # logLevel: info
    # statusAddr: ${status_addr}
    # concurrency: 4
    # rateLimit: 0
    # timeAgo: ${time}
    # checksum: true
    # sendCredToTikv: true
  azblob:
    secretName: azblob-secret
    container: my-container
    prefix: my-full-backup-folder
```

When configuring `restore-full-azblob.yaml`, note the following:

- For more information about Azure Blob Storage configuration, refer to [Azure Blob Storage fields](backup-restore-cr.md#azure-blob-storage-fields).
- Some parameters in `.spec.br` are optional, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, `timeAgo`, and `sendCredToTikv`. For more information about BR configuration, refer to [BR fields](backup-restore-cr.md#br-fields).
- `.spec.azblob.secretName`: fill in the name you specified when creating the Secret object, such as `azblob-secret`.
- For more information about the `Restore` CR fields, refer to [Restore CR fields](backup-restore-cr.md#restore-cr-fields).

After creating the `Restore` CR, execute the following command to check the restore status:

```shell
kubectl get restore -n test2 -o wide
```

```
NAME                   STATUS     ...
demo2-restore-azblob   Complete   ...
```

## Point-in-time recovery

This section provides an example about how to perform point-in-time recovery (PITR) in a `demo3` cluster in the `test3` namespace. PITR takes two steps:

1. Restore the cluster to the time point of the snapshot backup using the snapshot backup data in the `spec.pitrFullBackupStorageProvider.azblob.prefix` folder of the `spec.pitrFullBackupStorageProvider.azblob.container` bucket.
2. Restore the cluster to any point in time using the log backup data in the `spec.azblob.prefix` folder of the `spec.azblob.container` bucket.

The detailed steps are as follows.

### Prerequisites: Complete data backup

In this example, the `my-container` bucket of Azure Blob Storage stores the following two types of backup data:

- The snapshot backup data generated during the **log backup**, stored in the `my-full-backup-folder-pitr` folder.
- The log backup data, stored in the `my-log-backup-folder-pitr` folder.

For detailed steps of how to perform data backup, refer to [Back up data to Azure Blob Storage](backup-to-azblob-using-br.md).

> **Note:**
>
> The specified restoration time point must be between the snapshot backup time point and the log backup `checkpoint-ts`.

### Step 1: Prepare the restoration environment

The steps to prepare for a PITR are the same as those of [Full restoration](#full-restoration).

### Step 2: Restore the backup data to a TiDB cluster

The example in this section restores the snapshot backup data to the cluster. The specified restoration time point must be between [the time point of snapshot backup](backup-to-azblob-using-br.md#view-the-snapshot-backup-status) and the [`Log Checkpoint Ts` of log backup](backup-to-azblob-using-br.md#view-the-log-backup-status). The detailed steps are as follows:

1. Create a `Restore` CR named `demo3-restore-azblob` in the `test3` namespace and specify the restoration time point as `2022-10-10T17:21:00+08:00`:

    ```shell
    kubectl apply -n test3 -f restore-point-azblob.yaml
    ```

    The content of `restore-point-azblob.yaml` is as follows:

    ```yaml
    ---
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo3-restore-azblob
      namespace: test3
    spec:
      restoreMode: pitr
      br:
        cluster: demo3
      azblob:
        secretName: azblob-secret
        container: my-container
        prefix: my-log-backup-folder-pitr
      pitrRestoredTs: "2022-10-10T17:21:00+08:00"
      pitrFullBackupStorageProvider:
        azblob:
          secretName: azblob-secret
          container: my-container
          prefix: my-full-backup-folder-pitr
    ```

    When you configure `restore-point-azblob.yaml`, note the following:

    - `spec.restoreMode`: when you perform PITR, set this field to `pitr`. The default value of this field is `snapshot`, which means snapshot backup.

2. Wait for the restoration operation to complete:

    ```shell
    kubectl get jobs -n test3
    ```

    ```
    NAME                           COMPLETIONS   ...
    restore-demo3-restore-azblob   1/1           ...
    ```

    You can also check the restoration status by using the following command:

    ```shell
    kubectl get restore -n test3 -o wide
    ```

    ```
    NAME                   STATUS     ...
    demo3-restore-azblob   Complete   ...
    ```

## Troubleshooting

If you encounter any problem during the restoration process, refer to [Common Deployment Failures](deploy-failures.md).
