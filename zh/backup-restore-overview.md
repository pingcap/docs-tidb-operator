---
title: 备份与恢复简介
summary: 介绍如何使用 BR、Dumpling、TiDB Lightning 工具对 Kubernetes 上的 TiDB 集群进行数据备份和数据恢复。
---

# 备份与恢复简介

本文档介绍如何对 Kubernetes 上的 TiDB 集群进行数据备份和数据恢复。备份与恢复中所使用的工具有 [Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview)、[TiDB Lightning](https://docs.pingcap.com/zh/tidb/stable/get-started-with-tidb-lightning) 和 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool)。

[Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview) 是一个数据导出工具，该工具可以把存储在 TiDB/MySQL 中的数据导出为 SQL 或者 CSV 格式，可以用于完成逻辑上的全量备份或者导出。

[TiDB Lightning](https://docs.pingcap.com/zh/tidb/stable/get-started-with-tidb-lightning) 是一个数据导入工具，该工具可以把 Dumpling 或 CSV 输出格式的数据快速导入到 TiDB 中，可以用于完成逻辑上的全量恢复或者导入。

[BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。相比 Dumpling 和 Mydumper，BR 更适合大数据量的场景，BR 只支持 TiDB v3.1 及以上版本。如果需要对延迟不敏感的增量备份，请参阅 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool)。如果需要实时的增量备份，请参阅 [TiCDC](https://docs.pingcap.com/zh/tidb/stable/ticdc-overview)。

## 使用场景

### 数据备份

如果你对数据备份有以下要求，可考虑使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 对 TiDB 进行数据备份：

- 备份的数据量较大，而且要求备份速度较快
- 直接备份数据的 SST 文件（键值对）
- 对延迟不敏感的增量备份

BR 相关使用文档可参考：

- [使用 BR 备份 TiDB 集群到兼容 S3 的存储](backup-to-aws-s3-using-br.md)
- [使用 BR 备份 TiDB 集群到 GCS](backup-to-gcs-using-br.md)
- [使用 BR 备份 TiDB 集群到持久卷](backup-to-pv-using-br.md)

如果你对数据备份有以下要求，可考虑使用 [Dumpling](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview) 对 TiDB 进行数据备份：

- 导出 SQL 或 CSV 格式的数据
- 对单条 SQL 语句的内存进行限制
- 导出 TiDB 的历史数据快照

Dumpling 相关使用文档可参考：

- [使用 Dumpling 备份 TiDB 集群数据到兼容 S3 的存储](backup-to-s3.md)
- [使用 Dumpling 备份 TiDB 集群数据到 GCS](backup-to-gcs.md)

### 数据恢复

如果你需要从由 BR 备份出的 SST 文件对 TiDB 进行数据恢复，则应使用 BR。相关使用文档可参考：

- [使用 BR 恢复兼容 S3 的存储上的备份数据](restore-from-aws-s3-using-br.md)
- [使用 BR 恢复 GCS 上的备份数据](restore-from-gcs-using-br.md)
- [使用 BR 恢复持久卷上的备份数据](restore-from-pv-using-br.md)

如果你需要从由 Dumpling 导出的或其他格式兼容的 SQL 或 CSV 文件对 TiDB 进行数据恢复，则应使用 TiDB Lightning。相关使用文档可参考：

- [使用 TiDB Lightning 恢复兼容 S3 的存储上的备份数据](restore-from-s3.md)
- [使用 TiDB Lightning 恢复 GCS 上的备份数据](restore-from-gcs.md)

## 备份与恢复过程

为了对 Kubernetes 上的 TiDB 集群进行数据备份，用户需要创建一个自定义的 [`Backup` Custom Resource](backup-restore-cr.md#backup-cr-字段介绍) (CR) 对象来描述一次备份，或者创建一个自定义的 [`BackupSchedule` CR](backup-restore-cr.md#backupschedule-cr-字段介绍) 对象来描述一个定时备份。

为了对 Kubernetes 上的 TiDB 集群进行数据恢复，用户可以通过创建一个自定义的 [`Restore` CR](backup-restore-cr.md#restore-cr-字段介绍) 对象来描述一次恢复。

在创建完对应的 CR 对象后，TiDB Operator 将根据相应配置并选择对应的工具执行备份或恢复。

## 删除备份的 Backup CR

用户可以通过下述语句来删除对应的备份 CR 或定时全量备份 CR。

{{< copyable "shell-regular" >}}

```shell
kubectl delete backup ${name} -n ${namespace}
kubectl delete backupschedule ${name} -n ${namespace}
```

如果你使用 v1.1.2 及以前版本，或使用 v1.1.3 及以后版本并将 `spec.cleanPolicy` 设置为 `Delete` 时，TiDB Operator 在删除 CR 时会同时清理备份文件。

在满足上述条件时，如果需要删除 namespace，建议首先删除所有的 Backup/BackupSchedule CR，再删除 namespace。

如果直接删除存在 Backup/BackupSchedule CR 的 namespace，TiDB Operator 会持续尝试创建 Job 清理备份的数据，但因为 namespace 处于 `Terminating` 状态而创建失败，从而导致 namespace 卡在该状态。

这时需要通过下述命令删除 `finalizers`：

{{< copyable "shell-regular" >}}

```shell
kubectl patch -n ${namespace} backup ${name} --type merge -p '{"metadata":{"finalizers":[]}}'
```

### 清理备份文件

TiDB Operator v1.2.3 及之前的版本，清理备份文件的方式为：循环删除备份文件，一次删除一个文件。

TiDB Operator v1.2.4 及以后的版本，清理备份文件的方式为：循环删除备份文件，一次批量删除多个文件。对于每次批量删除多个文件的操作，根据备份使用的后端存储类型的不同，删除方式不同。

* S3 兼容的后端存储采用并发批量删除方式。TiDB Operator 启动多个 Go 协程，每个 Go 协程每次调用批量删除接口 ["DeleteObjects"](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObjects.html) 来删除多个文件。
* 其他类型的后端存储采用并发删除方式。TiDB Operator 启动多个 Go 协程，每个 Go 协程每次删除一个文件。

对于 TiDB Operator v1.2.4 及以后的版本，你可以使用 Backup CR 中的以下字段控制清理行为：

* `.spec.cleanOption.pageSize`：指定每次批量删除的文件数量。默认值为 10000。
* `.spec.cleanOption.disableBatchConcurrency`：当设置为 true 时，TiDB Operator 会禁用并发批量删除方式，使用并发删除方式。

    如果 S3 兼容的后端存储不支持 `DeleteObjects` 接口，默认的并发批量删除会失败，需要配置该字段为 `true` 来使用并发删除方式。

* `.spec.cleanOption.batchConcurrency`: 指定并发批量删除方式下启动的 Go 协程数量。默认值为 10。
* `.spec.cleanOption.routineConcurrency`: 指定并发删除方式下启动的 Go 协程数量。默认值为 100。
