---
title: TiDB Operator 1.5.0-beta.1 Release Notes
---

# TiDB Operator 1.5.0-beta.1 Release Notes

Release date: April 11, 2023

TiDB Operator version: 1.5.0-beta.1

## New Feature

- Support using the `tidb.pingcap.com/pd-transfer-leader` annotation to restart PD Pod gracefully ([#4896](https://github.com/pingcap/tidb-operator/pull/4896), [@luohao](https://github.com/luohao))

- Support using the `tidb.pingcap.com/tidb-graceful-shutdown` annotation to restart TiDB Pod gracefully ([#4948](https://github.com/pingcap/tidb-operator/pull/4948), [@wxiaomou](https://github.com/wxiaomou))

- Support managing TiCDC with Advanced StatefulSet ([#4881](https://github.com/pingcap/tidb-operator/pull/4881), [@charleszheng44](https://github.com/charleszheng44))

- Support managing TiProxy with Advanced StatefulSet ([#4917](https://github.com/pingcap/tidb-operator/pull/4917), [@xhebox](https://github.com/xhebox))

- Add a new field `bootstrapSQLConfigMapName` in the TiDB spec to specify an initialization SQL file on TiDB's first bootstrap ([#4862](https://github.com/pingcap/tidb-operator/pull/4862), [@fgksgf](https://github.com/fgksgf))

- Allow users to define a strategy to restart failed backup jobs, enhancing backup stability ([#4883](https://github.com/pingcap/tidb-operator/pull/4883), [@WizardXiao](https://github.com/WizardXiao)) ([#4925](https://github.com/pingcap/tidb-operator/pull/4925), [@WizardXiao](https://github.com/WizardXiao))

## Improvements

- Upgrade Kubernetes dependencies to v1.20 ([#4954](https://github.com/pingcap/tidb-operator/pull/4954), [@KanShiori](https://github.com/KanShiori))

- Add the metrics for the reconciler and worker queue to improve observability ([#4882](https://github.com/pingcap/tidb-operator/pull/4882), [@hanlins](https://github.com/hanlins))

- When rolling upgrade TiKV Pods, TiDB Operator will wait for the leader to transfer back to the upgraded Pod before upgrading the next TiKV pod. This helps to reduce performance degradation during rolling upgrade ([#4863](https://github.com/pingcap/tidb-operator/pull/4863), [@KanShiori](https://github.com/KanShiori))

- Allow users to customize Prometheus scraping settings ([#4846](https://github.com/pingcap/tidb-operator/pull/4846), [@coderplay](https://github.com/coderplay))

- Support sharing some of TiDB's certificates with TiProxy ([#4880](https://github.com/pingcap/tidb-operator/pull/4880), [@xhebox](https://github.com/xhebox))

- Configure the field `ipFamilyPolicy` as `PreferDualStack` for all components' Services when `spec.preferIPv6` is set to `true` ([#4959](https://github.com/pingcap/tidb-operator/pull/4959), [@KanShiori](https://github.com/KanShiori))

- Add the metrics for counting errors about the reconciliation to improve observability ([#4952](https://github.com/pingcap/tidb-operator/pull/4952), [@coderplay](https://github.com/coderplay))

## Bug fixes

- Fix the issue that pprof endpoint is not reachable because the route conflicts with the metrics endpoint ([#4874](https://github.com/pingcap/tidb-operator/pull/4874), [@hanlins](https://github.com/hanlins))
