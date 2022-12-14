---
title: Performance of EBS Snapshot Backup and Restore
summary: Learn about the performance of EBS snapshot backup and restore.
---

# Performance of EBS Snapshot Backup and Restore

This document describes the performance of EBS snapshot backup and restore, the factors that affect performance, and the performance test results. The performance metrics are based on the AWS region `us-west-2`.

## Backup performance

This section introduces the performance of EBS snapshot backup using volumes, the factors that affect performance, and the performance test results. Backup performance is scalable and increases linearly with the number of TiKV nodes.

### Backup time consumption

EBS snapshot backup using volumes consists of the following processes: creates a backup task, stops scheduling, stops GC, and obtains the backupts and volume snapshots. For more detailed information about these processes, see [Architecture of EBS snapshot volume backup and restore](backup-restore-overview.md). Among these processes, creating a volume snapshot consumes most of the time. Volume snapshots are created in parallel and the time taken to complete a backup task depends on when the last volume snapshot is backed up.

### Time consumption ratio of backup

| Backup stage     | Time taken    | Total ratio | Remarks                                     |
| :--------: | :---------: | :------: | :-------------------------------------: |
| Volume snapshot creation  | 16 m (50GB) | %99      | Time for AWS EBS snapshots                  |
| Others        | 1s          | %1       | Including the time for stopping scheduling, stopping GC, and obtaining the backupts |

### Backup performance data

Time taken by snapshot backup using volumes depends on when the last volume snapshot is backed up, which is done by AWS EBS. For now, AWS does not provide quantitative metrics for volume snapshot backup. The time taken by the entire backup process is as follows under the recommended machine type and GP3 storage volume, with the configuration of 400 MiB/s and 7000 IOPS:

![EBS Snapshot backup perf](/media/volume-snapshot-backup-perf.png)

| Data of a volume  | Volume size  | Volume configuration             | Appropriate backup duration |
| :------: | :-----: | :---------------: | :--------: |
| 50 GB    | 500 GB  | 7000IOPS/400MiB/s | 20 min    |
| 100 GB   | 500 GB  | 7000IOPS/400MiB/s | 50 min    |
| 200 GB   | 500 GB  | 7000IOPS/400MiB/s | 100 min   |
| 500 GB   | 1024 GB | 7000IOPS/400MiB/s | 150 min   |
| 1024 GB  | 3500 GB | 7000IOPS/400MiB/s | 350 min   |

> **Note:**
>
> The preceding performance data is based on full data backup.
>
> AWS EBS snapshot backup is performed on the per volume basis. Only the first volume snapshot is full, and the subsequent volume snapshots are incremental. You can complete a daily backup within about 1 hour. In special scenarios, you can shorten the backup interval, for example, 12 hours or 8 hours.

### Backup impact

It is tested that the backup impact on clusters in less than 3% when GP3 volumes are used. In the following figure, the backup is initiated after 10:25.

![EBS Snapshot backup impact](/media/volume-snapshot-backup-impact.jpg)

## Restore performance

This document describes the performance of EBS snapshot restore using volumes, the factors that affect performance, and the performance test results.

### Restore time consumption

EBS snapshot restore using volumes consists of the following processes. For detailed information, see [Architecture of EBS snapshot volume backup and restore](backup-restore-overview.md).

1. Create a cluster.

    TiDB Operator creates a cluster in recoveryMode and starts all PD nodes.

2. Restore volumes.

    TiDB Operator creates volume restore subtasks using BR. BR restores the data volumes from the snapshots to start TiKV.

3. Start TiKV.

    TiDB Operator mounts the TiKV volumes and starts TiKV.

4. Restores data.

    TiDB Operator creates volume data restore subtasks. BR restores the data volumes to a consistent state.

5. Start TiDB.

    TiDB is started and the restore is completed.

### Time consumption ratio of restore

| Restore stage     | Appropriate time taken | Restore ratio | Remarks                                                            |
| :--------: | :---------: | :------: | :-------------------------------------------------------------: |
| Creates clusters     | 30 s         | %1       | Including the time for downloading docker image and starting PD                                   |
| Restores volumes     | 20 s         | %1       | Including the time for starting the BR Pod and restoring volumes                                         |
| Starts TiKV   | 2～30 min    | 58%      | If there are ongoing transactions during backup, rocksDB consumes extra 5-30 minutes to start during restore |
| Restores data | 2～20 min    | 38%       |   Including the time for restoring data in the raft consensus layer and deleting MVCC data                    |
| Starts TiDB   | 1 min        | 2%       |  Including the time for download the TiDB docker image and starting TiDB                     |

> **Note:**
>
> Volume snapshots are consistent upon crash. Before TiKV starts, you need to start rocksDB first. If there is newly written data, the time taken in starting TiKV is longer. It is tested that the extra time is less than 30 minutes. If you use high-performance volumes, such as io2, the extra time can be shortened to 5 minutes. If you use standard GP3 volumes (3000 IOPS/125 MiB/s), the extra time may reach 30 minutes.

### Restore performance data

The duration of volume snapshot restore depends on the time taken by TiKV to start and data restore. TiKV can be started in 2 to 30 minutes, considering the impact of initialization delay of EBS volume snapshot restore. Data restore is completed by AWS EBS. Currently, AWS does not provide quantitative metrics. The time taken by the entire restore process is as follows under the recommended machine type and GP3 storage volume:

![EBS Snapshot restore perf](/media/volume-snapshot-restore-perf.png)

| Data of a volume  | Volume size   | Volume configuration             | Appropriate restore duration |
| :------: | :-----: | :---------------: | :--------: |
| 50 GB    | 500 GB  | 7000IOPS/400MiB/s | 16 min    |
| 100 GB   | 500 GB  | 7000IOPS/400MiB/s | 18 min    |
| 200 GB   | 500 GB  | 7000IOPS/400MiB/s | 21 min   |
| 500 GB   | 1024 GB | 7000IOPS/400MiB/s | 25 min   |
| 1024 GB  | 3500 GB | 7000IOPS/400MiB/s | 34 min   |

> **Note:**
>
> The preceding performance data is for reference only. The actual performance may vary.
