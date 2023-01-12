---
title: TiDB Operator 1.4.1 Release Notes
---

# TiDB Operator 1.4.1 Release Notes

发布日期: 2023 年 1 月 13 日

TiDB Operator 版本：1.4.1

## 新功能

- 故障自动转移支持在 Kubernetes 节点异常时通过强制移除 Pod 和 PVC 来清理异常的 PD、TiKV 和 TiFlash 节点 ([#4824](https://github.com/pingcap/tidb-operator/pull/4824), [@lalitkfk](https://github.com/lalitkfk))

    - 需要在 TiDB Operator 的 Helm Chart 中配置 `controllerManager.detectNodeFailure` 并在 TidbCluster CR 中配置 `app.kubernetes.io/auto-failure-recovery: "true"` annotation 进行开启

## 优化提升

- 支持在 TiDB Operator 的 Helm Chart 中配置 `controllerManager.kubeClientQPS` 与 `controllerManager.kubeClientBurst` 来设置 TiDB Controller Manager 中 Kubernetes client 的 QPS 和 Burst ([#4830](https://github.com/pingcap/tidb-operator/pull/4830)，[@Thearas](https://github.com/Thearas))

## Bug 修复

- 修复未配置 PV 权限时 TiDB Controller Manager panic 的问题 ([#4837](https://github.com/pingcap/tidb-operator/pull/4837), [@csuzhangxc](https://github.com/csuzhangxc))
