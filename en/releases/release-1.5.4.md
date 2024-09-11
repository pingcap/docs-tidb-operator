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

## Bug fixes

- Fix the issue that tidb-backup-manager can't parse files storage size from BR backupmeta v2 ([#5411](https://github.com/pingcap/tidb-operator/pull/5411), [@Leavrth](https://github.com/Leavrth))
- cleanup EBS volumes if EBS snapshot restore fails ([#5639](https://github.com/pingcap/tidb-operator/pull/5639), [@WangLe1321](https://github.com/WangLe1321))
- Reset metrics when federated manager restarts ([#5648](https://github.com/pingcap/tidb-operator/pull/5648), [@wxiaomou](https://github.com/wxiaomou))
- Enhance TC check for EBS Snapshot and fail EBS snapshot backup if no TiKV nodes or replica is 0 ([#5662](https://github.com/pingcap/tidb-operator/pull/5662), [@BornChanger ](https://github.com/BornChanger))
