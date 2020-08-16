---
title: 聚合多个TiDB集群的监控数据
summary: 通过 Thanos 框架聚合多个TiDB集群的监控数据
aliases: ['/docs-cn/tidb-in-kubernetes/dev/aggregate-multiple-cluster-monitor-data/']
---

# 聚合多个TiDB集群的监控数据

本文档介绍如果通过 Thanos 聚合多个 TiDB 集群的监控数据,解决多集群下监控数据的中心化问题

## Thanos 介绍

Thanos 是 Prometheus 高可用的解决方案，用于简化 Prometheus 的可用性保证。 具体请参考:[`Thanos官方文档`](https://thanos.io/design.md/)

Thanos 提供了跨 Prometheus 的统一查询方案 [Thanos Query](https://thanos.io/components/query.md/) 组件，我们可以利用这个功能解决 TiDB 多集群监控数据未中心化的问题。

## 配置Thanos Query

首先我们需要为每个 TiDBMonitor 安装一个 Thanos Sidecar 容器。请参考 examples [示例](https://github.com/pingcap/tidb-operator/tree/master/examples/monitor-with-thanos/README.md),更新自己的TiDBMonitor。
Thanos Sidecar 安装好之后,我们会安装 Thanos Query 容器。在 Thanos Query 中，一个Prometheus 对应一个Store,也就对应一个TiDBMonitor。部署完Thanos Query，我们就可以通过Thanos Query的API 提供监控数据的统一查询接口。


## 配置 Grafana
安装完 Thanos Query , grafana 只需要将 DataSource 更改成 Thanos 源，就可以查询到多个TiDBMonitor的监控数据。

## 增加或者减少TiDBMonitor
当需要更新或者下线 TiDBMonitor 时，我们需要将 Thanos Query Store 配置 更新并重启。



