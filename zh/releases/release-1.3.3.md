---
title: TiDB Operator 1.3.3 Release Notes
---

# TiDB Operator 1.3.3 Release Notes

发布日期: 2022 年 5 月 16 日

TiDB Operator 版本：1.3.3

## 新功能

- 添加新的 `spec.tidb.service.port` 字段，以支持配置 tidb 服务端口 ([#4512](https://github.com/pingcap/tidb-operator/pull/4512), [@KanShiori](https://github.com/KanShiori))

## Bug 修复

- 修复集群升级过程中，evict leader scheduler 可能泄漏的问题 ([#4522](https://github.com/pingcap/tidb-operator/pull/4522), [@KanShiori](https://github.com/KanShiori))

- 更新 `tidb-backup-manager` 镜像的基础镜像，以修复不兼容 ARM 架构的问题 ([#4490](https://github.com/pingcap/tidb-operator/pull/4490), [@better0332](https://github.com/better0332))

- 修复当 tidb Service 没有 Endpoint 时，operator 可能会 panic 的问题 ([#4500](https://github.com/pingcap/tidb-operator/pull/4500), [@mikechengwei](https://github.com/mikechengwei))

- 修复 Kubernetes 集群访问失败并重试后，组件 Pod 的 Labels 和 Annotations 可能丢失的问题 ([#4498](https://github.com/pingcap/tidb-operator/pull/4498), [@duduainankai](https://github.com/duduainankai))