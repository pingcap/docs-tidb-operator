---
title: Architecture of Backup and Restore Based on EBS Volume Snapshots
summary: Learn the architecture of backup and restore based on EBS volume snapshots in TiDB.
---

# Architecture of Backup and Restore Based on EBS Volume Snapshots

Backup and restore based on EBS volume snapshots is provided in TiDB Operator. This document describes the architecture and process of this feature by exemplifying backup and restore using TiDB Operator.

The architecture of backup and restore based on EBS volume snapshots is as follows:

![AWS EBS Snapshot Backup and Restore architecture](/media/volume-snapshot-backup-restore-overview.png)

## Back up TiDB cluster data by EBS volume snapshots

Workflow of EBS volume snapshot backup:

![EBS Snapshot backup process design](/media/volume-snapshot-backup-workflow.png)

1. The user submits a backup CRD.
   * TiDB Operator checks and collects information of volumes currently mounted to TiKV.
   * TiDB Operator creates a backup job using the volume information collected.

2. BR pauses the schedulers and GC.
   * **pause region scheduler**: BR requests TiDB to pause the schedulers.
   * **pause gc**: BR requests TiDB to pause GC.

3. BR retrieves `backupts`.
   * **retrieve backupts**: BR retrieves `backupts` of the backup data from TiDB.

4. BR creates volume snapshots.
   * **ec2 create snapshot**: BR requests AWS to create volume snapshots.

5. BR resumes the schedulers and GC, and waits for all EBS volume snapshots to be created.
   * **resume region scheduler**: BR requests TiDB to resume the schedulers.
   * **resume gc**: BR requests TiDB to resume GC.

6. BR saves the metadata to S3. The backup is complete.
   * **ec2 snapshot complete**: BR queries the snapshot status of all volumes from the AWS service and ensures that snapshots of all volumes reach the `Complete` state.
   * **save backupmeta to s3**: BR saves the backup metadata to S3.

## Restore EBS volume snapshots

Workflow of EBS volume snapshot restore:

![EBS Snapshot restore process design](/media/volume-snapshot-restore-workflow.png)

1. The user creates a TiDB cluster with `spec.recoveryMode:true` configured in the spec.
   * When a TiDB cluster is started in restore mode, the PD nodes are started and no TiKVs are started. The user is expected to create a restore job to continue the restore process.

2. The user creates a restore job.
   * **enter recovery mode**: BR configures the TiDB cluster to run in recovery mode.
   * **retrieve backupmeta from s3**: BR retrieves the backup metadata from S3 and then extracts the snapshot information and `backupts` of the backup data from backup metadata.
   * **create volume from snapshot**: BR invokes the AWS API to create volumes from the snapshots and returns the created volume information to TiDB Operator.

3. TiDB Operator configures the restored EBS volumes on the TiDB cluster and starts all TiKV nodes.
   * TiDB Operator configures Kubernetes and mounts the restored volumes to the corresponding nodes.
   * **config cluster and start tikv**: TiKV nodes start and enter the recovery mode. The raft state machine and related region state check operations are suspended.

4. TiDB Operator starts the BR restore sub-task, and obtains and restores the data of the TiDB cluster.
   * **raft log recovery**: BR reads the Region metadata from each TiKV, and selects the leader of each Region with the proper leader selection algorithm. Then Region leaders are assigned to campaign on TiKV, which triggers raft log alignment in the raft consensus layer.
   * **k-v data recovery**: BR uses `backupts` to restore data. For key-value data with version greater than `backupts`, BR deletes them to keep the cluster-level consistency of transaction data.
   * **exit recovery mode**: The TiDB cluster exits the restore mode and data restore is completed. BR returns `data complete` to TiDB Operator.

5. TiDB Operator starts the TiDB nodes of the TiDB cluster.
   * **start tidb**: TiDB Operator starts all TiDB nodes and the TiDB cluster is ready to serve.

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
