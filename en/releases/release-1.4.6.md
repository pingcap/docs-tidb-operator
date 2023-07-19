---
title: TiDB Operator 1.4.6 Release Notes
---

# TiDB Operator 1.4.6 Release Notes

Release date: July 19, 2023

TiDB Operator version: 1.4.6

## Improvements

- Enable volume resizing by default ([#5167](https://github.com/pingcap/tidb-operator/pull/5167), [@liubog2008](https://github.com/liubog2008))

## Bug fixes

- Fix the issue of `Error loading shared library libresolv.so.2` when executing backup and restore with BR >=v6.6.0 ([#4935](https://github.com/pingcap/tidb-operator/pull/4935), [@Ehco1996](https://github.com/Ehco1996))
- Fix the issue that graceful drain for TiCDC does not work if a non-SemVer image tag is used for TiCDC ([#5173](https://github.com/pingcap/tidb-operator/pull/5173), [@csuzhangxc](https://github.com/csuzhangxc))
