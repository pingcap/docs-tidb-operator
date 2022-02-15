---
title: TiDB Operator 1.3.0 Release Notes
---

# TiDB Operator 1.3.0 Release Notes

Release date: February 12, 2022

TiDB Operator version: 1.3.0

## Compatibility Change

- Due to changes in [#4400](https://github.com/pingcap/tidb-operator/pull/4400), if deploying TiDB cluster across Kubernetes clusters by TiDB Operator v1.3.0-beta.1 or earlier, upgrading TiDB Operator to v1.3.0 directly will cause failed rolling upgrading. You have to upgrade TiDB Operator by following steps:
  1. Update CRD.
  2. Add new `spec.acrossK8s` as `true` in TidbCluster spec.
  3. Upgrade TiDB Operator.

## New Features

- Add new field `spec.tidb.tlsClient.skipInternalClientCA` to skip server certificate verification when internal components access TiDB ([#4388](https://github.com/pingcap/tidb-operator/pull/4388), [@just1900](https://github.com/just1900))
- Support configuring DNS config for Pods of all components ([#4394](https://github.com/pingcap/tidb-operator/pull/4394), [@handlerww](https://github.com/handlerww))
- Add new field `spec.tidb.initializer.createPassword` to support setting a random password for TiDB when deploying new cluster ([#4328](https://github.com/pingcap/tidb-operator/pull/4328), [@mikechengwei](https://github.com/mikechengwei))
- Add new field `failover.recoverByUID` to support one-time recover for TiKV/TiFlash/DM Worker ([#4373](https://github.com/pingcap/tidb-operator/pull/4373), [@better0332](https://github.com/better0332))
- Add new field `sepc.pd.startUpScriptVersion` to use `dig` command not `nslookup` to lookup domain in startup script of PD ([#4379](https://github.com/pingcap/tidb-operator/pull/4379), [@july2993](https://github.com/july2993))

## Improvements

- Pre-check if VolumeMount is exist when deploy or update StatefuleSet of components to aovid failed rolling upgrade ([#4369](https://github.com/pingcap/tidb-operator/pull/4369), [@july2993](https://github.com/july2993))
- Improve the feature deploying TiDB cluster across Kubernetes clusters:
  - Add new field `spec.acrossK8s` to indicate deploying TiDB cluster across Kubernetes clusters ([#4400](https://github.com/pingcap/tidb-operator/pull/4400), [@KanShiori](https://github.com/KanShiori))
  - Support deploying heterogeneous TiDB cluster across Kubernetes clusters ([#4387](https://github.com/pingcap/tidb-operator/pull/4387), [@KanShiori](https://github.com/KanShiori))
  - The field `spec.clusterDomain` isn't required when deploying TiDB cluster across Kubernetes clusters, the field is only used for addresses accessed between components ([#4408](https://github.com/pingcap/tidb-operator/pull/4408), [@KanShiori](https://github.com/KanShiori))
  - Fixed the issue that Pump become abnormal when the PDs of one Kubernetes cluster are all down in across Kubernetes deployment ([#4377](https://github.com/pingcap/tidb-operator/pull/4377), [@just1900](https://github.com/just1900))

## Bug fixes

- Fix the issue that tidb scheduler can't be deployed in Kubernetes v1.23 or later ([#4386](https://github.com/pingcap/tidb-operator/pull/4386), [@just1900](https://github.com/just1900))
