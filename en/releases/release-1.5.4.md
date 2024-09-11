---
title: TiDB Operator 1.5.4 Release Notes
summary: Learn about new features and bug fixes in TiDB Operator 1.5.4.
---

# TiDB Operator 1.5.4 Release Notes

Release date: September 13, 2024

TiDB Operator version: 1.5.4

## Improvements

- VolumeReplace feature supports customizing the number of spare replicas used during TiKV or PD disk replacements ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- VolumeReplace feature supports only enabling for specified TiDB clusters ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- EBS Snapshot restore supports to configure if warmup failure on individual volume fails the restore instantly ([#5635](https://github.com/pingcap/tidb-operator/pull/5635), [@michealdeng](https://github.com/michealdeng))
- Gate EBS Snapshot restore failure on warmup failure only for `check-wal-only` warmup strategy ([#5621](https://github.com/pingcap/tidb-operator/pull/5621), [@michealdeng](https://github.com/michealdeng))

## Bug fixes

- Fix the issue that tidb-backup-manager can't parse files storage size from BR backupmeta v2 ([#5411](https://github.com/pingcap/tidb-operator/pull/5411), [@Leavrth](https://github.com/Leavrth))
- Fix the issue that EBS may leak after EBS snapshot restore fails ([#5634](https://github.com/pingcap/tidb-operator/pull/5634), [@WangLe1321](https://github.com/WangLe1321))
- Fix the issue that the metrics are not initialized after the federated manager restarts ([#5637](https://github.com/pingcap/tidb-operator/pull/5637), [@wxiaomou](https://github.com/wxiaomou))
- Fix the issue that EBS snapshot restore doesn't fail even if no TiKV instance configured or replica is set to 0 ([#5659](https://github.com/pingcap/tidb-operator/pull/5659), [@BornChanger](https://github.com/BornChanger))
