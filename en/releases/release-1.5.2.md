---
title: TiDB Operator 1.5.2 Release Notes
---

# TiDB Operator 1.5.2 Release Notes

Release date: January 19, 2023

TiDB Operator version: 1.5.2

## New features

- Support replacing volumes for PD, TiKV, and TiDB ([#5150](https://github.com/pingcap/tidb-operator/pull/5150), [@anish-db](https://github.com/anish-db))

## Improvements

- `startScriptVersion: v2` supports waiting for Pod IP to match the one published to external DNS before starting a PD or TiKV to better support scenarios such as Stale Read ([#5381](https://github.com/pingcap/tidb-operator/pull/5381), [@smineyev81](https://github.com/smineyev81))
- `startScriptVersion: v2` supports explicitly specifying PD addresses to better support scenarios where TiDB clusters are deployed across Kubernetes ([#5400](https://github.com/pingcap/tidb-operator/pull/5400), [@smineyev81](https://github.com/smineyev81))
- tidb-operator Helm Chart supports specify resource lock for leader election when deploying Advanced-StatefulSet ([#5448](https://github.com/pingcap/tidb-operator/pull/5448), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug fixes

- Fixed the issue that changing meta information such as annotations and replacing volume at the same time may cause a deadlock for TiDB Operator reconcile ([#5382](https://github.com/pingcap/tidb-operator/pull/5382), [@anish-db](https://github.com/anish-db))
- Fixed the issue that the PD member might be set the wrong label when replacing volume ([#5393](https://github.com/pingcap/tidb-operator/pull/5393), [@anish-db](https://github.com/anish-db))
