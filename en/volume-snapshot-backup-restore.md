---
title: Architecture of Backup and Restore Based on EBS Volume Snapshots
summary: Learn the architecture of backup and restore based on EBS volume snapshots in TiDB.
---

# Architecture of Backup and Restore Based on EBS Volume Snapshots

Backup and restore based on EBS volume snapshots is provided in TiDB Operator. This document describes the architecture and process of this feature by exemplifying backup and restore using TiDB Operator.

The architecture of backup and restore based on EBS volume snapshots is as follows:

![AWS EBS Snapshot Backup and Restore architecture](/media/volume-snapshot-backup-restore-overview.png)

## Back up EBS volume snapshots

Process of EBS volume snapshot backup:

![EBS Snapshot backup process design](/media/volume-snapshot-backup-workflow.png)

1. (The user) submits a backup CRD.
   * TiDB Operator checks and collects information of volumes currently mounted to TiKV.
   * TiDB Operator creates a backup job using the volume information collected.

2. Pauses scheduling and GC.
   * **pause region scheduler**: BR requests TiDB to pause scheduling.
   * **pause gc**: BR requests TiDB to pause GC.

3. Obtains `backupts`.
   * **retrieve backupts**: BR requests `backupts` of the backup data from TiDB.

4. Creates volume snapshots.
   * **ec2 create snapshot**: BR requests AWS to create volume snapshots.

5. Resumes scheduling and GC, and waits for all EBS volume snapshots to be created.
   * **resume region scheduler**: BR requests TiDB to resume scheduling.
   * **resume gc**: BR requests TiDB to resume GC.

6. Saves the metadata to S3. The backup is complete.
   * **ec2 snapshot complete**: BR queries the snapshot status of all volumes from the AWS service and ensures that snapshots of all volumes reach the `Complete` state.
   * **save backupmeta to s3**: BR saves the backup metadata to S3.

## Restore EBS volume snapshots

Process of EBS volume snapshot restore:

![EBS Snapshot restore process design](/media/volume-snapshot-restore-workflow.png)

1. (The user) creates a TiDB cluster with `spec.recoveryMode:true` specified.
   * A TiDB cluster in restore mode is created. The PD node is started first. The user is expected to create a restore job to continue the restore process.

2. The user creates a restore job.
   * **enter recovery mode**: BR configures the TiDB cluster to run in recovery mode.
   * **retrieve bakcupmeta from s3**: BR retrieves the backup metadata from S3 and extracts the snapshot information and `backupts` of the backup data.
   * **create volume from snapshot**: BR calls the AWS API to create volumes from the backup snapshots and returns the volume information to TiDB Operator.

3. TiDB Operator configures the EBS volumes for restore on the TiDB cluster and starts all TiKV nodes.
   * TiDB Operator configures Kubernetes and mounts the restored volumes to the corresponding nodes.
   * **config cluster and start tikv**: TiKV nodes start after the configuration and enter the recovery mode. The raft state machine and related state check operations are suspended.

4. TiDB Operator starts the BR restore sub-task, and obtains and restores the data of the TiDB cluster.
   * **raft log recovery**: BR reads the region metadata of the cluster, and selects the leader of each region after calculation. Then the candidate region leaders compete for the leader on TiKV, which triggers log restore in the raft consensus layer.
   * **k-v data recovery**: BR uses `backupts` to restore data. For key-value data with version greater than `backupts`, BR deletes them to keep the global consistency of transaction data.
   * **exit recovery mode**: The TiDB cluster exits the restore mode and data restore is completed. BR returns `data complete` to TiDB Operator.

5. TiDB Operator starts the TiDB nodes of the TiDB cluster.
   * **start tidb**: TiDB Operator starts all TiDB nodes and the TiDB cluster resumes services.

### Backup metadata

```
.
├── backupmeta
│   ├── cluster-info
│   │   ├── version
│   │   ├── backup_type
│   │   ├── resolved_ts
│   ├── store_volumes
│   │   ├── volume_id
│   │   ├── volume_type
│   │   ├── snapshot_id
│   │   ├── volume_az
│   ├── kubernetes
│   │   ├── pvcs
│   │   ├── crd
```

The following is an example:

```json
{
    "cluster_info": {
        "cluster_version": "6.3.0-alpha",
        "full_backup_type": "aws-ebs",
        "resolved_ts": 436732770870624257,
    },
    "tikv": {
        "replicas": 1,
        "stores": [
            {
                "store_id": 1,
                "volumes": [
                    {
                        "volume_id": "vol-0bedb7ec0993f8a41",
                        "type": "raft-engine.dir",
                        "snapshot_id": "snap-074769e94078a89b7",
                        "volume_az": "us-west-2a",
                    },
                    {
                        "volume_id": "vol-08b303894657288a9",
                        "type": "storage.data-dir",
                        "snapshot_id": "snap-07b969994a363fdab",
                        "volume_az": "us-west-2a",
                    }
                ]
            },
        ]
    },
    "kubernetes": {
        "pvs": [
        ],
        "pvcs": [
        ],
        "crd_tidb_cluster": {
        },
    },
}
```

> **Note:**
>
> In the preceding example, `resolved_ts` is the implementation of `backupts` and is used in code for convenience.
