---
title: TiDB Operator 架构
summary: 了解 TiDB Operator 架构及其工作原理。
---

# TiDB Operator 架构

本文档介绍 TiDB Operator 的架构及其工作原理。

## 架构

下图是 TiDB Operator 的架构概览。

![TiDB Operator Architecture](/media/tidb-operator-architecture.png)

图中包含多个由 [Custom Resource Definition (CRD)](https://kubernetes.io/zh-cn/docs/concepts/extend-kubernetes/api-extension/custom-resources/) 定义的资源对象，例如 `Cluster`、`PDGroup`、`PD`、`TiKVGroup`、`TiKV`、`TiDBGroup`、`TiDB`、`Backup`、`Restore` 等。部分资源的说明如下：

- `Cluster`：表示一个完整的 TiDB 集群，它包含了 TiDB 集群的一些通用配置和功能开关，并反映集群的整体状态。该 CRD 被设计为 TiDB 集群的“命名空间”，TiDB 集群的所有组件都必须引用一个 `Cluster` CR。
- `ComponentGroup`：用于描述一组具有相同配置的 TiDB 集群组件，例如：

    - `PDGroup` 表示一组具有相同配置的 PD 实例
    - `TiKVGroup` 表示一组具有相同配置的 TiKV 实例
    - `TiDBGroup` 表示一组具有相同配置的 TiDB 实例

- `Component`：用于描述一个 TiDB 集群组件，例如：

    - `PD` 表示一个 PD 实例
    - `TiKV` 表示一个 TiKV 实例
    - `TiDB` 表示一个 TiKV 实例

- `Backup`：用于描述用户期望执行的 TiDB 集群备份任务。
- `Restore`：用于描述用户期望执行的 TiDB 集群恢复任务。

## 流程解析

TiDB Operator 采用声明式 API，通过监控用户定义的资源对象实现自动化控制。其核心流程如下：

1. 用户通过 `kubectl` 创建 `Cluster` 以及其他组件的自定义资源 (Custom Resource, CR) 对象，例如 `PDGroup`、`TiKVGroup` 和 `TiDBGroup` 等。
2. TiDB Operator 持续监控 (Watch) 这些 CR，根据集群实际状态动态调整各组件对应的 `Pod`、`Service`、`PVC` 和 `ConfigMap` 等对象。

通过这种控制（协调）循环，TiDB Operator 能够自动进行集群节点健康检查和故障恢复。部署、升级、扩缩容等操作也可以通过修改 `Cluster` 和其他组件的 CR 对象“一键”完成。

以下是以 TiKV 为例的控制流程图：

![TiDB Operator Control Flow](/media/tidb-operator-control-flow.png)

在该流程中：

- TiKVGroup Controller：监听 `TiKVGroup` CR，并根据 CR 中的配置创建或更新对应的 `TiKV` CR。
- TiKV Controller：监听 `TiKV` CR，并根据 CR 中的配置创建或更新 TiKV 相关的 Pod、PVC 和 ConfigMap 等资源。
