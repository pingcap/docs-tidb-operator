---
title: Restore Data from PV
summary: Learn how to restore data from Persistent Volume (PV) using BR.
---

# Restore Data from PV

This document describes how to restore the TiDB cluster data backed up using TiDB Operator in Kubernetes. PVs in this documentation can be any [Kubernetes supported PV types](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes). This document shows how to restore data from NFS to TiDB.

The restore method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator. For the underlying implementation, [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-tool) is used to restore the data. BR stands for Backup & Restore, which is a command-line tool for distributed backup and recovery of the TiDB cluster data.

## Usage scenarios

After backing up TiDB cluster data to PVs using BR, if you need to recover the backup SST (key-value pairs) files from PVs to a TiDB cluster, you can follow steps in this document to restore the data using BR.

> **Note:**
>
> - BR is only applicable to TiDB v3.1 or later releases.
> - Data restored by BR cannot be replicated to a downstream cluster, because BR directly imports SST files to TiDB and the downstream cluster currently cannot access the upstream SST files.

## Step 1: Prepare the restore environment

Before restoring backup data on PVs to TiDB using BR, take the following steps to prepare the restore environment:

1. Download [`backup-rbac.yaml`](https://github.com/pingcap/tidb-operator/blob/v1.3.9/manifests/backup/backup-rbac.yaml).

2. Execute the following command to create the role-based access control (RBAC) resources in the `test2` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

3. Make sure that the NFS server is accessible from your Kubernetes cluster.

4. For a TiDB version earlier than v4.0.8, you also need to complete the following preparation steps. For TiDB v4.0.8 or a later version, skip these preparation steps.

    1. Make sure that you have the `SELECT` and `UPDATE` privileges on the `mysql.tidb` table of the target database so that the `Restore` CR can adjust the GC time before and after the restore.

    2. Create the `restore-demo2-tidb-secret` secret to store the account and password to access the TiDB cluster:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
        ```

## Step 2: Restore the backup data to a TiDB cluster

1. Create the `Restore` custom resource (CR), and restore the specified data to your cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore.yaml
    ```

    The content of the `restore.yaml` file is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-nfs
      namespace: test2
    spec:
      # backupType: full
      br:
        cluster: demo2
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status-addr}
        # concurrency: 4
        # rateLimit: 0
        # checksum: true
      # # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      # to:
      #   host: ${tidb_host}
      #   port: ${tidb_port}
      #   user: ${tidb_user}
      #   secretName: restore-demo2-tidb-secret
      local:
        prefix: backup-nfs
        volume:
          name: nfs
          nfs:
            server: ${nfs_server_if}
            path: /nfs
        volumeMount:
          name: nfs
          mountPath: /nfs
    ```

    When configuring `restore.yaml`, note the following:

    - The example above restores data from the `local://${.spec.local.volume.nfs.path}/${.spec.local.prefix}/` directory on NFS to the `demo2` TiDB cluster in the `test2` namespace. For more information about PV configuration, refer to [Local storage fields](backup-restore-cr.md#local-storage-fields).

    - Some parameters in `spec.br` are optional, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, `timeAgo`, and `sendCredToTikv`. For more information about `.spec.br`, refer to [BR fields](backup-restore-cr.md#br-fields).

    - For v4.0.8 or a later version, BR can automatically adjust `tikv_gc_life_time`. You do not need to configure the `spec.to` field in the `Restore` CR.

    - For more information about the `Restore` CR fields, refer to [Restore CR fields](backup-restore-cr.md#restore-cr-fields).

2. After creating the `Restore` CR, execute the following command to check the restore status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get rt -n test2 -owide
    ```

## Troubleshooting

If you encounter any problem during the restore process, refer to [Common Deployment Failures](deploy-failures.md).
