---
title: TiDB Operator v1.4 新特性
---

# TiDB Operator v1.4 新特性

TiDB Operator v1.4 引入了以下关键特性，从扩展性、易用性等方面帮助你更轻松地管理 TiDB 集群及其周边工具。

## 兼容性改动

由于 [#4683](https://github.com/pingcap/tidb-operator/pull/4683) 的变更，存储修改的功能变为默认关闭的。如果你想扩容某个组件的 PVC，你需要先打开这个功能。

## 滚动更新改动

由于 [#4494](https://github.com/pingcap/tidb-operator/pull/4494) 的变更，如果你部署的 TiCDC 没有设置 `log-file` 配置项，那么升级 TiDB Operator 到 v1.4.0-alpha.1 及之后版本会导致 TiCDC 滚动重建。

## 扩展性

- 支持使用新的 `TidbDashboard` CRD 独立管理 [TiDB Dashboard](https://github.com/pingcap/tidb-dashboard)。
- 支持基于 Amazon EBS 的 TiDB 集群 volume-snapshot 的备份和恢复。
- 支持同时缩容或者扩容多个 TiKV 和 TiFlash Pods。
- 支持使用 BR 恢复集群到快照备份和日志备份的某个时间点。
- 支持修改 TiDB 集群所用的 AWS EBS 存储的 IOPS 与 throughput。
- 实验性支持 [TiProxy](https://github.com/pingcap/tiproxy)。

## 易用性

- 支持为 TiKV 与 PD 配置 Liveness Probe。
- 支持自动设置 TiDB 的 location labels。
- 支持将 PD 的 location labels 中的简短的 label 映射到众所周知的 Kubernetes 的 labels。
- 支持使用字段 `additionalContainers` 来自定义 Pod 容器的配置。
- 支持配置 BR 的 `--check-requirements` 参数。
- 为 TiFlash `Service` 添加 metric 端口。
