---
title: TiDB Operator 1.1.10 Release Notes
---

# TiDB Operator 1.1.10 Release Notes

Release date: January 29, 2021

TiDB Operator version: 1.1.10

## Rolling Update Changes

- If the `spec.initializer.version` in the TidbMonitor does not match the TiDB version in the TidbCluster, upgrading TiDB Operator will cause the recreation of the TidbMonitor Pod due to [#3684](https://github.com/pingcap/tidb-operator/pull/3684)

## New Features

- Support canary upgrade of TiDB Operator ([#3548](https://github.com/pingcap/tidb-operator/pull/3548), [@shonge](https://github.com/shonge), [#3554](https://github.com/pingcap/tidb-operator/pull/3554), [@cvvz](https://github.com/cvvz))
- TidbMonitor supports `remotewrite` configuration ([#3679](https://github.com/pingcap/tidb-operator/pull/3679), [@mikechengwei](https://github.com/mikechengwei))
- Support configuring init containers for components in the TiDB cluster ([#3713](https://github.com/pingcap/tidb-operator/pull/3713), [@handlerww](https://github.com/handlerww))
- Add local backend support to the TiDB Lightning chart ([#3644](https://github.com/pingcap/tidb-operator/pull/3644), [@csuzhangxc](https://github.com/csuzhangxc))

## Improvements

- Support customizing the storage config for TiDB slow log ([#3731](https://github.com/pingcap/tidb-operator/pull/3731), [@BinChenn](https://github.com/BinChenn))
- Add `tidb_cluster` label for the scrape jobs in TidbMonitor to support monitoring multiple clusters ([#3750](https://github.com/pingcap/tidb-operator/pull/3750), [@mikechengwei](https://github.com/mikechengwei))
- During the upgrade, after TiKV Pod is recreated, delete the corresponding evict leader scheduler  ([#3724](https://github.com/pingcap/tidb-operator/pull/3724), [@handlerww](https://github.com/handlerww))
- Optimize CR syncing intervals ([#3700](https://github.com/pingcap/tidb-operator/pull/3700), [@dragonly](https://github.com/dragonly))
- Supports persisting checkpoint for TiDB Lightning helm chart ([#3653](https://github.com/pingcap/tidb-operator/pull/3653), [@csuzhangxc](https://github.com/csuzhangxc))
- Change the directory to save the customized alert rules in TidbMonitor from `tidb:${tidb_image_version}` to `tidb:${initializer_image_version}`. Please note that if the `spec.initializer.version` in the TidbMonitor does not match with the TiDB version in the TidbCluster, upgrade TiDB Operator will cause the re-creation of the monitor Pod ([#3684](https://github.com/pingcap/tidb-operator/pull/3684), [@BinChenn](https://github.com/BinChenn))

## Bug Fixes

- Fix the issue that when TLS is enabled for the TiDB cluster, if `spec.from` or `spec.to` is not configured, backup and restore jobs with BR might fail ([#3707](https://github.com/pingcap/tidb-operator/pull/3707), [@BinChenn](https://github.com/BinChenn))
- Fix the bug that if advanced StatefulSet is enabled and `delete-slots` annotations are added for PD or TiKV, the Pods whose ordinal is bigger than `replicas - 1` will be terminated directly without any pre-delete operations such as evicting leaders ([#3702](https://github.com/pingcap/tidb-operator/pull/3702), [@cvvz](https://github.com/cvvz))
- Fix the issue that after the Pod has been evicted or killed, the status of backup or restore is not `Failed` ([#3696](https://github.com/pingcap/tidb-operator/pull/3696), [@csuzhangxc](https://github.com/csuzhangxc))
- Fix the issue that when TiKV cluster is not bootstrapped, the TiKV component could not be recovered by editing `TidbCluster` CR ([#3694](https://github.com/pingcap/tidb-operator/pull/3694), [@cvvz](https://github.com/cvvz))
