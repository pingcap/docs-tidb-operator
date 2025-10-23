---
title: TiDB Operator 1.6.3 Release Notes
summary: 了解 TiDB Operator 1.6.3 版本的新功能。
---

# TiDB Operator 1.6.3 Release Notes

发布日期：2025 年 10 月 18 日

TiDB Operator 版本：1.6.4

## 新功能

- 增加定期与内核同步的功能。如果 Operator 状态与内核不一致，Operator 会修改 logBackup CR 的状态，并在后续的 Reconcile 中尝试与内核同步（最终使内核达到期望状态）。 ([#6300](https://github.com/pingcap/tidb-operator/pull/6147), [@RidRisR](https://github.com/RidRisR))