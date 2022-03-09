---
title: Backup and Restore Custom Resources
summary: Learn the fields in the Backup and Restore custom resources (CR).
---

# Backup and Restore Custom Resources

This document describes the fields in the `Backup`, `Restore`, and `BackupSchedule` custom resources (CR). You can use these fields to better perform the backup or restore of TiDB clusters in Kubernetes.

## Backup CR fields

To back up data for a TiDB cluster in Kubernetes, you can create a `Backup` custom resource (CR) object. For detailed backup process, refer to documents listed in [Back up data](backup-restore-overview.md#back-up-data).

This section introduces the fields in the `Backup` CR.

### General fields

* `.spec.metadata.namespace`: The namespace where the `Backup` CR is located.
* `.spec.toolImage`: The tool image used by `Backup`. TiDB Operator supports this configuration item starting from v1.1.9.

    - When using BR for backup, you can specify the BR version in this field.
        - If the field is not specified or the value is empty, the `pingcap/br:${tikv_version}` image is used for backup by default.
        - If the BR version is specified in this field, such as `.spec.toolImage: pingcap/br:v5.4.0`, the image of the specified version is used for backup.
        - If an image is specified without the version, such as `.spec.toolImage: private/registry/br`, the `private/registry/br:${tikv_version}` image is used for backup.
    - When using Dumpling for backup, you can specify the Dumpling version in this field.
        - If the Dumpling version is specified in this field, such as `spec.toolImage: pingcap/dumpling:v5.4.0`, the image of the specified version is used for backup.
        - If the field is not specified, the Dumpling version specified in `TOOLKIT_VERSION` of the [Backup Manager Dockerfile](https://github.com/pingcap/tidb-operator/blob/master/images/tidb-backup-manager/Dockerfile) is used for backup by default.

* `.spec.tikvGCLifeTime`: The temporary `tikv_gc_life_time` time setting during the backup, which defaults to `72h`.

    Before the backup begins, if the `tikv_gc_life_time` setting in the TiDB cluster is smaller than `spec.tikvGCLifeTime` set by the user, TiDB Operator [adjusts the value of `tikv_gc_life_time`](https://docs.pingcap.com/tidb/stable/dumpling-overview#tidb-gc-settings-when-exporting-a-large-volume-of-data) to the value of `spec.tikvGCLifeTime`. This operation makes sure that the backup data is not garbage-collected by TiKV.

    After the backup, no matter the backup is successful or not, as long as the previous `tikv_gc_life_time` value is smaller than `.spec.tikvGCLifeTime`, TiDB Operator tries to set `tikv_gc_life_time` to the previous value.

    In extreme cases, if TiDB Operator fails to access the database, TiDB Operator cannot automatically recover the value of `tikv_gc_life_time` and treats the backup as failed.

    In such cases, you can view `tikv_gc_life_time` of the current TiDB cluster using the following statement:

    {{< copyable "sql" >}}

    ```sql
    SELECT VARIABLE_NAME, VARIABLE_VALUE FROM mysql.tidb WHERE VARIABLE_NAME LIKE "tikv_gc_life_time";
    ```

    In the output of the command above, if the value of `tikv_gc_life_time` is still larger than expected (usually `10m`), you need to manually [set `tikv_gc_life_time` back](https://docs.pingcap.com/tidb/stable/dumpling-overview#tidb-gc-settings-when-exporting-a-large-volume-of-data) to the previous value.

* `.spec.cleanPolicy`: The cleaning policy for the backup data when the backup CR is deleted. You can choose from three clean policies:

    * `Retain`: Under any circumstances, retain the backup data when deleting the backup CR.
    * `Delete`: Under any circumstances, delete the backup data when deleting the backup CR.
    * `OnFailure`: If the backup fails, delete the backup data when deleting the backup CR.

    If this field is not configured, or if you configure a value other than the three policies above, the backup data is retained.

    Note that in v1.1.2 and earlier versions, this field does not exist. The backup data is deleted along with the CR by default. For v1.1.3 or later versions, if you want to keep this earlier behavior, set this field to `Delete`.

* `.spec.from.host`: The address of the TiDB cluster to be backed up, which is the service name of the TiDB cluster to be exported, such as `basic-tidb`.
* `.spec.from.port`: The port of the TiDB cluster to be backed up.
* `.spec.from.user`: The user of the TiDB cluster to be backed up.
* `.spec.from.secretName`: The secret that contains the password of the `.spec.from.user`.
* `.spec.from.tlsClientSecretName`: The secret of the certificate used during the backup.

    If [TLS](enable-tls-between-components.md) is enabled for the TiDB cluster, but you do not want to back up data using the `${cluster_name}-cluster-client-secret` created when you [enable TLS between TiDB components](enable-tls-between-components.md), you can use the `.spec.from.tlsClient.tlsSecret` parameter to specify a secret for the backup. To generate the secret, run the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${namespace} --from-file=tls.crt=${cert_path} --from-file=tls.key=${key_path} --from-file=ca.crt=${ca_path}
    ```

* `.spec.storageClassName`: The persistent volume (PV) type specified for the backup operation.
* `.spec.storageSize`: The PV size specified for the backup operation (`100 GiB` by default). This value must be greater than the size of the TiDB cluster to be backed up.

    The PVC name corresponding to the `Backup` CR of a TiDB cluster is fixed. If the PVC already exists in the cluster namespace and the size is smaller than `spec.storageSize`, you need to first delete this PVC and then run the Backup job.

* `.spec.tableFilter`: Specifies tables that match the [table filter rules](https://docs.pingcap.com/tidb/stable/table-filter/) for BR or Dumpling. This field can be ignored by default.

    When the field is not configured, if you use Dumpling, the default value of `tableFilter` is as follows:

    ```bash
    tableFilter:
    - "*.*"
    - "!/^(mysql|test|INFORMATION_SCHEMA|PERFORMANCE_SCHEMA|METRICS_SCHEMA|INSPECTION_SCHEMA)$/.*"
    ```

    When the field is not configured, if you use BR, BR backs up all schemas except the system schema.

    > **Note:**
    >
    > If you want to backup up all table except `db.table` using the `"!db.table"` rule, you need to first add the `*.*` rule to include all tables. For example:
    >
    > ```
    > tableFilter:
    > - "*.*"
    > - "!db.table"
    > ```

### BR fields

* `.spec.br.cluster`: The name of the cluster to be backed up.
* `.spec.br.clusterNamespace`: The `namespace` of the cluster to be backed up.
* `.spec.br.logLevel`: The log level (`info` by default).
* `.spec.br.statusAddr`: The listening address through which BR provides statistics. If not specified, BR does not listen on any status address by default.
* `.spec.br.concurrency`: The number of threads used by each TiKV process during backup. Defaults to `4` for backup and `128` for restore.
* `.spec.br.rateLimit`: The speed limit, in MB/s. If set to `4`, the speed limit is 4 MB/s. The speed limit is not set by default.
* `.spec.br.checksum`: Whether to verify the files after the backup is completed. Defaults to `true`.
* `.spec.br.timeAgo`: Backs up the data before `timeAgo`. If the parameter value is not specified (empty by default), it means backing up the current data. It supports data formats such as `"1.5h"` and `"2h45m"`. See [ParseDuration](https://golang.org/pkg/time/#ParseDuration) for more information.
* `.spec.br.sendCredToTikv`: Whether the BR process passes its AWS or GCP permissions to the TiKV process. Defaults to `true`.
* `.spec.br.options`: The extra arguments that BR supports. This field is supported since TiDB Operator v1.1.6. It accepts an array of strings and can be used to specify the last backup timestamp `--lastbackupts` for incremental backup.

### S3 storage fields

* `.spec.s3.provider`: The supported S3-compatible storage provider. All supported providers are as follows:

    - `alibaba`: Alibaba Cloud Object Storage System (OSS), formerly Aliyun
    - `digitalocean`: Digital Ocean Spaces
    - `dreamhost`: Dreamhost DreamObjects
    - `ibmcos`: IBM COS S3
    - `minio`: Minio Object Storage
    - `netease`: Netease Object Storage (NOS)
    - `wasabi`: Wasabi Object Storage
    - `other`: Any other S3 compatible provider

* `spec.s3.region`: If you want to use Amazon S3 for backup storage, configure this field as the region where Amazon S3 is located.
* `.spec.s3.bucket`: The name of the bucket of the S3-compatible storage.
* `.spec.s3.prefix`: If you set this field, the value is used to make up the remote storage path `s3://${.spec.s3.bucket}/${.spec.s3.prefix}/backupName`.
* `.spec.s3.endpoint`：The endpoint of S3 compatible storage service, for example, `http://minio.minio.svc.cluster.local:9000`.
* `.spec.s3.secretName`：The name of secret which stores S3 compatible storage's access key and secret key.
* `.spec.s3.acl`: The supported access-control list (ACL) policies.

    Amazon S3 supports the following ACL options:

    * `private`
    * `public-read`
    * `public-read-write`
    * `authenticated-read`
    * `bucket-owner-read`
    * `bucket-owner-full-control`

    If the field is not configured, the policy defaults to `private`. For more information on the ACL policies, refer to [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html).

* `.spec.s3.storageClass`: The supported storage class.

    Amazon S3 supports the following storage class options:

    * `STANDARD`
    * `REDUCED_REDUNDANCY`
    * `STANDARD_IA`
    * `ONEZONE_IA`
    * `GLACIER`
    * `DEEP_ARCHIVE`

    If the field is not configured, the storage class defaults to `STANDARD_IA`. For more information on storage classes, refer to [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html).

### GCS fields

* `.spec.gcs.projectId`: The unique identifier of the user project on GCP. To obtain the project ID, refer to [GCP documentation](https://cloud.google.com/resource-manager/docs/creating-managing-projects).
* `.spec.gcs.bucket`: The name of the bucket which stores data.
* `.spec.gcs.prefix`: If you set this field, the value is used to make up the path of the remote storage: `gcs://${.spec.gcs.bucket}/${.spec.gcs.prefix}/backupName`.
* `spec.gcs.storageClass`: The supported storage class.

    GCS supports the following storage class options:

    * `MULTI_REGIONAL`
    * `REGIONAL`
    * `NEARLINE`
    * `COLDLINE`
    * `DURABLE_REDUCED_AVAILABILITY`

    If the field is not configured, the storage class defaults to `COLDLINE`. For more information on storage classes, refer to [GCS documentation](https://cloud.google.com/storage/docs/storage-classes).

* `.spec.gcs.objectAcl`: The supported object access-control list (ACL) policies.

    GCS supports the following object ACL options:

    * `authenticatedRead`
    * `bucketOwnerFullControl`
    * `bucketOwnerRead`
    * `private`
    * `projectPrivate`
    * `publicRead`

    If the field is not configured, the policy defaults to `private`. For more information on the ACL policies, refer to [GCS documentation](https://cloud.google.com/storage/docs/access-control/lists).

* `.spec.gcs.bucketAcl`: The supported bucket access-control list (ACL) policies.

    GCS supports the following bucket ACL options:

    * `authenticatedRead`
    * `private`
    * `projectPrivate`
    * `publicRead`
    * `publicReadWrite`

    If the field is not configured, the policy defaults to `private`. For more information on the ACL policies, refer to [GCS documentation](https://cloud.google.com/storage/docs/access-control/lists).

### Local storage fields

* `.spec.local.prefix`: The storage directory of the persistent volumes. If you set this field, the value is used to make up the storage path of the persistent volume: `local://${.spec.local.volumeMount.mountPath}/${.spec.local.prefix}/`.
* `.spec.local.volume`: The persistent volume configuration.
* `.spec.local.volumeMount`: The persistent volume mount configuration.

## Restore CR fields

To restore data to a TiDB cluster in Kubernetes, you can create a `Restore` CR object. For detailed restore process, refer to documents listed in [Restore data](backup-restore-overview.md#restore-data).

This section introduces the fields in the `Restore` CR.

* `.spec.metadata.namespace`: The namespace where the `Restore` CR is located.
* `.spec.toolImage`：The tools image used by `Restore`. TiDB Operator supports this configuration starting from v1.1.9.

    - When using BR for restoring, you can specify the BR version in this field. For example,`spec.toolImage: pingcap/br:v5.4.0`. If not specified, `pingcap/br:${tikv_version}` is used for restoring by default.
    - When using Lightning for restoring, you can specify the Lightning version in this field. For example, `spec.toolImage: pingcap/lightning:v5.4.0`. If not specified, the Lightning version specified in `TOOLKIT_VERSION` of the [Backup Manager Dockerfile](https://github.com/pingcap/tidb-operator/blob/master/images/tidb-backup-manager/Dockerfile) is used for restoring by default.

* `.spec.to.host`: The address of the TiDB cluster to be restored.
* `.spec.to.port`: The port of the TiDB cluster to be restored.
* `.spec.to.user`: The user of the TiDB cluster to be restored.
* `.spec.to.secretName`: The secret that contains the password of the `.spec.to.user`.
* `.spec.to.tlsClientSecretName`: The secret of the certificate used during the restore.

    If [TLS](enable-tls-between-components.md) is enabled for the TiDB cluster, but you do not want to restore data using the `${cluster_name}-cluster-client-secret` created when you [enable TLS between TiDB components](enable-tls-between-components.md), you can use the `.spec.to.tlsClient.tlsSecret` parameter to specify a secret for the restore. To generate the secret, run the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${namespace} --from-file=tls.crt=${cert_path} --from-file=tls.key=${key_path} --from-file=ca.crt=${ca_path}
    ```

* `.spec.storageClassName`: The persistent volume (PV) type specified for the restore operation.
* `.spec.storageSize`: The PV size specified for the restore operation. This value must be greater than the size of the backup data.
* `.spec.tableFilter`: Specifies tables that match the [table filter rules](https://docs.pingcap.com/tidb/stable/table-filter/) for BR. This field can be ignored by default.

    When the field is not configured, if you use TiDB Lightning, the default `tableFilter` value for TiDB Lightning is as follows:

    ```bash
    tableFilter:
    - "*.*"
    - "!/^(mysql|test|INFORMATION_SCHEMA|PERFORMANCE_SCHEMA|METRICS_SCHEMA|INSPECTION_SCHEMA)$/.*"
    ```

    When the field is not configured, if you use BR, BR restores all the schemas in the backup file.

    > **Note:**
    >
    > If you want to backup up all table except `db.table` using the `"!db.table"` rule, you need to first add the `*.*` rule to include all tables. For example:
    >
    > ```
    > tableFilter:
    > - "*.*"
    > - "!db.table"
    > ```

* `.spec.br`: BR-related configuration. Refer to [BR fields](#br-fields).
* `.spec.s3`: S3-related configuration. Refer to [S3 storage fields](#s3-storage-fields).
* `.spec.gcs`: GCS-related configuration. Refer to [GCS fields](#gcs-fields).
* `.spec.local`: Persistent volume-related configuration. Refer to [Local storage fields](#local-storage-fields).

## BackupSchedule CR fields

The `backupSchedule` configuration consists of two parts. One is `backupTemplate`, and the other is the unique configuration of `backupSchedule`.

`backupTemplate` specifies the configuration related to the cluster and remote storage, which is the same as the `spec` configuration of [the `Backup` CR](#backup-cr-fields).

The unique configuration items of `backupSchedule` are as follows:

* `.spec.maxBackups`: A backup retention policy, which determines the maximum number of backup files to be retained. When the number of backup files exceeds this value, the outdated backup file will be deleted. If you set this field to `0`, all backup items are retained.
* `.spec.maxReservedTime`: A backup retention policy based on time. For example, if you set the value of this field to `24h`, only backup files within the recent 24 hours are retained. All backup files older than this value are deleted. For the time format, refer to [`func ParseDuration`](https://golang.org/pkg/time/#ParseDuration). If you have set `.spec.maxBackups` and `.spec.maxReservedTime` at the same time, the latter takes effect.
* `.spec.schedule`: The time scheduling format of Cron. Refer to [Cron](https://en.wikipedia.org/wiki/Cron) for details.
* `.spec.pause`: `false` by default. If this field is set to `true`, the scheduled scheduling is paused. In this situation, the backup operation will not be performed even if the scheduling time point is reached. During this pause, the backup garbage collection runs normally. If you change `true` to `false`, the scheduled full backup process is restarted.
