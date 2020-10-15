---
title: Restore Data from GCS Using BR
summary: Learn how to restore data from Google Cloud Storage (GCS) using BR.
---

# Restore Data from GCS Using BR

This document describes how to restore the TiDB cluster data backed up using TiDB Operator in Kubernetes. [BR](https://docs.pingcap.com/tidb/dev/backup-and-restore-tool) is used to perform the restore.

The restore method described in this document is implemented based on Custom Resource Definition (CRD) in TiDB Operator v1.1 or later versions.

This document shows an example in which the backup data stored in the specified path on Google Cloud Storage (GCS) is restored to the TiDB cluster.

## Required database account privileges

* The `SELECT` and `UPDATE` privileges of the `mysql.tidb` table: Before and after the restoration, the `Restore` CR needs a database account with these privileges to adjust the GC time.

## Prerequisites

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test2` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. Create the `gcs-secret` secret which stores the credential used to access the GCS:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic gcs-secret --from-file=credentials=./google-credentials.json -n test1
    ```

    The `google-credentials.json` file stores the service account key that you download from the GCP console. Refer to [GCP Documentation](https://cloud.google.com/docs/authentication/getting-started) for details.

3. Create the `restore-demo2-tidb-secret` secret which stores the root account and password needed to access the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=user=root --from-literal=password=<password> --namespace=test2
    ```

## Process of restore

1. Create the `Restore` custom resource (CR), and restore the specified data to your cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore.yaml
    ```

    The content of `restore.yaml` file is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-gcs
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
        # sendCredToTikv: true
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      gcs:
        projectId: ${project-id}
        secretName: gcs-secret
        bucket: ${bucket}
        prefix: ${prefix}
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

2. After creating the `Restore` CR, execute the following command to check the restore status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get rt -n test2 -owide
    ```

This example restores the backup data stored in the `spec.gcs.prefix` folder of the `spec.gcs.bucket` bucket on GCS to the TiDB cluster `spec.to.host`. For more information on the configuration items of BR and GCS, refer to [`backup-gcs.yaml`](backup-to-gcs-using-br.md#process-of-ad-hoc-backup).

More descriptions of fields in the `Restore` CR are as follows:

* `.spec.metadata.namespace`: The namespace where the `Restore` CR is located.
* `.spec.to.host`: The address of the TiDB cluster to be restored.
* `.spec.to.port`: The port of the TiDB cluster to be restored.
* `.spec.to.user`: The accessing user of the TiDB cluster to be restored.
* `.spec.to.tidbSecretName`: The secret containg the password of the `.spec.to.user` in the TiDB cluster.
* `.spec.to.tlsClientSecretName`: The secret of the certificate used during the restore.

    If [TLS](enable-tls-between-components.md) is enabled for the TiDB cluster, but you do not want to restore data using the `${cluster_name}-cluster-client-secret` as described in [Enable TLS between TiDB Components](enable-tls-between-components.md), you can use the `.spec.to.tlsClientSecretName` parameter to specify a secret for the restore. To generate the secret, run the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${namespace} --from-file=tls.crt=${cert_path} --from-file=tls.key=${key_path} --from-file=ca.crt=${ca_path}
    ```

* `.spec.tableFilter`: BR only restores tables that match the [table filter rules](https://docs.pingcap.com/tidb/stable/table-filter/). This field can be ignored by default. If the field is not configured, BR restores all schemas except the system schemas.

    > **Note:**
    >
    > To use the table filter to exclude `db.table`, you need to add the `*.*` rule to include all tables first. For example:

    ```
    tableFilter:
    - "*.*"
    - "!db.table"
    ```

In the examples above, some parameters in `.spec.br` can be ignored, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, `timeAgo`, and `sendCredToTikv`.

* `.spec.br.cluster`: The name of the cluster to be backed up.
* `.spec.br.clusterNamespace`: The `namespace` of the cluster to be backed up.
* `.spec.br.logLevel`: The log level (`info` by default).
* `.spec.br.statusAddr`: The listening address through which BR provides statistics. If not specified, BR does not listen on any status address by default.
* `.spec.br.concurrency`: The number of threads used by each TiKV process during backup. Defaults to `4` for backup and `128` for restore.
* `.spec.br.rateLimit`: The speed limit, in MB/s. If set to `4`, the speed limit is 4 MB/s. The speed limit is not set by default.
* `.spec.br.checksum`: Whether to verify the files after the backup is completed. Defaults to `true`.
* `.spec.br.timeAgo`: Backs up the data before `timeAgo`. If the parameter value is not specified (empty by default), it means backing up the current data. It supports data formats such as "1.5h" and "2h45m". See [ParseDuration](https://golang.org/pkg/time/#ParseDuration) for more information.
* `.spec.br.sendCredToTikv`: Whether the BR process passes its GCP privileges to the TiKV process. Defaults to `true`.

## Troubleshooting

If you encounter any problem during the restore process, refer to [Common Deployment Failures](deploy-failures.md).
