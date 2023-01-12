---
title: TiDB Operator 1.4.1 Release Notes
---

# TiDB Operator 1.4.1 Release Notes

Release date: January 13, 2023

TiDB Operator version: 1.4.1

## New features

- Support cleaning up failed instances of PD, TiKV and TiFlash components by removing the failed Pods and PVCs to handle unplanned failures of Kubernetes nodes in auto failure recovery feature ([#4824](https://github.com/pingcap/tidb-operator/pull/4824), [@lalitkfk](https://github.com/lalitkfk))

    - To enable this feature, you need to configure `controllerManager.detectNodeFailure` in TiDB Operator Helm chart and configure the `app.kubernetes.io/auto-failure-recovery: "true"` annotation in the TidbCluster CR.

## Improvements

- Support configuring `controllerManager.kubeClientQPS` and `controllerManager.kubeClientBurst` in TiDB Operator Helm chart to set QPS and Burst for the Kubernetes client in TiDB Controller Manager ([#4830](https://github.com/pingcap/tidb-operator/pull/4830)，[@Thearas](https://github.com/Thearas))

## Bug fixes

- Fix the issue that TiDB Controller Manager panics without PV permission ([#4837](https://github.com/pingcap/tidb-operator/pull/4837), [@csuzhangxc](https://github.com/csuzhangxc))
