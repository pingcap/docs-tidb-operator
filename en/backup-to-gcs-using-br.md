---
title: Back up Data to GCS Using BR
summary: Learn how to back up data to Google Cloud Storage (GCS) using BR.
---

# Back up Data to GCS Using BR

This document describes how to back up the data of a TiDB cluster in Kubernetes to [Google Cloud Storage](https://cloud.google.com/storage/docs/) (GCS). "Backup" in this document refers to full backup (ad-hoc full backup and scheduled full backup). [BR](https://pingcap.com/docs/stable/br/backup-and-restore-tool/) is used to get the logic backup of the TiDB cluster, and then this backup data is sent to GCS.

The backup method described in this document is implemented using Custom Resource Definition (CRD) in TiDB Operator v1.1 or later versions.

## Ad-hoc full backup

Ad-hoc full backup describes the backup by creating a `Backup` Custom Resource (CR) object. TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry, and you need to handle this error manually.

Currently, the above three authorization methods are supported for the ad-hoc full backup. This document provides examples in which the data of the `demo1` TiDB cluster in the `test1` Kubernetes namespace is backed up to AWS storage and all the above methods are used in the examples.

### Prerequisites for ad-hoc full backup

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test1` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. Create the `gcs-secret` secret which stores the credential used to access GCS:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic gcs-secret --from-file=credentials=./google-credentials.json -n test1
    ```

    The `google-credentials.json` file stores the service account key that you download from the GCP console. Refer to [GCP Documentation](https://cloud.google.com/docs/authentication/getting-started) for details.

3. Create the `backup-demo1-tidb-secret` secret which stores the root account and password needed to access the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
    ```

### Process of ad-hoc full backup

1. Create the `Backup` CR, and back up cluster data to GCS as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-gcs.yaml
    ```

    The content of `backup-gcs.yaml` is as follows:

    {{< copyable "shell-regular" >}}

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
    name: demo1-backup-gcs
    namespace: test1
    spec:
      # backupType: full
      from:
        host: ${tidb-host}
        port: ${tidb-port}
        user: ${tidb-user}
        secretName: backup-demo1-tidb-secret
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
        # statusAddr: ${status-addr}
        # concurrency: 4
        # rateLimit: 0
        # checksum: true
        # sendCredToTikv: true
      gcs:
        projectId: ${project-id}
        secretName: gcs-secret
        bucket: ${bucket}
        prefix: ${prefix}
        # location: us-east1
        # storageClass: STANDARD_IA
        # objectAcl: private
    ```

    In the example above, some parameters in `spec.br` can be ignored, such as `logLevel`, `statusAddr`, `concurrency`, `rateLimit`, `checksum`, and `sendCredToTikv`.

    <details>
    <summary>More description of parameters</summary>

    - `spec.br.cluster`: The name of the cluster to be backed up.
    - `spec.br.clusterNamespace`: The `namespace` of the cluster to be backed up.
    - `spec.br.logLevel`: The log level (`info` by default).
    - `spec.br.statusAddr`: The HTTP port used for listening a process status in BR to facilitate debugging. If not specified, BR does not listen the process status by default.
    - `spec.br.concurrency`: The number of threads used by each TiKV process during backup. Defaults to `4` for backup and `128` for restore.
    - `spec.br.rateLimit`: The speed limit, in MB/s. If set to `4`, the speed limit is 4 MB/s. The default is no limit.
    - `spec.br.checksum`: Whether to verify the files after the backup is completed. Defaults to `true`.
    - `spec.br.sendCredToTikv`: Whether the BR process passes its GCP privileges to the TiKV process. Defaults to `true`.
    </details>

    This example backs up all data in the TiDB cluster to GCS. Some parameters in `spec.gcs` can be ignored, such as `location`, `objectAcl`, and `storageClass`.

    The `projectId` in the configuration is the unique identifier for the user project on GCP. For how to obtain the identifier, see [GCP Documentation](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

    <details>
    <summary>Configure <code>storageClass</code>.</summary>

    GCS supports the following `storageClass` types:

    * `MULTI_REGIONAL`
    * `REGIONAL`
    * `NEARLINE`
    * `COLDLINE`
    * `DURABLE_REDUCED_AVAILABILITY`

    If you do not configure `storageClass`, the default is `COLDLINE`. See [GCS Documentation](https://cloud.google.com/storage/docs/storage-classes) for details.
    
    </details>

    <details>
    <summary>Configure the object access-control list (ACL) strategy</summary>

    CS supports the following ACL strategies:

    * `authenticatedRead`
    * `bucketOwnerFullControl`
    * `bucketOwnerRead`
    * `private`
    * `projectPrivate`
    * `publicRead`

    If you do not configure `storageClass`, the default is `COLDLINE`. See [GCS Documentation](https://cloud.google.com/storage/docs/storage-classes) for details.
    </details>

2. After creating the `Backup` CR, use the following command to check the backup status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -n test1 -owide
    ```

<details>

<summary>More descriptions of fields in `Backup` CR</summary>

* `.spec.metadata.namespace`: The namespace where the `Backup` CR is located.
* `.spec.from.host`: The address of the TiDB cluster to be backed up.
* `.spec.from.port`: The port of the TiDB cluster to be backed up.
* `.spec.from.user`: The accessing user of the TiDB cluster to be backed up.
* `.spec.gcs.bucket`: The name of the bucket which stores data.
* `.spec.gcs.prefix`: This field is used to make up the path of the remote storage: `s3://${.spec.gcs.bucket}/${.spec.gcs.prefix}/backupName`. This field can be ignored.
* `.spec.from.tidbSecretName`: The secret of the user password of the `.spec.from.user` TiDB cluster.
* `.spec.from.tlsClientSecretName`: The secret of the certificate used during the backup.

    If [TLS](enable-tls-between-components.md) is enabled for the TiDB cluster, but you do not want to back up data using the `${cluster_name}-cluster-client-secret` as described in [Enable TLS between TiDB Components](enable-tls-between-components.md), you can use the `.spec.from.tlsClientSecretName` parameter to specify a secret for the backup. To generate the secret, run the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${namespace} --from-file=tls.crt=${cert_path} --from-file=tls.key=${key_path} --from-file=ca.crt=${ca_path}
    ```

</details>

## Scheduled full backup

You can set a backup policy to perform scheduled backups of the TiDB cluster, and set a backup retention policy to avoid excessive backup items. A scheduled full backup is described by a custom `BackupSchedule` CR object. A full backup is triggered at each backup time point. Its underlying implementation is the ad-hoc full backup.

### Prerequisites for scheduled full backup

The prerequisites for the scheduled full backup is the same with the [prerequisites for ad-hoc full backup](#prerequisites-for-ad-hoc-full-backup).

### Process of scheduled full backup

1. Create the `BackupSchedule` CR, and back up cluster data as described below:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-gcs.yaml
    ```

    The content of `backup-scheduler-aws-s3.yaml` is as follows:

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
    name: demo1-backup-schedule-gcs
    namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        br:
          cluster: demo1
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status-addr}
          # concurrency: 4
          # rateLimit: 0
          # checksum: true
          # sendCredToTikv: true
        gcs:
          secretName: gcs-secret
          projectId: ${project-id}
          bucket: ${bucket}
          prefix: ${prefix}
          # location: us-east1
          # storageClass: STANDARD_IA
          # objectAcl: private
    ```

2. After creating the scheduled full backup, use the following command to check the backup status:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bks -n test1 -owide
    ```

    Use the following command to check all the backup items:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-gcs -n test1
    ```

From the example above, you can see that the `backupSchedule` configuration consists of two parts. One is the unique configuration of `backupSchedule`, and the other is `backupTemplate`. `backupTemplate` specifies the configuration related to GCS, which is the same as the configuration of the ad-hoc full backup to GCS (refer to [Ad-hoc backup process](#process-of-ad-hoc-full-backup) for details).

<details>
<summary>The unique configuration items of `backupSchedule`</summary>

* `.spec.maxBackups`: A backup retention policy, which determines the maximum number of backup items to be retained. When this value is exceeded, the outdated backup items will be deleted. If you set this configuration item to `0`, all backup items are retained.

* `.spec.maxReservedTime`: A backup retention policy based on time. For example, if you set the value of this configuration to `24h`, only backup items within the recent 24 hours are retained. All backup items out of this time are deleted. For the time format, refer to [`func ParseDuration`](https://golang.org/pkg/time/#ParseDuration). If you have set the maximum number of backup items and the longest retention time of backup items at the same time, the latter setting takes effect.

* `.spec.schedule`: The time scheduling format of Cron. Refer to [Cron](https://en.wikipedia.org/wiki/Cron) for details.

* `.spec.pause`: `false` by default. If this parameter is set to `true`, the scheduled scheduling is paused. In this situation, the backup operation will not be performed even if the scheduling time is reached. During this pause, the backup [Garbage Collection](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) (GC) runs normally. If you change `true` to `false`, the full backup process is restarted.

</details>
