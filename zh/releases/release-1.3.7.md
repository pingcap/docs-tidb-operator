---
title: TiDB Operator 1.3.7 Release Notes
---

# TiDB Operator 1.3.7 Release Notes

发布日期：2022 年 8 月 1 日

TiDB Operator 版本：1.3.7

## 新功能

- 每个组件添加 `suspendAction` 字段，用以暂停任一个组件，暂停组件将会删除对应的 `StatefulSet` ([#4640](https://github.com/pingcap/tidb-operator/pull/4640), [@KanShiori](https://github.com/KanShiori))

## 优化提升

- 在扩容完成组件的所有 PVC 后，重建组件的 `StatefulSet`，使得新的 PVC 使用正确的存储大小 ([#4620](https://github.com/pingcap/tidb-operator/pull/4620), [@KanShiori](https://github.com/KanShiori))

- 为了避免 TiKV PVC 扩容流程卡住，当 leader 驱逐超时后直接继续扩容流程 ([#4625](https://github.com/pingcap/tidb-operator/pull/4625), [@KanShiori](https://github.com/KanShiori))

## 错误修复

- 修复使用本地存储时，无法升级 TiKV 的问题 ([#4615](https://github.com/pingcap/tidb-operator/pull/4615), [@KanShiori](https://github.com/KanShiori))

- 修复清理备份文件后，备份文件可能残留的问题 ([#4617](https://github.com/pingcap/tidb-operator/pull/4617), [@KanShiori](https://github.com/KanShiori))
