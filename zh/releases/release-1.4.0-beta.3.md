---
title: TiDB Operator 1.4.0-beta.3 Release Notes
---

# TiDB Operator 1.4.0-beta.3 Release Notes

发布日期：2022 年 12 月 2 日

TiDB Operator 版本：1.4.0-beta.3

## 新功能

- 实验性支持 TiProxy ([#4693](https://github.com/pingcap/tidb-operator/pull/4693)), [@xhebox](https://github.com/xhebox)

- 基于 Amazon EBS 的 TiDB 集群 volume-snapshot 备份和恢复 GA ([#4784](https://github.com/pingcap/tidb-operator/pull/4784), [@fengou1](https://github.com/fengou1))，此功能有以下特点：

    - 将备份对 QPS 的影响降至小于 5%
    - 快速备份和恢复，比如 1 小时内完成备份，2 小时内完成恢复。

## 错误修复

- 修复错误信息中的拼写错误 ([#4773](https://github.com/pingcap/tidb-operator/pull/4773), [@dveeden](https://github.com/dveeden))

- 修复清理卷快照备份失败的问题 ([#4783](https://github.com/pingcap/tidb-operator/pull/4783), [@fengou1](https://github.com/fengou1))

- 修复大规模 TiKV 节点 (40+) 下备份 TiDB 集群失败的问题 ([#4784](https://github.com/pingcap/tidb-operator/pull/4784), [@fengou1](https://github.com/fengou1))
