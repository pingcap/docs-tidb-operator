---
title: TiDB Operator 1.3.0-beta.1 Release Notes
---
# TiDB Operator 1.3.0-beta.1 Release Notes

Release date: January 12, 2022

TiDB Operator version: 1.3.0-beta.1

## Compatibility Change

Due to changes in [#4209](https://github.com/pingcap/tidb-operator/pull/4209), if `ValidatingWebhook` and `MutatingWebhook` of Pods are deployed in the cluster by TiDB Operator v1.2 or earlier versions, upgrading TiDB Operator to v1.3.0-beta.1 will cause `ValidatingWebhook` and `MutatingWebhook` to be deleted. But this has no impact on TiDB cluster management.

## Rolling Update Changes

- Due to changes in [#4358](https://github.com/pingcap/tidb-operator/pull/4358), if the TiDB cluster (>= v5.4) is deployed by TiDB Operator v1.2, upgrading TiDB Operator to v1.3.0-beta.1 causes TiFlash to rolling upgrade. It is recommended to upgrade TiDB Operator to v1.3 before upgrading the TiDB cluster to v5.4.0 or later versions.
- Due to changes in [#4169](https://github.com/pingcap/tidb-operator/pull/4169) , for TiDB clusters >= v5.0, if `spec.tikv.seperateRocksDBLog: true` or  `spec.tikv.separateRaftLog: true` is configured, upgrading TiDB Operator to v1.3.0-beta.1 causes TiKV to rolling upgrade.

## New Features

- Support configuring the resource usage for the init container of TiFlash ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- Support enabling continuous profiling for the TiDB cluster ([#4287](https://github.com/pingcap/tidb-operator/pull/4287), [@KanShiori](https://github.com/KanShiori))
- Support gracefully restarting TiKV through annotations ([#4279](https://github.com/pingcap/tidb-operator/pull/4279), [@july2993](https://github.com/july2993))
- Support `PodSecurityContext` and other configurations for Discovery ([#4259](https://github.com/pingcap/tidb-operator/pull/4259), [@csuzhangxc](https://github.com/csuzhangxc), [#4208](https://github.com/pingcap/tidb-operator/pull/4208), [@KanShiori](https://github.com/KanShiori))
- Support configuring `PodManagementPolicy` in TidbCluster CR ([#4211](https://github.com/pingcap/tidb-operator/pull/4211), [@mianhk](https://github.com/mianhk))
- Support configuring Prometheus shards in TidbMonitor CR ([#4198](https://github.com/pingcap/tidb-operator/pull/4198), [@mikechengwei](https://github.com/mikechengwei))
- Support deploying TiDB Operator in Kubernetes v1.22 or later versions ([#4195](https://github.com/pingcap/tidb-operator/pull/4195), [#4202](https://github.com/pingcap/tidb-operator/pull/4202), [@KanShiori](https://github.com/KanShiori))

## Improvements

- Remove and change some default configurations for TiFlash due to configuration changes in TiFlash v5.4.0. If the TiDB cluster (>= v5.4) is deployed by TiDB Operator v1.2, upgrading TiDB Operator to v1.3.0-beta.1 causes TiFlash to rolling upgrade. ([#4358](https://github.com/pingcap/tidb-operator/pull/4358), [@KanShiori](https://github.com/KanShiori))
- Improve advanced deployment example of TidbMonitor. ([#4242](https://github.com/pingcap/tidb-operator/pull/4242), [@mianhk](https://github.com/mianhk))
- Optimize the user experience of heterogenous clusters by displaying the metrics for one TiDB cluster and its heterogeneous clusters in the same dashboards. ([#4210](https://github.com/pingcap/tidb-operator/pull/4210), [@mikechengwei](https://github.com/mikechengwei))
- Use `secretRef` to obtain Grafana password in TidbMonitor to avoid using plaintext password. ([#4135](https://github.com/pingcap/tidb-operator/pull/4135), [@mianhk](https://github.com/mianhk))
- Optimize the upgrade process for PD and TiKV components with fewer than two replicas, and force the upgrade of PD and TiKV components by default to avoid the upgrade process from taking too long ([#4107](https://github.com/pingcap/tidb-operator/pull/4107), [#4091](https://github.com/pingcap/tidb-operator/pull/4091), [@mianhk](https://github.com/mianhk))

## Other Notable Changes

- Update Grafana images in examples to 7.5.11 to enhance security ([#4212](https://github.com/pingcap/tidb-operator/pull/4212), [@makocchi-git](https://github.com/makocchi-git))
- Deprecate Pod validating and mutating webhook ([#4209](https://github.com/pingcap/tidb-operator/pull/4209), [@mianhk](https://github.com/mianhk))
- Support configuring the number of tidb-controller-manager workers in Helm chart ([#4111](https://github.com/pingcap/tidb-operator/pull/4111), [@mianhk](https://github.com/mianhk))
