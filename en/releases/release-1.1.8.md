---
title: TiDB Operator 1.1.8 Release Notes
---

# TiDB Operator 1.1.8 Release Notes

Release date: December 18, 2020

TiDB Operator version: 1.1.8

## New Features

- Support arbitrary Volume and VolumeMount for `PD`, `TiDB`, `TiKV`, `TiFlash`, `Backup` and `Restore`, which enables using NFS or any other kubernetes supported volume source for backup/restore workflow. ([#3517](https://github.com/pingcap/tidb-operator/pull/3517), [@dragonly](https://github.com/dragonly))

## Improvements

- Support cluster and client TLS for `tidb-lightning` and `tikv-importer` helm charts. ([#3598](https://github.com/pingcap/tidb-operator/pull/3598), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting additional ports for the TiDB service. Users can utilize this feature to implement customized services, e.g. additional health check. ([#3599](https://github.com/pingcap/tidb-operator/pull/3599), [@handlerww](https://github.com/handlerww))
- Support skipping TLS when connecting `TidbInitializer` to TiDB Server. ([#3564](https://github.com/pingcap/tidb-operator/pull/3564), [@LinuxGit](https://github.com/LinuxGit))
- Support tableFilters for restoring with TiDB-Lightning. ([#3521](https://github.com/pingcap/tidb-operator/pull/3521), [@sstubbs](https://github.com/sstubbs))
- Support monitor multiple TiDB clusters. ([#3622](https://github.com/pingcap/tidb-operator/pull/3622), [@mikechengwei](https://github.com/mikechengwei))

    ACTION REQUIRED: If `TidbMonitor` CRs are deployed, please update the `spec.initializer.version` to `v4.0.9` after upgrading TiDB Operator to v1.1.8, or some metrics will not be shown correctly in the Grafana dashboards. Scrape job names are changed from `${component}` to `${namespace}-${TidbCluster Name}-${component}`.
- `component` label is added to the scrape jobs of Prometheus in `TidbMonitor`. ([#3609](https://github.com/pingcap/tidb-operator/pull/3609), [@mikechengwei](https://github.com/mikechengwei))

## Bug Fixes

- Fix the issue that TiDB cluster fails to deploy if `spec.tikv.storageVolumes` is configured. ([#3586](https://github.com/pingcap/tidb-operator/pull/3586), [@mikechengwei](https://github.com/mikechengwei))
- Fix codecs error for non-ASCII char password in `TidbInitializer` job. ([#3569](https://github.com/pingcap/tidb-operator/pull/3569), [@handlerww](https://github.com/handlerww))
- Fix the issue that TiFlash pods are recognized as TiKV pods. The original issue can potentially cause TiDB Operator to scale in TiKV pods to a number less than `tikv.replicas`, which there are TiFlash pods in the `TidbCluster`. ([#3514](https://github.com/pingcap/tidb-operator/pull/3514), [@handlerww](https://github.com/handlerww))
- Fix the issue that syncing `Backup` CR will crash `tidb-controller-manager` pod when TLS client is enabled for TiDB. ([#3535](https://github.com/pingcap/tidb-operator/pull/3535), [@dragonly](https://github.com/dragonly))
- Fix the issue that TiDB-Lighting doesn't log to stdout ([#3617](https://github.com/pingcap/tidb-operator/pull/3617), [@csuzhangxc](https://github.com/csuzhangxc))
