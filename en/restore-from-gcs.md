---
title: Restore Data from GCS
summary: Learn how to restore the backup data from GCS.
---

# Restore Data from GCS

This document describes how to restore the TiDB cluster data backed up using TiDB Operator in Kubernetes.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator v1.1 or later versions. For the underlying implementation, [TiDB Lightning TiDB-backend](https://docs.pingcap.com/tidb/stable/tidb-lightning-backends#tidb-lightning-tidb-backend) is used to perform the restore.

TiDB Lightning is a tool used for fast full import of large amounts of data into a TiDB cluster. It reads data from local disks, Google Cloud Storage (GCS) or Amazon S3. TiDB Lightning supports three backends: `Importer-backend`, `Local-backend`, and `TiDB-backend`. In this document, `TiDB-backend` is used. For the differences of these backends and how to choose backends, see [TiDB Lightning Backends](https://docs.pingcap.com/tidb/stable/tidb-lightning-backends). To import data using `Importer-backend` or `Local-backend`, see [Import Data](restore-data-using-tidb-lightning.md).

This document shows an example in which the backup data stored in the specified path on [GCS](https://cloud.google.com/storage/docs/) is restored to the TiDB cluster.

## Usage scenarios

You can use the restore solution introduced in this document if you need to export the backup data from GCS to a TiDB cluster, with the following requirements:

- To restore data with lower resource usage and lower network bandwidth usage. A restore speed of 50 GB/h is acceptable.
- To import data into the cluster with ACID compliance.
- The TiDB cluster can still provide services during the restore process.

## Prerequisites

Before you perform the data restore, you need to prepare the restore environment and get the required database account privileges.

### Prepare the restore environment

1. Download [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml) and execute the following command to create the role-based access control (RBAC) resources in the `test2` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. Grant permissions to the remote storage.

    Refer to [GCS account permissions](grant-permissions-to-remote-storage.md#gcs-account-permissions).

3. Create the `restore-demo2-tidb-secret` secret which stores the root account and password needed to access the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=${password} --namespace=test2
    ```

### Get the required database account privileges

Before you use TiDB Lightning to restore the backup data in GCS to the TiDB cluster, make sure that you have the following database account privileges:

| Privileges | Scope |
|:----|:------|
| SELECT | Tables |
| INSERT | Tables |
| UPDATE | Tables |
| DELETE | Tables |
| CREATE | Databases, tables |
| DROP | Databases, tables |
| ALTER | Tables |

## Restore process

1. Create the restore custom resource (CR) and restore the backup data to the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore.yaml
    ```

    The `restore.yaml` file has the following content:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore
      namespace: test2
    spec:
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      gcs:
        projectId: ${project_id}
        secretName: gcs-secret
        path: gcs://${backup_path}
      # storageClassName: local-storage
      storageSize: 1Gi
    ```

    The example above restores data from the `spec.gcs.path` path on GCS to the `spec.to.host` TiDB cluster. For more information about GCS configuration, refer to [GCS fields](backup-restore-cr.md#gcs-fields).

    For more information about the `Restore` CR fields, refer to [Restore CR fields](backup-restore-cr.md#restore-cr-fields).

2. After creating the `Restore` CR, execute the following command to check the restore status:

    {{< copyable "shell-regular" >}}

     ```shell
     kubectl get rt -n test2 -owide
     ```

> **Note:**
>
> TiDB Operator creates a PVC for data recovery. The backup data is downloaded from the remote storage to the PV first, and then restored. If you want to delete this PVC after the recovery is completed, you can refer to [Delete Resource](cheat-sheet.md#delete-resources) to delete the recovery Pod first, and then delete the PVC.

## Troubleshooting

If you encounter any problem during the restore process, refer to [Common Deployment Failures](deploy-failures.md).
