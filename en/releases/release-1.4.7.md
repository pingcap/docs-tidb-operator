---
title: TiDB Operator 1.4.7 Release Notes
---

# TiDB Operator 1.4.7 Release Notes

Release date: July 26, 2023

TiDB Operator version: 1.4.7

## Improvements

## Bug fixes

- Fix the issue of `Error loading shared library libresolv.so.2` when executing backup and restore with BR >=v6.6.0 ([#4935](https://github.com/pingcap/tidb-operator/pull/4935), [@Ehco1996](https://github.com/Ehco1996))

- Make `logBackupTemplate` optional in BackupSchedule CR ([#5190](https://github.com/pingcap/tidb-operator/pull/5190), [@Ehco1996](https://github.com/Ehco1996))