---
title: TiDB Operator 1.5.2 Release Notes
summary: TiDB Operator 1.5.2 版本新增了对 AWS EBS 快照的备份能力的跨多个 K8S 集群的支持。优化了重启 PD、TiKV 时的启动流程，修复了替换 volume 时可能出现的问题。
---

# TiDB Operator 1.5.2 Release Notes

发布日期：2024 年 1 月 19 日

TiDB Operator 版本：1.5.2

## 新功能

从 v1.5.2 起，TiDB Operator 支持基于 AWS EBS 快照的备份能力的跨多个 K8S 集群的备份恢复。更多详情，请查看文档 [Back up Data Using EBS Snapshots across Multiple Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/backup-by-ebs-snapshot-across-multiple-kubernetes) 和 [Restore Data Using EBS Snapshots across Multiple Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/restore-from-ebs-snapshot-across-multiple-kubernetes)。([#5003](https://github.com/pingcap/tidb-operator/pull/5003), [@BornChanger](https://github.com/BornChanger), [@WangLe1321](https://github.com/WangLe1321), [@YuJuncen](https://github.com/YuJuncen), [@csuzhangxc](https://github.com/csuzhangxc))

## 优化提升

- `startScriptVersion: v2` 支持在重启 PD、TiKV 时等待 Pod IP 与 DNS 解析一致后再进行启动以更好地支持 Stale Read 等场景 ([#5381](https://github.com/pingcap/tidb-operator/pull/5381), [@smineyev81](https://github.com/smineyev81))
- `startScriptVersion: v2` 支持显式指定 PD 地址以更好地支持跨 Kubernetes 部署 TiDB 集群的场景 ([#5400](https://github.com/pingcap/tidb-operator/pull/5400), [@smineyev81](https://github.com/smineyev81))
- tidb-operator Helm Chart 支持在部署 Advanced-StatefulSet 时指定 leader election 的 resource lock ([#5448](https://github.com/pingcap/tidb-operator/pull/5448), [@csuzhangxc](https://github.com/csuzhangxc))

## Bug 修复

- 修复同时变更 annotation 等 meta 信息以及替换 volume 时可能造成 TiDB Operator reconcile 死锁的问题 ([#5382](https://github.com/pingcap/tidb-operator/pull/5382), [@anish-db](https://github.com/anish-db))
- 修复替换 volume 时可能给 PD member 设置错误的 label 的问题 ([#5393](https://github.com/pingcap/tidb-operator/pull/5393), [@anish-db](https://github.com/anish-db))
