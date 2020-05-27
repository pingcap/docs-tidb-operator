---
title: What's New in v1.1
category: how-to
---

# What's New in v1.1

TiDB Operator 1.1 在 1.0 基础上新增了许多功能，支持 TiDB 4.0 以及 TiFlash、TiCDC 新组件。同时在易用性上做了许多改进，提供与 Kubernetes 原生资源一致的用户体验。以下是主要特性：

## TidbCluster

- TidbCluster CR 支持部署管理 PD discovery 组件，可完全替代 tidb-cluster chart
- 管理 TiDB 集群
- 新增 Pump、TiFlash、TiCDC 支持
- 新增 PD Dashboard  支持
- 全面支持 TiDB 组件及客户端 TLS 证书配置

## 新增 CRD

- 新增 `TidbMonitor` 用于部署集群监控
- 新增 `TidbInitializer` 用于初始化集群
- 新增 `Backup`、`BackupSchedule`、`Restore` 用于备份恢复集群
- 新增 `TidbClusterAutoScaler` 实现[集群自动伸缩功能](enable-tidb-cluster-auto-scaling.md) (开启 `AutoScaling` 特性开关后使用)

## 其他

- 新增可选的[准入控制器](enable-admission-webhook.md)改进升级、扩缩容体验，并提供灰度发布功能
- 新增可选的[增强型 StatefulSet 控制器](advanced-statefulset.md)，提供对指定 Pod 进行删除的功能 (开启 `AdvancedStatefulSet` 特性开关后使用)
- `tidb-scheduler` 支持任意维度的 HA 调度和 Preemption 支持
- 备份、恢复支持 S3 和 GCS

完成发布日志参见 [1.1 CHANGE LOG](https://github.com/pingcap/tidb-operator/blob/master/CHANGELOG-1.1.md) 。
TiDB Operator 在 Kubernetes 上部署参见[安装文档](#deploy-tidb-operator.md)，CRD 文档参见 [API References](#api-references.md) 。
