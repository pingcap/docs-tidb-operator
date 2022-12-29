---
title: What's New in TiDB Operator 1.4
---

# What's New in TiDB Operator 1.4

TiDB Operator 1.4 introduces the following key features, which helps you manage TiDB clusters and the tools more easily in terms of extensibility and usability.

## Compatibility changes

Due to the change in [#4683](https://github.com/pingcap/tidb-operator/pull/4683), the feature of modifying storage is disabled by default. If you want to resize the PVC for a component, you need to first enable this feature.

## Rolling upgrade changes

Due to the change in [#4493](https://github.com/pingcap/tidb-operator/pull/4494), if you deploy TiCDC without setting the `log-file` configuration item, the rolling upgrade of TiDB Operator to v1.4.0-alpha.1 and later versions will cause TiCDC to be rolling recreated.

## Extensibility

- Support managing [TiDB Dashboard](https://github.com/pingcap/tidb-dashboard) in a separate `TidbDashboard` CRD.
- Support backup and restore based on Amazon EBS volume-snapshot.
- Support scaling in or out multiple TiKV and TiFlash Pods at the same time.
- Support restoring a cluster to a specific time point from a snapshot backup or a log backup using BR.
- Support modifying the IOPS and throughput of AWS EBS storage used by a TiDB cluster.
- Support [TiProxy](https://github.com/pingcap/tiproxy) as an experimental feature.

## Usability

- Support configuring Liveness Probe for TiKV and PD.
- Support automatically setting the location labels for TiDB.
- Support mapping the short labels in the PD location labels to the well-known Kubernetes labels.
- Support customizing the Pod container configuration using the `additionalContainers` field.
- Support configuring the `--check-requirements` parameter for BR.
- Add metric port for TiFlash `Service`.
