---
title: Performance of EBS Snapshot Backup and Restore
summary: Learn about the performance of EBS snapshot backup and restore.
---

# Performance of EBS Snapshot Backup and Restore

This document describes the performance of EBS snapshot backup and restore, the factors that affect performance, and the performance test results. The performance metrics are based on the AWS region `us-west-2`.

> **Note:**
>
> The preceding performance data is for reference only. The actual performance may vary.

## Backup performance

This section introduces the performance of EBS snapshot backup using volumes, the factors that affect performance, and the performance test results.

### Backup time consumption

EBS snapshot backup using volumes consists of the following processes: creates a backup task, stops scheduling, disables GC, and obtains the backupts and volume snapshots. For more detailed information about these processes, see [Architecture of EBS snapshot volume backup and restore](volume-snapshot-backup-restore.md). Among these processes, creating a volume snapshot consumes most of the time. Volume snapshots are created in parallel, and the time taken to complete the entire backup task depends on when the most time-consuming volume is created.

### Time consumption ratio of backup

| Backup stage     | Time taken    | Total ratio | Remarks                                     |
| :--------: | :---------: | :------: | :-------------------------------------: |
| Create volume snapshots  | 16 m (50 GB) | 99%      | Including the time for creating AWS EBS snapshots                  |
| Others        | 1s          | 1%       | Including the time for stopping scheduling, disabling GC, and obtaining the backupts |

### Backup performance data

Time taken by snapshot backup using volumes depends on when the last volume snapshot is backed up, which is done by AWS EBS. For now, AWS does not provide quantitative metrics for volume snapshot backup. The time taken by the entire backup process is as follows under the recommended machine type and GP3 storage volume, with the configuration of 400 MiB/s and 7000 IOPS:

![EBS Snapshot backup perf](/media/volume-snapshot-backup-perf.png)

| Volume data  | Total volume size  | Volume configuration             | Appropriate backup duration |
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

EBS snapshot restore using volumes consists of the following processes. For detailed information, see [Architecture of EBS snapshot volume backup and restore](volume-snapshot-backup-restore.md).

1. Create a cluster.

    TiDB Operator creates a cluster in recoveryMode and starts all PD nodes.

2. Restore volumes.

    TiDB Operator creates volume restore subtasks using BR. BR restores the data volumes from the snapshots to start TiKV.

3. Start TiKV.

    TiDB Operator mounts the TiKV volumes and starts TiKV.

4. Restore data.

    TiDB Operator creates volume data restore subtasks. BR restores the data volumes to a consistent state.

5. Start TiDB.

    TiDB is started and the restore is completed.

### Time consumption ratio of restore

| Restore stage     | Appropriate time taken | Restore ratio | Remarks                                                            |
| :--------: | :---------: | :------: | :-------------------------------------------------------------: |
| Creates clusters     | 30s         |  1%      | Including the time for downloading docker image and starting PD                                   |
| Restores volumes     | 20s         |  1%     | Including the time for starting the BR Pod and restoring volumes                                         |
| Starts TiKV   | 2 to 30 min    | 58%      | The time taken to start TiKV is affected by volume performance and usually takes about 3 minutes. When the task restores backup data that contains trasactions, it might take up to 30 minutes to start TiKV. |
| Restores data | 2 to 20 min    | 38%       |  Including the time for restoring data in the raft consensus layer and deleting MVCC data                                 |
| Starts TiDB   | 1 min        | 2%       |  Including the time for downloading the tidb docker image and starting TiDB                                           |
| Starts TiKV   | 2～30 min    | 58%      | If there are ongoing transactions during backup, rocksDB consumes extra 5-30 minutes to start during restore |
| Restores data | 2～20 min    | 38%       |   Including the time for restoring data in the raft consensus layer and deleting MVCC data                    |
| Starts TiDB   | 1 min        | 2%       |  Including the time for download the TiDB docker image and starting TiDB                     |

> **Note:**
>
> Volume snapshots are consistent upon crash. During restore, before TiKV starts, data self-check and repair are performed, which might take less than 30 minutes. If you restore using high-performance disks that can increase the IOPS and bandwidth, the time can be shortened to 5 minutes. For details about how to use high-performance disks, see [Restore period is excessively long (longer than 2 hours)](backup-restore-faq.md#restore-period-is-excessively-long-longer-than-2-hours).

### Restore performance data

The duration of volume snapshot restore depends on the time taken to start TiKV and that for data restore. Time taken to start TiKV might be affected by lazy initialization of EBS volume snapshot restore, for which AWS does not provide quantitative metrics. Test data is as follows under the recommended machine type and GP3 storage volume:

![EBS Snapshot restore perf](/media/volume-snapshot-restore-perf.png)

| Volume data  | Total volume size   | Volume configuration             | Appropriate restore duration |
| :------: | :-----: | :---------------: | :--------: |
| 50 GB    | 500 GB  | 7000IOPS/400MiB/s | 16 min    |
| 100 GB   | 500 GB  | 7000IOPS/400MiB/s | 18 min    |
| 200 GB   | 500 GB  | 7000IOPS/400MiB/s | 21 min   |
| 500 GB   | 1024 GB | 7000IOPS/400MiB/s | 25 min   |
| 1024 GB  | 3500 GB | 7000IOPS/400MiB/s | 34 min   |
