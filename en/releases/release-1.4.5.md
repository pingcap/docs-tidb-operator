---
title: TiDB Operator 1.4.5 Release Notes
---

# TiDB Operator 1.4.5 Release Notes

Release date: June TODO, 2023

TiDB Operator version: 1.4.5

## Improvements

- Add the metrics for fine-grained TidbCluster reconcile errors ([#4952](https://github.com/pingcap/tidb-operator/pull/4952), [@coderplay](https://github.com/coderplay))
- Add the metrics for the reconciler and worker queue to improve observability ([#4882](https://github.com/pingcap/tidb-operator/pull/4882), [@hanlins](https://github.com/hanlins))
- Introduce `startUpScriptVersion` field for DM master to specify startup script version ([#4971](https://github.com/pingcap/tidb-operator/pull/4971), [@hanlins](https://github.com/hanlins))

## Bug fixes

- Supress GC when scheduled backup is newly created ([#4940](https://github.com/pingcap/tidb-operator/pull/4940), [@oliviachenairbnb](https://github.com/oliviachenairbnb))
- Make `backupTemplate` optional in backup CR ([#4956](https://github.com/pingcap/tidb-operator/pull/4956), [@Ehco1996](https://github.com/Ehco1996))
