---
title: TiDB Operator 1.3.0-beta.1 Release Notes
---
# TiDB Operator 1.3.0-beta.1 Release Notes

Release date: January 12, 2022

TiDB Operator version: 1.3.0-beta.1

## Rolling Update Changes

- Due to [#4358](https://github.com/pingcap/tidb-operator/pull/4358), If deploy v5.4 tidb cluster by v1.2 operator, upgrade operator will cause rolling upgrade of tiflash ([#4358](https://github.com/pingcap/tidb-operator/pull/4358), [@KanShiori](https://github.com/KanShiori))
- Due to [#4169](https://github.com/pingcap/tidb-operator/pull/4169) ,If deploy tidb cluster that version is equal or larger than v5.0.0 and the field `separateRocksDBLog` is true, it will casuse tikv recreation after upgrade operator ([#4169](https://github.com/pingcap/tidb-operator/pull/4169), [@mianhk](https://github.com/mianhk))

## New Features

- Support to configure init container resource for TiFlash ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- Support to deploy TiDBNGMonitoring ([#4287](https://github.com/pingcap/tidb-operator/pull/4287), [@KanShiori](https://github.com/KanShiori))
- Support evicting region leaders for TiKV and restarting TiKV gracefully through annotations ([#4279](https://github.com/pingcap/tidb-operator/pull/4279), [@july2993](https://github.com/july2993))
- support PodSecurityContext for Discovery ([#4259](https://github.com/pingcap/tidb-operator/pull/4259), [@csuzhangxc](https://github.com/csuzhangxc))
- Feature: support configuring PodManagementPolicy in TidbCluster CR ([#4211](https://github.com/pingcap/tidb-operator/pull/4211), [@mianhk](https://github.com/mianhk))
- Support configurations for Discovery ([#4208](https://github.com/pingcap/tidb-operator/pull/4208), [@KanShiori](https://github.com/KanShiori))
- Support tidbmonitor prometheus shards feature. ([#4198](https://github.com/pingcap/tidb-operator/pull/4198), [@mikechengwei](https://github.com/mikechengwei))
- Support to use `v1 Ingress` and be compatible with `v1beta1 Ingress` ([#4195](https://github.com/pingcap/tidb-operator/pull/4195), [@KanShiori](https://github.com/KanShiori))

## Improvements

- Remove and change some default configurations for TiFlash due to config change about v5.4.0 TiFlash. If deploy v5.4 tidb cluster by v1.2 operator, upgrade operator will cause rolling upgrade of tiflash ([#4358](https://github.com/pingcap/tidb-operator/pull/4358), [@KanShiori](https://github.com/KanShiori))
- Add e2e cases for multi-kubernetes tidbcluster ([#4354](https://github.com/pingcap/tidb-operator/pull/4354), [#4352](https://github.com/pingcap/tidb-operator/pull/4352), [#4314](https://github.com/pingcap/tidb-operator/pull/4314), [#4300](https://github.com/pingcap/tidb-operator/pull/4300), [@just1900](https://github.com/just1900))
- Add e2e case for deploy and delete a cluster on multi-cluster kubernetes ([#4289](https://github.com/pingcap/tidb-operator/pull/4289), [@handlerww](https://github.com/handlerww))
- Optimize: Deprecate pod validating and mutating webhook ([#4209](https://github.com/pingcap/tidb-operator/pull/4209), [@mianhk](https://github.com/mianhk))
- Remove dependency with the firstTC and firstDC in the TidbMonitor controller. ([#4272](https://github.com/pingcap/tidb-operator/pull/4272), [@mikechengwei](https://github.com/mikechengwei))
- Read tls cert from local TC when TC is heterogeneous or across-kubernetes ([#4249](https://github.com/pingcap/tidb-operator/pull/4249), [@KanShiori](https://github.com/KanShiori))
- Separate dm and tidb monitor code logic. ([#4243](https://github.com/pingcap/tidb-operator/pull/4243), [@mikechengwei](https://github.com/mikechengwei))
- Optimization for secret retrieving logic ([#4166](https://github.com/pingcap/tidb-operator/pull/4166), [@mianhk](https://github.com/mianhk))
- Improve advanced example of TidbMonitor ([#4242](https://github.com/pingcap/tidb-operator/pull/4242), [@mianhk](https://github.com/mianhk))
- Use scheduler configuration to run tidb-scheduler, when Kubernetes is higher than  v1.19 ([#4202](https://github.com/pingcap/tidb-operator/pull/4202), [@KanShiori](https://github.com/KanShiori))
- Show the metrics for one TiDB cluster and its heterogeneous clusters in the same dashboards. ([#4210](https://github.com/pingcap/tidb-operator/pull/4210), [@mikechengwei](https://github.com/mikechengwei))
- Force upgrade PD when PD replicas number is less than 2 ([#4107](https://github.com/pingcap/tidb-operator/pull/4107), [@mianhk](https://github.com/mianhk))
- use secretRef for Grafana password in TidbMonitor ([#4135](https://github.com/pingcap/tidb-operator/pull/4135), [@mianhk](https://github.com/mianhk))
- Fast upgrade TiKV when tikv replicas number are less than 2 ([#4091](https://github.com/pingcap/tidb-operator/pull/4091), [@mianhk](https://github.com/mianhk))

## Other Notable Changes

- Separate package `pkg/apis` and `pkg/client` into submodules ([#4134](https://github.com/pingcap/tidb-operator/pull/4134), [@KanShiori](https://github.com/KanShiori))
- set all components minimum replicas to 0 ([#4288](https://github.com/pingcap/tidb-operator/pull/4288), [@handlerww](https://github.com/handlerww))
- The helper image was updated to a newer version of busybox ([#4260](https://github.com/pingcap/tidb-operator/pull/4260), [@dveeden](https://github.com/dveeden))
- Update grafana images in examples to 7.5.11 due to security issue. ([#4212](https://github.com/pingcap/tidb-operator/pull/4212), [@makocchi-git](https://github.com/makocchi-git))
- remove unused func SyncAutoScalerAnn ([#4192](https://github.com/pingcap/tidb-operator/pull/4192), [@mianhk](https://github.com/mianhk))
- Update kubernetes dependency to v1.19.14 ([#4161](https://github.com/pingcap/tidb-operator/pull/4161), [@KanShiori](https://github.com/KanShiori))
- Support configure tidb-controller-manager workers number in helm chart ([#4111](https://github.com/pingcap/tidb-operator/pull/4111), [@mianhk](https://github.com/mianhk))
