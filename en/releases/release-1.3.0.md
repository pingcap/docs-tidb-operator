---
title: TiDB Operator 1.3.0 Release Notes
---

# TiDB Operator 1.3.0 Release Notes

Release date: February 15, 2022

TiDB Operator version: 1.3.0

## Compatibility Change

- Due to changes in [#4400](https://github.com/pingcap/tidb-operator/pull/4400), if a TiDB cluster is deployed across multiple Kubernetes clusters by TiDB Operator (<= v1.3.0-beta.1), upgrading TiDB Operator to v1.3.0 directly will cause failed rolling upgrade. You have to upgrade TiDB Operator by the following steps:
    1. Update CRD.
    2. Add a new `spec.acrossK8s` field in TidbCluster spec and set it to `true`.
    3. Upgrade TiDB Operator.

- Due to the issue [#4434](https://github.com/pingcap/tidb-operator/pull/4434), If you upgrade TiFlash to v5.4.0 or later when using v1.3.0 TiDB Operator, TiFlash maybe lose metadata and not work. If TiFlash is deployed in your cluster, it's recommended that upgrade TiDB Operator to v1.3.1 or later to upgrade TiFlash.

- Due to the issue [#4435](https://github.com/pingcap/tidb-operator/pull/4435), when using v1.3.0 TiDB Operator, you have to set `tmp_path` field in TiFlash's config to use v5.4.0 or later TiFlash. It's recommended that upgrade TiDB Operator to v1.3.1 or later to use TiFlash.

## New Features

- Add a new field `spec.tidb.tlsClient.skipInternalClientCA` to skip server certificate verification when internal components access TiDB ([#4388](https://github.com/pingcap/tidb-operator/pull/4388), [@just1900](https://github.com/just1900))
- Support configuring DNS config for Pods of all components ([#4394](https://github.com/pingcap/tidb-operator/pull/4394), [@handlerww](https://github.com/handlerww))
- Add a new field `spec.tidb.initializer.createPassword` to support setting a random password for TiDB when deploying a new cluster ([#4328](https://github.com/pingcap/tidb-operator/pull/4328), [@mikechengwei](https://github.com/mikechengwei))
- Add a new field `failover.recoverByUID` to support one-time recover for TiKV/TiFlash/DM Worker ([#4373](https://github.com/pingcap/tidb-operator/pull/4373), [@better0332](https://github.com/better0332))
- Add a new field `sepc.pd.startUpScriptVersion` to use the `dig` command instead of `nslookup` to lookup domain in the startup script of PD ([#4379](https://github.com/pingcap/tidb-operator/pull/4379), [@july2993](https://github.com/july2993))

## Improvements

- Pre-check whether `VolumeMount` exists when the StatefuleSet of components is deployed or updated to avoid failed rolling upgrade ([#4369](https://github.com/pingcap/tidb-operator/pull/4369), [@july2993](https://github.com/july2993))
- Enhance the feature of deploying a TiDB cluster across Kubernetes clusters:
    - Add a new field `spec.acrossK8s` to indicate deploying a TiDB cluster across Kubernetes clusters ([#4400](https://github.com/pingcap/tidb-operator/pull/4400), [@KanShiori](https://github.com/KanShiori))
    - Support deploying heterogeneous TiDB cluster across Kubernetes clusters ([#4387](https://github.com/pingcap/tidb-operator/pull/4387), [@KanShiori](https://github.com/KanShiori))
    - The field `spec.clusterDomain` is not required when TiDB cluster is deployed across Kubernetes clusters. The field is only used for addresses accessed between components ([#4408](https://github.com/pingcap/tidb-operator/pull/4408), [@KanShiori](https://github.com/KanShiori))
    - Fix the issue that in cross-Kubernetes deployment, Pump becomes abnormal when all PDs of one Kubernetes cluster are down ([#4377](https://github.com/pingcap/tidb-operator/pull/4377), [@just1900](https://github.com/just1900))

## Bug fixes

- Fix the issue that tidb scheduler cannot be deployed in Kubernetes v1.23 or later versions ([#4386](https://github.com/pingcap/tidb-operator/pull/4386), [@just1900](https://github.com/just1900))
