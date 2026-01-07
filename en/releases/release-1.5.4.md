---
title: TiDB Operator 1.5.4 Release Notes
summary: Learn about improvements and bug fixes in TiDB Operator 1.5.4.
---

# TiDB Operator 1.5.4 Release Notes

Release date: September 13, 2024

TiDB Operator version: 1.5.4

## Improvements

- The VolumeReplace feature supports customizing the number of spare replicas for PD and TiKV ([#5666](https://github.com/pingcap/tidb-operator/pull/5666), [@anish-db](https://github.com/anish-db))
- The VolumeReplace feature can be enabled for specific TiDB clusters ([#5670](https://github.com/pingcap/tidb-operator/pull/5670), [@rajsuvariya](https://github.com/rajsuvariya))
- EBS snapshot restore supports configuring whether to terminate the entire restore task immediately if volume warmup fails ([#5622](https://github.com/pingcap/tidb-operator/pull/5622), [@michaelmdeng](https://github.com/michaelmdeng))
- When using the `check-wal-only` warmup strategy, EBS snapshot restore marks the entire restore task as failed if warmup fails ([#5621](https://github.com/pingcap/tidb-operator/pull/5621), [@michaelmdeng](https://github.com/michaelmdeng))

## Bug fixes

- Fix the issue that `tidb-backup-manager` cannot parse backup file size in BR backupmeta v2 ([#5411](https://github.com/pingcap/tidb-operator/pull/5411), [@Leavrth](https://github.com/Leavrth))
- Fix a potential EBS volume leak issue that occurs when EBS snapshot restore fails ([#5634](https://github.com/pingcap/tidb-operator/pull/5634), [@WangLe1321](https://github.com/WangLe1321))
- Fix the issue that metrics are not properly initialized after federated manager restarts ([#5637](https://github.com/pingcap/tidb-operator/pull/5637), [@wxiaomou](https://github.com/wxiaomou))
- Fix the issue that EBS snapshot restore incorrectly succeeds when no TiKV instances are configured or TiKV replica is set to 0 ([#5659](https://github.com/pingcap/tidb-operator/pull/5659), [@BornChanger](https://github.com/BornChanger))
