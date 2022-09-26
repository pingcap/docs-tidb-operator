---
title: TiDB Operator 1.4.0-alpha.1 Release Notes
---

# TiDB Operator 1.4.0-alpha.1 Release Notes

发布日期：2022 年 9 月 26 日

TiDB Operator 版本：1.4.0-alpha.1

## 兼容性改动

- 由于 [#4683](https://github.com/pingcap/tidb-operator/pull/4683) 的变更，存储修改的功能变为默认关闭的。如果你想扩容某个组件的 PVC，你需要先打开这个功能。

## 滚动升级改动

- 由于 [#4494](https://github.com/pingcap/tidb-operator/pull/4494) 的变更，如果你部署的 TiCDC 没有设置 `log-file` 配置项，那么升级 TiDB Operator 到 v1.4.0-alpha.1 后会导致 TiCDC 滚动重建。

## 新功能

- 支持自动设置 TiDB 的 location labels ([#4663](https://github.com/pingcap/tidb-operator/pull/4663), [@glorv](https://github.com/glorv))

- 添加新字段 `spec.tikv.scalePolicy` 与 `spec.tiflash.scalePolicy`，用于同时缩容或者扩容多个 TiKV 和 TiFlash Pods ([#3881](https://github.com/pingcap/tidb-operator/pull/3881), [@lizhemingi](https://github.com/lizhemingi))

- 添加一个新字段 `startScriptVersion` 用于选择所有组件的启动脚本 ([#4505](https://github.com/pingcap/tidb-operator/pull/4505), [@KanShiori](https://github.com/KanShiori))

- 支持将 PD 的 location labels 中的简短的 label 映射到众所周知的 Kubernetes 的 labels ([#4688](https://github.com/pingcap/tidb-operator/pull/4688), [@glorv](https://github.com/glorv))

- 支持使用 BR 恢复集群到快照备份和日志备份的某个时间点 ([#4648](https://github.com/pingcap/tidb-operator/pull/4648) [#4682](https://github.com/pingcap/tidb-operator/pull/4682) [#4694](https://github.com/pingcap/tidb-operator/pull/4694) [#4695](https://github.com/pingcap/tidb-operator/pull/4695), [@WizardXiao](https://github.com/WizardXiao))

- 添加一个新的 feature gate `VolumeModifying`，用以打开修改存储参数的功能，该功能默认关闭 ([#4683](https://github.com/pingcap/tidb-operator/pull/4683), [@liubog2008](https://github.com/liubog2008))

- 支持通过修改某个 TidbCluster 组件的 `StorageClass` 来修改集群所用的 AWS EBS 存储的 IOPS 与 throughput ([#4683](https://github.com/pingcap/tidb-operator/pull/4683), [@liubog2008](https://github.com/liubog2008))

- 支持配置 BR 的 `--check-requirements` 参数  ([#4631](https://github.com/pingcap/tidb-operator/pull/4631), [@KanShiori](https://github.com/KanShiori))

- 支持使用字段 `additionalContainers` 来自定义 Pod 容器的配置。如果字段中的容器名字与 TiDB Operator 生成的容器一致，那么会将该字段设置的容器配置合并到默认的容器配置 ([#4530](https://github.com/pingcap/tidb-operator/pull/4530), [@mikechengwei](https://github.com/mikechengwei))

## 优化提升

- 优化 `TidbMonitor` 所使用的 Prometheus 的 remoteWrite 配置 ([#4247](https://github.com/pingcap/tidb-operator/pull/4247), [@mikechengwei](https://github.com/mikechengwei))

- 为 TiFlash `Service` 添加 metric 端口 ([#4470](https://github.com/pingcap/tidb-operator/pull/4470), [@mikechengwei](https://github.com/mikechengwei))

- 更新 TiCDC 的 `log-file` 配置项的默认值，以避免覆盖 `/dev/stderr` ([#4494](https://github.com/pingcap/tidb-operator/pull/4494), [@KanShiori](https://github.com/KanShiori))

## 错误修复

- 修复在集群扩缩容时，挂起集群导致的集群管理阻塞的问题 ([#4679](https://github.com/pingcap/tidb-operator/pull/4679), [@KanShiori](https://github.com/KanShiori))

- 修复在 PD spec 为空时导致 TiDB Operator 崩溃的问题 ([#4679](https://github.com/pingcap/tidb-operator/pull/4691), [@KanShiori](https://github.com/mahjonp))