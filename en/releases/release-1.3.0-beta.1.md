---
title: TiDB Operator 1.3.0-beta.1 Release Notes
---
# TiDB Operator 1.3.0-beta.1 Release Notes

Release date: January 12, 2022

TiDB Operator version: 1.3.0-beta.1

## Compatibility Changes

Due to [#4209](https://github.com/pingcap/tidb-operator/pull/4209), If `ValidatingWebhook` and `MutatingWebhook` of pods are deployed in the cluster by TiDB Operator v1.2 or earlier, upgrading TiDB Operator to v1.3.0-beta.1 will cause `ValidatingWebhook` and `MutatingWebhook` to be deleted. But this has no impact on TiDB cluster management.

## Rolling Update Changes

- Due to [#4358](https://github.com/pingcap/tidb-operator/pull/4358), If tidb cluster with version greater or equal to v5.4 is deployed by v1.2 operator, upgrading TiDB Operator to v1.3.0-beta.1 will cause the rolling upgrade of TiFlash. It's recommended to upgrade TiDB Operator to v1.3 before upgrading the TiDB cluster to v5.4.0 or higher version.
- Due to [#4169](https://github.com/pingcap/tidb-operator/pull/4169) , If tidb cluster with version greater or equal to v5.0 is deployed and `spec.tikv.seperateRocksDBLog: true` or  `spec.tikv.separateRaftLog: true` is set, it will casuse tikv recreation after upgrading operator ([#4169](https://github.com/pingcap/tidb-operator/pull/4169), [@mianhk](https://github.com/mianhk))

## New Features

- Support to configure init container resource for TiFlash ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- Support to deploy TiDBNGMonitoring ([#4287](https://github.com/pingcap/tidb-operator/pull/4287), [@KanShiori](https://github.com/KanShiori))
- Support evicting region leaders for TiKV and restarting TiKV gracefully through annotations ([#4279](https://github.com/pingcap/tidb-operator/pull/4279), [@july2993](https://github.com/july2993))
- support PodSecurityContext and other configurations for Discovery ([#4259](https://github.com/pingcap/tidb-operator/pull/4259), [@csuzhangxc](https://github.com/csuzhangxc), [#4208](https://github.com/pingcap/tidb-operator/pull/4208), [@KanShiori](https://github.com/KanShiori))
- Feature: support configuring PodManagementPolicy in TidbCluster CR ([#4211](https://github.com/pingcap/tidb-operator/pull/4211), [@mianhk](https://github.com/mianhk))
- Support tidbmonitor prometheus shards feature. ([#4198](https://github.com/pingcap/tidb-operator/pull/4198), [@mikechengwei](https://github.com/mikechengwei))
- Support deploy TiDB Operator in kubernetes higher than v1.22 ([#4195](https://github.com/pingcap/tidb-operator/pull/4195), [#4202](https://github.com/pingcap/tidb-operator/pull/4202), [@KanShiori](https://github.com/KanShiori))

## Improvements

- Remove and change some default configurations for TiFlash due to config change about v5.4.0 TiFlash. If deploy v5.4 tidb cluster by v1.2 operator, upgrade operator will cause rolling upgrade of tiflash ([#4358](https://github.com/pingcap/tidb-operator/pull/4358), [@KanShiori](https://github.com/KanShiori))
- Improve advanced example of TidbMonitor ([#4242](https://github.com/pingcap/tidb-operator/pull/4242), [@mianhk](https://github.com/mianhk))
- Show the metrics for one TiDB cluster and its heterogeneous clusters in the same dashboards. ([#4210](https://github.com/pingcap/tidb-operator/pull/4210), [@mikechengwei](https://github.com/mikechengwei))
- Use secretRef for Grafana password in TidbMonitor to avoid using plaintext password ([#4135](https://github.com/pingcap/tidb-operator/pull/4135), [@mianhk](https://github.com/mianhk))
- Optimize the upgrading process for PD and TiKV components with less than 2 replicas number. By default, PD and TiKV are forced to be upgraded to avoid stuck on upgrading ([#4107](https://github.com/pingcap/tidb-operator/pull/4107), [#4091](https://github.com/pingcap/tidb-operator/pull/4091), [@mianhk](https://github.com/mianhk))

## Other Notable Changes

- Update grafana images in examples to 7.5.11 due to security issue. ([#4212](https://github.com/pingcap/tidb-operator/pull/4212), [@makocchi-git](https://github.com/makocchi-git))
- Deprecate pod validating and mutating webhook ([#4209](https://github.com/pingcap/tidb-operator/pull/4209), [@mianhk](https://github.com/mianhk))
- Support configure tidb-controller-manager workers number in helm chart ([#4111](https://github.com/pingcap/tidb-operator/pull/4111), [@mianhk](https://github.com/mianhk))
