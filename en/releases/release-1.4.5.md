---
title: TiDB Operator 1.4.5 Release Notes
summary: TiDB Operator 1.4.5 was released on June 26, 2023. The improvements include adding metrics for TidbCluster reconcile errors, reconciler and worker queue observability, introducing `startUpScriptVersion` field for DM master, and support for rolling restart and scaling-in of TiCDC clusters. Bug fixes include suppressing GC for newly created scheduled backups, making `backupTemplate` optional in backup CR, and fixing issues related to Kubernetes cluster-level permission and `AdditionalVolumeMounts` for TidbCluster.
---

# TiDB Operator 1.4.5 Release Notes

Release date: June 26, 2023

TiDB Operator version: 1.4.5

## Improvements

- Add the metrics for fine-grained TidbCluster reconcile errors ([#4952](https://github.com/pingcap/tidb-operator/pull/4952), [@coderplay](https://github.com/coderplay))
- Add the metrics for the reconciler and worker queue to improve observability ([#4882](https://github.com/pingcap/tidb-operator/pull/4882), [@hanlins](https://github.com/hanlins))
- Introduce `startUpScriptVersion` field for DM master to specify the startup script version ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))
- Add support for rolling restart and scaling-in of TiCDC clusters when deploying TiCDC across multiple kubernetes clusters ([#5040](https://github.com/pingcap/tidb-operator/pull/5040), [@charleszheng44](https://github.com/charleszheng44))

## Bug fixes

- Suppress GC when scheduled backup is newly created ([#4940](https://github.com/pingcap/tidb-operator/pull/4940), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- Make `backupTemplate` optional in backup CR ([#4956](https://github.com/pingcap/tidb-operator/pull/4956), [@Ehco1996](https://github.com/Ehco1996))
- Fix the issue that TiDB Operator panics if no Kubernetes cluster-level permission is configured ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
- Fix the issue that TiDB Operator might panic if `AdditionalVolumeMounts` is set for TidbCluster ([#5058](https://github.com/pingcap/tidb-operator/pull/5058), [@liubog2008](https://github.com/liubog2008))
