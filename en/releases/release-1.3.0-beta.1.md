---
title: TiDB Operator 1.3.0-beta.1 Release Notes
---
# TiDB Operator 1.3.0-beta.1 Release Notes

Release date: January 12, 2022

TiDB Operator version: 1.3.0-beta.1

## Compatibility Change

- Due to changes in [#4209](https://github.com/pingcap/tidb-operator/pull/4209), if Webhook is deployed, and `ValidatingWebhook` and `MutatingWebhook` of Pods are enabled with TiDB Operator v1.2 or earlier versions, upgrading TiDB Operator to v1.3.0-beta.1 will cause `ValidatingWebhook` and `MutatingWebhook` to be deleted. But this has no impact on TiDB cluster management.

- Due to changes in [#4151](https://github.com/pingcap/tidb-operator/pull/4151), if you deploy v1 CRD, TiDB Operator >= v1.3.0-beta.1 sets the default `baseImage` field of all components. If you set the component image using the `image` field instead of the `baseImage` field, upgrading TiDB Operator to v1.3.0-beta.1 will change the image in use, cause the TiDB cluster to rolling update or even fail to run. To avoid such situations, you must upgrade TiDB Operator by the following steps:
    1. Use the `baseImage` and `version` fields to replace the `image` field. For details, refer to [Configure TiDB deployment](../configure-a-tidb-cluster.md#version).
    2. Upgrade TiDB Operator.

- Due to the issue in [#4434](https://github.com/pingcap/tidb-operator/pull/4434), if you upgrade TiFlash to v5.4.0 or later when using v1.3.0-beta.1 TiDB Operator, TiFlash might lose metadata and not work. If TiFlash is deployed in your cluster, it is recommended that you upgrade TiDB Operator to v1.3.1 or later versions before upgrading TiFlash.

- Due to the issue [#4435](https://github.com/pingcap/tidb-operator/pull/4435), If there isn't the `tmp_path` field in TiFlash's config, you can't use v5.4.0 TiFlash when using v1.3.0-beta.1 TiDB Operator. It's recommended that upgrade TiDB Operator to v1.3.1 or later to use TiFlash.

## Rolling Update Changes

- Due to changes in [#4358](https://github.com/pingcap/tidb-operator/pull/4358), if the TiDB cluster (>= v5.4) is deployed by TiDB Operator v1.2, upgrading TiDB Operator to v1.3.0-beta.1 causes TiFlash to rolling upgrade. It is recommended to upgrade TiDB Operator to v1.3 before upgrading the TiDB cluster to v5.4.0 or later versions.
- Due to changes in [#4169](https://github.com/pingcap/tidb-operator/pull/4169) , for TiDB clusters >= v5.0, if `spec.tikv.seperateRocksDBLog: true` or  `spec.tikv.separateRaftLog: true` is configured, upgrading TiDB Operator to v1.3.0-beta.1 causes TiKV to rolling upgrade.
- Due to changes in [#4198](https://github.com/pingcap/tidb-operator/pull/4198), upgrading TiDB Operator causes the recreation of TidbMonitor Pod.

## New Features

- Support configuring the resource usage for the init container of TiFlash ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- Support enabling [continuous profiling](../access-dashboard.md#enable-continuous-profiling) for the TiDB cluster ([#4287](https://github.com/pingcap/tidb-operator/pull/4287), [@KanShiori](https://github.com/KanShiori))
- Support gracefully restarting TiKV through annotations ([#4279](https://github.com/pingcap/tidb-operator/pull/4279), [@july2993](https://github.com/july2993))
- Support `PodSecurityContext` and other configurations for Discovery ([#4259](https://github.com/pingcap/tidb-operator/pull/4259), [@csuzhangxc](https://github.com/csuzhangxc), [#4208](https://github.com/pingcap/tidb-operator/pull/4208), [@KanShiori](https://github.com/KanShiori))
- Support configuring `PodManagementPolicy` in TidbCluster CR ([#4211](https://github.com/pingcap/tidb-operator/pull/4211), [@mianhk](https://github.com/mianhk))
- Support configuring Prometheus shards in TidbMonitor CR ([#4198](https://github.com/pingcap/tidb-operator/pull/4198), [@mikechengwei](https://github.com/mikechengwei))
- Support deploying TiDB Operator in Kubernetes v1.22 or later versions ([#4195](https://github.com/pingcap/tidb-operator/pull/4195), [#4202](https://github.com/pingcap/tidb-operator/pull/4202), [@KanShiori](https://github.com/KanShiori))
- Generate v1 CRD to support deploying in Kubernetes v1.22 or later versions ([#4151](https://github.com/pingcap/tidb-operator/pull/4151), [@KanShiori](https://github.com/KanShiori))

## Improvements

- Remove and change some default configurations for TiFlash due to configuration changes in TiFlash v5.4.0. If the TiDB cluster (>= v5.4) is deployed by TiDB Operator v1.2, upgrading TiDB Operator to v1.3.0-beta.1 causes TiFlash to rolling upgrade. ([#4358](https://github.com/pingcap/tidb-operator/pull/4358), [@KanShiori](https://github.com/KanShiori))
- Improve advanced deployment example of TidbMonitor. ([#4242](https://github.com/pingcap/tidb-operator/pull/4242), [@mianhk](https://github.com/mianhk))
- Optimize the user experience of heterogenous clusters by displaying the metrics for one TiDB cluster and its heterogeneous clusters in the same dashboards. ([#4210](https://github.com/pingcap/tidb-operator/pull/4210), [@mikechengwei](https://github.com/mikechengwei))
- Use `secretRef` to obtain Grafana password in TidbMonitor to avoid using plaintext password. ([#4135](https://github.com/pingcap/tidb-operator/pull/4135), [@mianhk](https://github.com/mianhk))
- Optimize the upgrade process for PD and TiKV components with fewer than two replicas, and force the upgrade of PD and TiKV components by default to avoid the upgrade process from taking too long ([#4107](https://github.com/pingcap/tidb-operator/pull/4107), [#4091](https://github.com/pingcap/tidb-operator/pull/4091), [@mianhk](https://github.com/mianhk))
- Update Grafana images in examples to 7.5.11 to enhance security ([#4212](https://github.com/pingcap/tidb-operator/pull/4212), [@makocchi-git](https://github.com/makocchi-git))
- Deprecate Pod validating and mutating webhook ([#4209](https://github.com/pingcap/tidb-operator/pull/4209), [@mianhk](https://github.com/mianhk))
- Support configuring the number of tidb-controller-manager workers in Helm chart ([#4111](https://github.com/pingcap/tidb-operator/pull/4111), [@mianhk](https://github.com/mianhk))
