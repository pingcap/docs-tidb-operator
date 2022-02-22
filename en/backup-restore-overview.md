---
title: Backup and Restore Overview
summary: Learn how to perform backup and restore on the TiDB cluster in Kubernetes using BR, Dumpling, and TiDB Lightning.
---

# Backup and Restore Overview

This document describes how to perform backup and restore on the TiDB cluster in Kubernetes. The backup and restore tools used are Dumpling, TiDB Lightning, and Backup & Restore (BR).

[Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) is a data export tool, which exports data stored in TiDB or MySQL as SQL or CSV data files. Dumpling can be used to make a logical full backup or export.

[TiDB Lightning](https://docs.pingcap.com/tidb/stable/get-started-with-tidb-lightning) is a tool used for fast full data import into a TiDB cluster. TiDB Lightning supports Dumpling or CSV format data source. TiDB Lightning can be used to make a logical full data restore or import.

[BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-tool) is a command-line tool for distributed backup and restoration of the TiDB cluster data. Compared with Dumpling and Mydumper, BR is more suitable for huge data volumes. BR only supports TiDB v3.1 and later versions. For incremental backup insensitive to latency, refer to [BR Overview](https://docs.pingcap.com/tidb/stable/backup-and-restore-tool). For real-time incremental backup, refer to [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview).

TiDB Operator 1.1 and later versions implement the backup and restore methods using Custom Resource Definition (CRD):

+ If your TiDB cluster version is v3.1 or later, refer to the following documents:

    - [Back up Data to S3-Compatible Storage Using BR](backup-to-aws-s3-using-br.md)
    - [Back up Data to GCS Using BR](backup-to-gcs-using-br.md)
    - [Back up Data to PV Using BR](backup-to-pv-using-br.md)
    - [Restore Data from S3-Compatible Storage Using BR](restore-from-aws-s3-using-br.md)
    - [Restore Data from GCS Using BR](restore-from-gcs-using-br.md)
    - [Restore Data from PV Using BR](restore-from-pv-using-br.md)

+ If your TiDB cluster version is earlier than v3.1, refer to the following documents:

    - [Back up Data to S3-Compatible Storage Using Dumpling](backup-to-s3.md)
    - [Back up Data to GCS Using Dumpling](backup-to-gcs.md)
    - [Restore Data from S3-Compatible Storage Using TiDB Lightning](restore-from-s3.md)
    - [Restore Data from GCS Using TiDB Lightning](restore-from-gcs.md)

## User scenarios

### Back up data

If you have the following backup needs, you can use BR to make a backup of the TiDB cluster data:

- To back up a large volume of data at a fast speed
- To get a direct backup of data as SST files (key-value pairs)
- To perform incremental backup that is insensitive to latency

Refer to the following documents for more information:

- [Back up Data to S3-Compatible Storage Using BR](backup-to-aws-s3-using-br.md)
- [Back up Data to GCS Using BR](backup-to-gcs-using-br.md)
- [Back up Data to PV Using BR](backup-to-pv-using-br.md)

If you have the following backup needs, you can use Dumpling to make a backup of the TiDB cluster data:

- To export SQL or CSV files
- To limit the memory usage of a single SQL statement
- To export the historical data snapshot of TiDB

Refer to the following documents for more information:

- [Back up Data to S3-Compatible Storage Using Dumpling](backup-to-s3.md)
- [Back up Data to GCS Using Dumpling](backup-to-gcs.md)

### Restore data

If you need to recover the SST files exported by BR to a TiDB cluster, you can use BR. Refer to the following documents for more information:

- [Restore Data from S3-Compatible Storage Using BR](restore-from-aws-s3-using-br.md)
- [Restore Data from GCS Using BR](restore-from-gcs-using-br.md)
- [Restore Data from PV Using BR](restore-from-pv-using-br.md)

If you need to restore data from SQL or CSV files exported by Dumpling or other compatible data sources to a TiDB cluster, you can use TiDB Lightning. Refer to the following documents for more information:

- [Restore Data from S3-Compatible Storage Using TiDB Lightning](restore-from-s3.md)
- [Restore Data from GCS Using TiDB Lightning](restore-from-gcs.md)

## Backup and restore process

To make a backup of the TiDB cluster in Kubernetes, you need to create a [`Backup` CR](backup-restore-cr.md#backup-cr-fields) object to describe the backup or create a [`BackupSchedule` CR](backup-restore-cr.md#backupschedule-cr-fields) object to describe a scheduled backup.

To restore data to the TiDB cluster in Kubernetes, you need to create a [`Restore` CR](backup-restore-cr.md#restore-cr-fields) object to describe the restore.

After creating the CR object, according to your configuration, TiDB Operator chooses the corresponding tool and performs the backup or restore.

## Delete the Backup CR

You can delete the `Backup` CR or `BackupSchedule` CR by running the following commands:

{{< copyable "shell-regular" >}}

```shell
kubectl delete backup ${name} -n ${namespace}
kubectl delete backupschedule ${name} -n ${namespace}
```

If you use TiDB Operator v1.1.2 or an earlier version, or if you use TiDB Operator v1.1.3 or a later version and set the value of `spec.cleanPolicy` to `Delete`, TiDB Operator cleans the backup data when it deletes the CR.

In such cases, if you need to delete the namespace, it is recommended that you first delete all the `Backup`/`BackupSchedule` CRs and then delete the namespace.

If you delete the namespace before you delete the `Backup`/`BackupSchedule` CR, TiDB Operator will keep creating jobs to clean the backup data. However, because the namespace is in `Terminating` state, TiDB Operator fails to create such a job, which causes the namespace to be stuck in this state.

To address this issue, delete `finalizers` by running the following command:

{{< copyable "shell-regular" >}}

```shell
kubectl patch -n ${namespace} backup ${name} --type merge -p '{"metadata":{"finalizers":[]}}'
```

### Clean backup data

For TiDB Operator v1.2.3 and earlier versions, TiDB Operator cleans the backup data by deleting the backup files one by one.

For TiDB Operator v1.2.4 and later versions, TiDB Operator cleans the backup data by deleting the backup files in batches. For the batch deletion, the deletion methods are different depending on the type of backend storage used for backups.

* For the S3-compatible backend storage, TiDB Operator uses the concurrent batch deletion method, which deletes files in batch concurrently. TiDB Operator starts multiple goroutines concurrently, and each goroutine uses the batch delete API ["DeleteObjects"](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObjects.html) to delete multiple files.
* For other types of backend storage, TiDB Operator uses the concurrent deletion method, which deletes files concurrently. TiDB Operator starts multiple goroutines, and each goroutine deletes one file at a time.

For TiDB Operator v1.2.4 and later versions, you can configure the following fields in the Backup CR to control the clean behavior:

* `.spec.cleanOption.pageSize`: Specifies the number of files to be deleted in each batch at a time. The default value is 10000.
* `.spec.cleanOption.disableBatchConcurrency`: If the value of this field is `true`, TiDB Operator disables the concurrent batch deletion method and uses the concurrent deletion method.

    If your S3-compatible backend storage does not support the `DeleteObjects` API, the default concurrent batch deletion method fails. You need to configure this field to `true` to use the concurrent deletion method.

* `.spec.cleanOption.batchConcurrency`: Specifies the number of goroutines to start for the concurrent batch deletion method. The default value is `10`.
* `.spec.cleanOption.routineConcurrency`: Specifies the number of goroutines to start  for the concurrent deletion method. The default value is `100`.
