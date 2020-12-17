---
title: TiDB Operator 1.1.8 Release Notes
---

# TiDB Operator 1.1.8 Release Notes

发布日期：2020 年 12 月 18 日

TiDB Operator 版本：1.1.8

## 新功能

- 支持为 `PD`、`TiDB`、`TiKV`、`TiFlash`、`Backup` 和 `Restore` 指定任意 Volume 和 VolumeMount，用户可以利用该功能实现基于 NFS 或者任意 Kubernetes 支持的 Volume 类型的备份和恢复任务。([#3517](https://github.com/pingcap/tidb-operator/pull/3517), [@dragonly](https://github.com/dragonly))

## 优化提升

- 支持在 `tidb-lightning` 和 `tikv-importer` helm charts 中为 TiDB 组件和客户端开启 TLS 的功能。([#3598](https://github.com/pingcap/tidb-operator/pull/3598), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TiDB service 指定额外的端口。用户可以利用该功能实现自定义服务，如额外的健康检查机制。([#3599](https://github.com/pingcap/tidb-operator/pull/3599), [@handlerww](https://github.com/handlerww))
- 支持在 `TidbInitializer` 连接 TiDB server 时不使用 TLS。([#3564](https://github.com/pingcap/tidb-operator/pull/3564), [@LinuxGit](https://github.com/LinuxGit))
- 支持 TiDB-Lightning 恢复数据时使用 tableFilters 进行过滤。([#3521](https://github.com/pingcap/tidb-operator/pull/3521), [@sstubbs](https://github.com/sstubbs))

## Bug 修复

- 修复当配置了 `spec.tikv.storageVolumes` 时，无法部署 TiDB 集群的问题。([#3586](https://github.com/pingcap/tidb-operator/pull/3586), [@mikechengwei](https://github.com/mikechengwei))
- 修复在 `TidbInitializer` 任务中使用包含非 ASCII 字符密码时的编码错误。([#3569](https://github.com/pingcap/tidb-operator/pull/3569), [@handlerww](https://github.com/handlerww))
- 修复 TiFlash pods 会被误认为 TiKV pods 的问题。该问题会导致当同一个 `TidbCluster` 中部署了 TiFlash 实例时，TiDB Operator 可能将 TiKV 实例缩容到小于 `tikv.replicas` 的数字。([#3514](https://github.com/pingcap/tidb-operator/pull/3514), [@handlerww](https://github.com/handlerww))
- 修复在开启 TiDB 客户端 TLS 功能的情况下，同步 `Backup` CR 会导致 `tidb-controller-manager` pod 崩溃的问题。([#3535](https://github.com/pingcap/tidb-operator/pull/3535), [@dragonly](https://github.com/dragonly))
