---
title: TiDB Operator 1.6.4 Release Notes
summary: 了解 TiDB Operator 1.6.4 版本的新功能。
---

# TiDB Operator 1.6.4 Release Notes

发布日期：2025 年 12 月 2 日

TiDB Operator 版本：1.6.4

## 新功能

- 日志备份新增定期状态同步机制。当 TiDB Operator 的状态与 TiDB 集群底层备份任务的实际状态不一致时，TiDB Operator 会更新 `logBackup` CR 的状态，并在后续 Reconcile 过程中尝试与底层状态同步，直至达到预期状态。([#6147](https://github.com/pingcap/tidb-operator/pull/6147), [@RidRisR](https://github.com/RidRisR))