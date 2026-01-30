---
title: Backup and Restore Overview
summary: Learn how to perform backup and restore on the TiDB cluster on Kubernetes.
---

# Backup and Restore Overview

This document describes how to perform backup and restore on the TiDB cluster on Kubernetes. To back up and restore your data, you can use the Dumpling, TiDB Lightning, and Backup & Restore (BR) tools.

[Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) is a data export tool, which exports data stored in TiDB or MySQL as SQL or CSV data files. You can use Dumpling to make a logical full backup or export.

[TiDB Lightning](https://docs.pingcap.com/tidb/stable/get-started-with-tidb-lightning) is a tool used for fast full data import into a TiDB cluster. TiDB Lightning supports Dumpling or CSV format data source. You can use TiDB Lightning to make a logical full data restore or import.

[BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview) is a command-line tool for distributed backup and restoration of the TiDB cluster data. Compared with Dumpling and Mydumper, BR is more suitable for huge data volumes. BR only supports TiDB v3.1 and later versions. For incremental backup insensitive to latency, refer to [BR Overview](https://docs.pingcap.com/tidb/stable/backup-and-restore-overview). For real-time incremental backup, refer to [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview).

## Usage scenarios

### Back up data

If you have the following backup needs, you can use [BR](https://docs.pingcap.com/tidb/stable/backup-and-restore-tool) to make a backup of your TiDB cluster data:

- To back up a large volume of data (more than 1 TiB) at a fast speed
- To get a direct backup of data as SST files (key-value pairs)
- To perform incremental backup that is insensitive to latency

For more information, see the following documents:

- [Back Up Data to S3-Compatible Storage Using BR](backup-to-aws-s3-using-br.md)
- [Back Up Data to GCS Using BR](backup-to-gcs-using-br.md)
- [Back Up Data to Azure Blob Storage Using BR](backup-to-azblob-using-br.md)

### Restore data

To recover the SST files exported by BR to a TiDB cluster, use BR. For more information, see the following documents:

- [Restore Data from S3-Compatible Storage Using BR](restore-from-aws-s3-using-br.md)
- [Restore Data from GCS Using BR](restore-from-gcs-using-br.md)
- [Restore Data from Azure Blob Storage Using BR](restore-from-azblob-using-br.md)

## Backup and restore process

To make a backup of the TiDB cluster on Kubernetes, you need to create a [`Backup` CR](backup-restore-cr.md#backup-cr-fields) object to describe the backup.

> **Warning:**
>
> Currently, TiDB Operator v2 does not support the `BackupSchedule` CR. To perform scheduled snapshot backups, scheduled log backups, or scheduled compact log backups, use TiDB Operator v1.x and see [BackupSchedule CR fields](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/backup-restore-cr/#backupschedule-cr-fields).

To restore data to the TiDB cluster on Kubernetes, you need to create a [`Restore` CR](backup-restore-cr.md#restore-cr-fields) object to describe the restore.

After creating the CR object, according to your configuration, TiDB Operator chooses the corresponding tool and performs the backup or restore.

## Delete the Backup CR

You can delete the `Backup` CR by running the following commands:

```shell
kubectl delete backup ${name} -n ${namespace}
```

If you set the value of `spec.cleanPolicy` to `Delete`, TiDB Operator cleans the backup data when it deletes the CR.

TiDB Operator automatically attempts to stop running log backup tasks when you delete the Custom Resource (CR). This automatic stop feature only applies to log backup tasks that are running normally and does not handle tasks in an error or failed state.

In such cases, if you need to delete the namespace, it is recommended that you first delete the `Backup` CR and then delete the namespace.

If you delete the namespace before you delete the `Backup` CR, TiDB Operator will keep creating jobs to clean the backup data. However, because the namespace is in `Terminating` state, TiDB Operator fails to create such a job, which causes the namespace to be stuck in this state.

To address this issue, delete `finalizers` by running the following command:

```shell
kubectl patch -n ${namespace} backup ${name} --type merge -p '{"metadata":{"finalizers":[]}}'
```

### Clean backup data

TiDB Operator cleans the backup data by deleting the backup files in batches. For the batch deletion, the deletion methods are different depending on the type of backend storage used for backups.

* For the S3-compatible backend storage, TiDB Operator uses the concurrent batch deletion method, which deletes files in batch concurrently. TiDB Operator starts multiple goroutines concurrently, and each goroutine uses the batch delete API [`DeleteObjects`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObjects.html) to delete multiple files.
* For other types of backend storage, TiDB Operator uses the concurrent deletion method, which deletes files concurrently. TiDB Operator starts multiple goroutines, and each goroutine deletes one file at a time.

You can configure the following fields in the Backup CR to control the clean behavior:

* `.spec.cleanOption.pageSize`: Specifies the number of files to be deleted in each batch at a time. The default value is `10000`.
* `.spec.cleanOption.disableBatchConcurrency`: If the value of this field is `true`, TiDB Operator disables the concurrent batch deletion method and uses the concurrent deletion method.

    If your S3-compatible backend storage does not support the `DeleteObjects` API, the default concurrent batch deletion method fails. You need to configure this field to `true` to use the concurrent deletion method.

* `.spec.cleanOption.batchConcurrency`: Specifies the number of goroutines to start for the concurrent batch deletion method. The default value is `10`.
* `.spec.cleanOption.routineConcurrency`: Specifies the number of goroutines to start for the concurrent deletion method. The default value is `100`.
