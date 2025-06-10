---
title: TiDB Operator 架构
summary: 了解 TiDB Operator 架构及其工作原理。
---

# TiDB Operator 架构

本文档介绍 TiDB Operator 的架构及其工作原理。

## 架构

下图是 TiDB Operator 的架构概览。

![TiDB Operator Architecture](/media/tidb-operator-architecture.png)

其中，`Cluster`、`PDGroup`、`PD`、`TiKVGroup`、`TiKV`、`TiDBGroup`、`TiDB`、`Backup`、`Restore` 等是 [CustomResourceDefinition（CRD）](https://kubernetes.io/zh-cn/docs/concepts/extend-kubernetes/api-extension/custom-resources/)：

Cluster 是一个 CRD，它抽象了一个 TiDB 集群。它包含了 TiDB 集群的一些通用配置和特性开关，并展示了整个集群的概览状态。这个 CRD 被设计成 TiDB 集群的 “命名空间”。TiDB 集群的所有组件都应该引用一个 Cluster CR。

* `Cluster` 用于描述用户期望的 TiDB 集群
* `TidbMonitor` 用于描述用户期望的 TiDB 集群监控组件
* `Backup` 用于描述用户期望的 TiDB 集群备份
* `Restore` 用于描述用户期望的 TiDB 集群恢复

TiDB 集群的编排由各 CRD 对应的 controller 负责。

## 流程解析

整体的控制流程如下：

1. 用户通过 kubectl 创建 `Cluster` 和其他组件的自定义资源（CustomResource，CR）对象，比如 `PDGroup`、`TiKVGroup`、`TiDBGroup` 等。
2. TiDB Operator 会 watch 这些 CR，基于集群的实际状态不断调整 PD、TiKV、TiDB 等组件的 `Pod`、`Service`、`PVC`、`ConfigMap` 等对象。

基于上述的声明式控制流程，TiDB Operator 能够自动进行集群节点健康检查和故障恢复。部署、升级、扩缩容等操作也可以通过修改 `Cluster` 和 其他组件的 CR 对象“一键”完成。

以 TiKV 为例，控制流程如下图所示：

![TiDB Operator Control Flow](/media/tidb-operator-control-flow.png)

TiDB Operator 的 TiKVGroup Controller 会 watch TiKVGroup CR，并根据 CR 中的配置创建或更新 TiKV CR。而 TiKV Controller 会 watch TiKV CR，并根据 CR 中的配置创建或更新 TiKV Pod 以及对应的 PVC 和 ConfigMap。