---
title: 基于 EBS 卷快照的备份恢复功能架构
summary: 了解 TiDB EBS 卷快照的备份恢复架构设计。
---

# 基于 EBS 卷快照的备份恢复功能架构

基于 EBS 卷快照的备份恢复功能以 TiDB Operator 为使用入口。本文以使用 TiDB Operator 进行备份恢复为例，介绍备份和恢复的功能架构和流程。

基于 EBS 卷快照的备份恢复功能架构如下：

![AWS EBS Snapshot Backup and Restore architecture](/media/volume-snapshot-backup-restore-overview.png)

## 备份 EBS 卷快照

EBS 卷快照备份流程如下：

![EBS Snapshot backup process design](/media/volume-snapshot-backup-workflow.png)

1. 用户提交备份 CRD
   * TiDB Operator 检查和收集当前集群 TiKV 已挂载卷信息。
   * TiDB Operator 使用挂载卷信息创建备份任务。

2. BR 暂停 TiDB 集群调度以及 GC
   * **pause region scheduler**：BR 向 TiDB Cluster 发起暂停调度请求。
   * **pause gc**：BR 向 TiDB Cluster 发起暂停 GC 请求。

3. BR 获取备份数据 backupts
   * **retrieve backupts**：BR 向 TiDB Cluster 获取 backupts。

4. BR 向 AWS 服务发起创建卷快照请求
   * **ec2 create snapshot**：BR 向 AWS 服务发起创建卷快照请求。

5. BR 恢复 TiDB 集群调度以及 GC，并等待所有的 EBS 卷的快照创建完成。
   * **resume region scheduler**：BR 向 TiDB Cluster 发起恢复调度请求。
   * **resume gc**：BR 请求 TiDB Cluster 恢复 GC。

6. BR 保存元数据信息到 S3 并退出。备份完成。
   * **ec2 snapshot complete**：BR 向 AWS 服务查询所有卷的快照状态，直到所有卷达到 Complete 状态。
   * **save backupmeta to s3**：BR 保存备份元数据到 S3。

## 恢复 EBS 卷快照

EBS 卷快照恢复流程如下：

![EBS Snapshot restore process design](/media/volume-snapshot-restore-workflow.png)

1. 用户以恢复模式创建 TiDB 集群，即在 Spec 中指定 `spec.recoveryMode:true`。
   * 恢复模式创建的 TiDB 集群，将会首先启动 PD 节点，不启动 TiKV 节点，同时等待用户创建恢复任务进行下一步恢复。

2. 用户创建恢复任务。
   * **enter recovery mode**：BR 设置 TiDB 集群为 recovery mode。
   * **retrieve backupmeta from s3**：BR 获取备份元数据信息，并从中提取已备份的快照以及 backupts。
   * **create volume from snapshot**：BR 调用 AWS API，从备份快照创建卷，并返回给 TiDB Operator。

3. TiDB Operator 使用恢复的 EBS 卷配置 TiDB 集群，同时启动所有的 TiKV 节点。
   * TiDB Operator 配置 Kubernetes，并挂载恢复的卷到相应的节点。
   * **config cluster and start tikv**：配置完成后，启动 TiKV 节点。TiKV 进入 recovery mode，等待下一步的数据恢复。在 recovery mode 下，raft 状态机以及相关的状态检查操作被停止。

4. TiDB Operator 启动 BR 数据恢复子任务，获取并恢复 TiDB Cluster 数据。
   * **raft log recovery**：BR 读取集群的 region meta, 汇总计算决策出每个 region 的 leader，让 leader 在 TiKV 上主动发起竞选来启动 raft 共识层的日志恢复。
   * **k-v data recovery**：BR 使用备份的 `backupts` 进行数据恢复。BR 删除数据版本大于 `backupts` 的 key-value 数据，从而确保事务数据集群级别的一致性。
   * **exit recovery mode**：TiDB 集群退出恢复模式，数据恢复完成。BR 返回给 TiDB Operator `data complete`。

5. TiDB Operator 启动 TiDB Cluster 的 TiDB 节点，整个恢复任务完成。
   * **start tidb**：TiDB Operator 启动 TiDB Cluster 的所有 TiDB 节点，集群对外提供服务。

### 备份元数据信息

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

具体示例如下

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

> **注意：**
>
> 示例中，`resolved_ts` 是 backupts 的实现。为实现上的方便，在代码中我们使用 `resolved_ts`。