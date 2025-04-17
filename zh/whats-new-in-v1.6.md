---
title: TiDB Operator v1.6 新特性
summary: 了解 TiDB Operator 1.6.0 版本引入的新特性。
---

# TiDB Operator v1.6 新特性

TiDB Operator v1.6 引入了以下关键特性，从扩展性、易用性等方面帮助你更轻松地管理 TiDB 集群及其周边工具。

## 兼容性改动

- 升级 Kubernetes 依赖库至 v1.28 版本，建议不再部署 `tidb-scheduler` 组件。
- 当通过 Helm Chart 部署时，支持设置 `tidb-controller-manager` 用于 leader 选举的 lock resource，默认值为 `.Values.controllerManager.leaderResourceLock: leases`。当从之前的版本升级到 v1.6.0-beta.1 或之后的版本时，推荐先设置 `.Values.controllerManager.leaderResourceLock: endpointsleases`，等待新的 `tidb-controller-manager` 正常运行后再设置 `.Values.controllerManager.leaderResourceLock: leases` 以更新部署。

## 扩展性

- 支持以[微服务模式](https://docs.pingcap.com/zh/tidb/dev/pd-microservices)部署 PD v8.0.0 及以上版本（实验特性）。
- 支持对 TiDB 组件进行并行的扩容与缩容操作。

## 易用性

- 支持自动为 TiProxy 设置 location labels。
- 支持为 TiDB 集群各组件的 `topologySpreadConstraints` 设置 `maxSkew`、`minDomains` 与 `nodeAffinityPolicy`。
- 支持为 TiDB 组件设置 `startupProbe`。
- 支持为 TiDB 组件设置额外的命令行参数。
- 支持为 Discovery 组件设置 `livenessProbe` 与 `readinessProbe`。
- 支持为 TidbInitializer 组件设置 `nodeSelector`。
- 支持为 TiFlash 直接挂载 ConfigMap 而不再依赖 InitContainer 对配置文件进行处理。
