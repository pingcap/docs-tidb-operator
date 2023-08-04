---
title: TiDB Operator v1.5 新特性
Summary: 了解 TiDB Operator 1.5.0 版本引入的新特性。
---

# TiDB Operator v1.5 新特性

TiDB Operator v1.5 引入了以下关键特性，从扩展性、易用性等方面帮助你更轻松地管理 TiDB 集群及其周边工具。

## 兼容性改动

如需使用在 [#4959](https://github.com/pingcap/tidb-operator/pull/4959) 中引入的 `PreferDualStack` 特性（通过 `spec.preferIPv6: true` 启用），Kubernetes 版本需要大于等于 v1.20。

## 滚动升级改动

由于 [#5075](https://github.com/pingcap/tidb-operator/pull/5075) 的改动，如果 TiDB v7.1.0 或以上版本的集群中部署了 TiFlash，升级 TiDB Operator 到 v1.5.0 之后 TiFlash 组件会滚动升级。

## 扩展性

- 支持通过 `bootstrapSQLConfigMapName` 字段指定 TiDB 首次启动时所执行的初始 SQL 文件。
- 支持通过配置 `spec.preferIPv6: true` 为所有组件的 Service 的 `ipFamilyPolicy` 配置 `PreferDualStack`。
- 支持使用 [Advanced StatefulSet](advanced-statefulset.md) 管理 TiCDC 和 TiProxy。
- 新增 BR Federation Manager 组件，支持对跨多个 Kubernetes 部署的 TiDB 集群进行基于 EBS snapshot 的备份恢复。

## 易用性

- 支持通过为 PD Pod 加上 `tidb.pingcap.com/pd-transfer-leader` annotation 来优雅重启 PD Pod。
- 支持通过为 TiDB Pod 加上 `tidb.pingcap.com/tidb-graceful-shutdown` annotation 来优雅重启 TiDB Pod。
- 允许用户自定义策略来重启失败的备份任务，以提高备份的稳定性。
- 添加与 reconciler 和 worker queue 相关的监控指标以提高可观测性。
- 添加统计协调流程失败计数的监控指标以提高可观测性。
