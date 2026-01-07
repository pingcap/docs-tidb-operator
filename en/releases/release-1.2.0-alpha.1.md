---
title: TiDB Operator 1.2.0-alpha.1 Release Notes
summary: TiDB Operator 1.2.0-alpha.1 was released on January 15, 2021. The update includes the ability to deploy one TiDB cluster across multiple Kubernetes clusters, support for DM 2.0, auto-scaling with PD API, and canary upgrade of TiDB Operator. Improvements include local backend support for the TiDB Lightning chart, TLS support for the TiDB Lightning chart and TiKV Importer chart, persisting checkpoint for TiDB Lightning helm chart, support for Thanos sidecar for monitoring multiple clusters, and migration from Deployment to StatefulSet for TidbMonitor. Other notable changes include optimized rate limiter intervals and changes in the directory to save customized alert rules in TidbMonitor.
---

# TiDB Operator 1.2.0-alpha.1 Release Notes

Release date: January 15, 2021

TiDB Operator version: 1.2.0-alpha.1

## Rolling Update Changes

- Due to [#3440](https://github.com/pingcap/tidb-operator/pull/3440), the Pod of TidbMonitor will be deleted and recreated after TiDB Operator is upgraded to v1.2.0-alpha.1.

## New Features

- Deploy one TiDB cluster across multiple Kubernetes clusters ([@L3T](https://github.com/L3T), [@handlerww](https://github.com/handlerww))
- Support DM 2.0 in TiDB Operator ([@lichunzhu](https://github.com/lichunzhu), [@BinChenn](https://github.com/BinChenn))
- Auto-Scaling with PD API ([@howardlau1999](https://github.com/howardlau1999))
- Canary Upgrade of TiDB Operator ([#3548](https://github.com/pingcap/tidb-operator/pull/3548), [@shonge](https://github.com/shonge), [#3554](https://github.com/pingcap/tidb-operator/pull/3554), [@cvvz](https://github.com/cvvz))

## Improvements

- Add local backend support for the TiDB Lightning chart ([#3644](https://github.com/pingcap/tidb-operator/pull/3644), [@csuzhangxc](https://github.com/csuzhangxc))
- Add TLS support for the TiDB Lightning chart and TiKV Importer chart ([#3598](https://github.com/pingcap/tidb-operator/pull/3598), [@csuzhangxc](https://github.com/csuzhangxc))
- Support persisting checkpoint for TiDB Lightning helm chart ([#3653](https://github.com/pingcap/tidb-operator/pull/3653), [@csuzhangxc](https://github.com/csuzhangxc))
- Support Thanos sidecar for monitoring multiple clusters ([#3579](https://github.com/pingcap/tidb-operator/pull/3579), [@mikechengwei](https://github.com/mikechengwei))
- Migrate from Deployment to StatefulSet for TidbMonitor ([#3440](https://github.com/pingcap/tidb-operator/pull/3440), [@mikechengwei](https://github.com/mikechengwei))

## Other Notable Changes

- Optimize rate limiter intervals ([#3700](https://github.com/pingcap/tidb-operator/pull/3700), [@dragonly](https://github.com/dragonly))
- Change the directory to save the customized alert rules in TidbMonitor from `tidb:${tidb_image_version}` to `tidb:${initializer_image_version}`. Please note that if the `spec.initializer.version` in the TidbMonitor does not match with the TiDB version in the TidbCluster, upgrading TiDB Operator will cause the re-creation of the monitor Pod ([#3684](https://github.com/pingcap/tidb-operator/pull/3684), [@BinChenn](https://github.com/BinChenn))
