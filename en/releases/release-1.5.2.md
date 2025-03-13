---
title: TiDB Operator 1.5.2 Release Notes
summary: TiDB Operator 1.5.2 released on January 19, 2024. New features include support for backing up and restoring data of a TiDB cluster across multiple AWS Kubernetes clusters to AWS storage using EBS volume snapshots. Improvements include better support for scenarios such as Stale Read and explicitly specifying PD addresses. Bug fixes address issues with changing meta information and PD member labels.
---

# TiDB Operator 1.5.2 Release Notes

Release date: January 19, 2024

TiDB Operator version: 1.5.2

## New features

Starting from v1.5.2, TiDB Operator supports backing up and restoring the data of a TiDB cluster deployed across multiple AWS Kubernetes clusters to AWS storage using EBS volume snapshots. For more information, refer to [Back up Data Using EBS Snapshots across Multiple Kubernetes](../backup-by-ebs-snapshot-across-multiple-kubernetes.md) and [Restore Data Using EBS Snapshots across Multiple Kubernetes](../restore-from-ebs-snapshot-across-multiple-kubernetes.md). ([#5003](https://github.com/pingcap/tidb-operator/pull/5003), [@BornChanger](https://github.com/BornChanger), [@WangLe1321](https://github.com/WangLe1321), [@YuJuncen](https://github.com/YuJuncen), [@csuzhangxc](https://github.com/csuzhangxc))

## Improvements

- `startScriptVersion: v2` supports waiting for Pod IP to match the one published to external DNS before starting a PD or TiKV to better support scenarios such as Stale Read ([#5381](https://github.com/pingcap/tidb-operator/pull/5381), [@smineyev81](https://github.com/smineyev81))
- `startScriptVersion: v2` supports explicitly specifying PD addresses to better support scenarios where a TiDB cluster is deployed across Kubernetes ([#5400](https://github.com/pingcap/tidb-operator/pull/5400), [@smineyev81](https://github.com/smineyev81))
- tidb-operator Helm Chart supports specifying resource lock for leader election when deploying Advanced StatefulSet ([#5448](https://github.com/pingcap/tidb-operator/pull/5448), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug fixes

- Fix the issue that changing meta information such as annotations and replacing volumes at the same time might cause a deadlock for TiDB Operator reconcile ([#5382](https://github.com/pingcap/tidb-operator/pull/5382), [@anish-db](https://github.com/anish-db))
- Fix the issue that the PD member might be set to the wrong label when replacing volumes ([#5393](https://github.com/pingcap/tidb-operator/pull/5393), [@anish-db](https://github.com/anish-db))
