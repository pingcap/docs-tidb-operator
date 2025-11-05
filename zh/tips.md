---
title: Kubernetes 上的 TiDB 集群管理常用使用技巧
summary: 介绍 Kubernetes 上 TiDB 集群管理常用使用技巧。
---

# Kubernetes 上的 TiDB 集群管理常用使用技巧

本文介绍了 Kubernetes 上 TiDB 集群管理常用使用技巧。

## 单独修改某个 TiKV 的配置

在一些测试场景中，如果你需要单独修改某一个 TiKV 实例配置，而不影响其他的 TiKV 实例，可以参考文档[在线修改 TiKV 配置](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-tikv-配置)，使用 SQL 在线更新某一个 TiKV 实例的配置。

> **注意：**
>
> 这种方式的配置更新是临时的，不会持久化。这意味着，当该 TiKV 的 Pod 重启后，依旧会使用原来的配置。
