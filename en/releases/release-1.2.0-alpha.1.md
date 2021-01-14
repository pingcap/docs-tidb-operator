---
title: TiDB Operator 1.2.0-alpha.1 Release Notes
---

# TiDB Operator 1.2.0-alpha.1 Release Notes

Release date: January 15, 2021

TiDB Operator version: 1.2.0-alpha.1

## New Features

- Across Kubernetes Deployment ([#2816](https://github.com/pingcap/tidb-operator/issues/2816), [@handlerww](https://github.com/handlerww), In progress, v1.2.0-alpha.1, IDC)
- Support DM 2.0 in TiDB Operator ([#2868](https://github.com/pingcap/tidb-operator/issues/2868), In progress, v1.2.0-alpha.1)
- Lightning (v1.2.0-alpha.1) ([@july2993](https://github.com/july2993)) 
    - TLS [#1631](https://github.com/pingcap/tidb-operator/issues/1631)
    - Local Backend [#3162](https://github.com/pingcap/tidb-operator/issues/3162)
- Monitoring Architecture Improvement
    - Use statefulsets
    - Support thanos
- Canary Upgrade of TiDB Operator
- Auto-Scaling (PD, In progress, v1.2.0-alpha.1) (Pause)
    - [#1651](https://github.com/pingcap/tidb-operator/issues/1651)
    - [#3159](https://github.com/pingcap/tidb-operator/issues/3159)

## Improvements

## Bug Fixes

## Other Notable Changes

- Optimize CR syncing intervals ([#3700](https://github.com/pingcap/tidb-operator/pull/3700), [@dragonly](https://github.com/dragonly))
- Change the directory to save the customized alert rules in TidbMonitor from `tidb:${tidb_image_version}` to `tidb:${initializer_image_version}`. Please note that if the `spec.initializer.version` in the TidbMonitor does not match with the TiDB version in the TidbCluster, upgrade TiDB Operator will cause the re-creation of the monitor Pod ([#3684](https://github.com/pingcap/tidb-operator/pull/3684), [@BinChenn](https://github.com/BinChenn))
- Add local backend support for the TiDB-Lightning chart ([#3644](https://github.com/pingcap/tidb-operator/pull/3644), [@csuzhangxc](https://github.com/csuzhangxc))
- Supports to persist checkpoint for TiDB-Lightning helm chart ([#3653](https://github.com/pingcap/tidb-operator/pull/3653), [@csuzhangxc](https://github.com/csuzhangxc))
- Support thanos sidecar and can use thanos to do multiple cluster monitoring and management. ([#3579](https://github.com/pingcap/tidb-operator/pull/3579), [@mikechengwei](https://github.com/mikechengwei))
