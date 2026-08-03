---
title: TiDB Operator 1.6.6 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.6.
---

# TiDB Operator 1.6.6 Release Notes

Release date: August 3, 2026

TiDB Operator version: 1.6.6

## New features

- Support configuring `securityContext` for containers of TiDB cluster components ([#6404](https://github.com/pingcap/tidb-operator/pull/6404), [@fgksgf](https://github.com/fgksgf))
- Support configuring `automountServiceAccountToken` for TiDB cluster component Pods ([#6764](https://github.com/pingcap/tidb-operator/pull/6764), [@liubog2008](https://github.com/liubog2008))
- Support enabling mTLS for the `discovery` component ([#6781](https://github.com/pingcap/tidb-operator/pull/6781), [@liubog2008](https://github.com/liubog2008))
- Support specifying `serviceAccountName` for `TidbInitializer` ([#6872](https://github.com/pingcap/tidb-operator/pull/6872), [@tennix](https://github.com/tennix))
- Support configuring `automountServiceAccountToken` for `TidbMonitor` ([#6906](https://github.com/pingcap/tidb-operator/pull/6906), [@tennix](https://github.com/tennix))

## Improvements

- Support the `BashShebang` and `NoWaitDNS` flags to separately control whether component startup scripts use Bash shebangs and whether to skip DNS readiness checks ([#6767](https://github.com/pingcap/tidb-operator/pull/6767), [@liubog2008](https://github.com/liubog2008))
- Replace wildcard resource and action permissions in Helm chart RBAC rules with explicit configurations ([#6762](https://github.com/pingcap/tidb-operator/pull/6762), [@liubog2008](https://github.com/liubog2008))
- Support explicitly mounting ServiceAccount tokens for the BR and `discovery` components when `automountServiceAccountToken` is disabled. This improvement enables TiDB Operator to run in restricted environments, such as FedRAMP/Gatekeeper environments that enforce the `block-automount-serviceaccount-token-pod` policy ([#6815](https://github.com/pingcap/tidb-operator/pull/6815), [@liubog2008](https://github.com/liubog2008))
- Add projected ServiceAccount token volume support for `controller-manager`, so that controller-manager can still authenticate to the Kubernetes API when `automountServiceAccountToken` is disabled ([#6873](https://github.com/pingcap/tidb-operator/pull/6873), [@tennix](https://github.com/tennix))
- Pause user DDL operations during eligible TiDB upgrades by calling the TiDB smooth upgrade API (`/upgrade/start` and `/upgrade/finish`), reducing the impact of DDL operations on rolling upgrades and improving upgrade stability ([#6904](https://github.com/pingcap/tidb-operator/pull/6904), [@tennix](https://github.com/tennix))
- Record the IDs of the last 10 BR operations in the `Backup` and `Restore` status fields, making it easier to correlate Kubernetes backup and restore tasks with BR-side diagnostics and lock metadata ([#6954](https://github.com/pingcap/tidb-operator/pull/6954), [@RidRisR](https://github.com/RidRisR))

## Bug fixes

- Fix the issue that the `--stderrthreshold` flag does not take effect when `--logtostderr` is enabled ([#6786](https://github.com/pingcap/tidb-operator/pull/6786), [@pierluigilenoci](https://github.com/pierluigilenoci))
- Fix the issue that the `TidbInitializer` job Pod does not disable ServiceAccount token automount as expected, which causes the Pod to fail the FedRAMP/Gatekeeper `block-automount-serviceaccount-token-pod` policy check ([#6838](https://github.com/pingcap/tidb-operator/pull/6838), [@tennix](https://github.com/tennix))
- Fix an issue where backup and restore jobs using GKE Workload Identity Federation could not access Google Cloud Storage because TiDB Operator referenced an empty service account credential file ([#6888](https://github.com/pingcap/tidb-operator/pull/6888), [@Leavrth](https://github.com/Leavrth))
- Fix the `TidbMonitor` reconciliation failure (`Invalid Semantic version`) that occurs when the Prometheus image tag is not semver-compatible and `remote_write` is not configured. Previously, the system unconditionally parsed the image tag as a semantic version, even though the parsed result is only used when processing the `remote_write` configuration ([#7007](https://github.com/pingcap/tidb-operator/pull/7007), [@time-and-fate](https://github.com/time-and-fate))
