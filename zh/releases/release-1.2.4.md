---
title: TiDB Operator 1.2.4 Release Notes
---

# TiDB Operator 1.2.4 Release Notes

发布日期：2021 年 10 月 21 日

TiDB Operator 版本：1.2.4

## 新功能

- TidbMonitor 支持用户挂载 Prometheus 告警规则，并且 TidbMonitor 可以动态重新加载 ([#4180](https://github.com/pingcap/tidb-operator/pull/4180), [@mikechengwei](https://github.com/mikechengwei))

- TidbMonitor 支持 `enableRules` 字段。当没有配置 AlterManager 时，可以配置该字段为 `true` 来为 Prometheus 添加告警规则 ([#4115](https://github.com/pingcap/tidb-operator/pull/4115), [@mikechengwei](https://github.com/mikechengwei))


## 优化提升

- 升级 `TiFlash` 的过程更加的优雅 ([#4193](https://github.com/pingcap/tidb-operator/pull/4193), [@KanShiori](https://github.com/KanShiori))

- 增强清理 `Backup` 备份数据的效率 ([#4095](https://github.com/pingcap/tidb-operator/pull/4095), [@KanShiori](https://github.com/KanShiori))

- 从 TidbMonitor ConfigMap 分离出单独的 Grafana ConfigMap ([#4108](https://github.com/pingcap/tidb-operator/pull/4108), [@mikechengwei](https://github.com/mikechengwei))

## Bug 修复

- 修复镜像中的安全漏洞 ([#4217](https://github.com/pingcap/tidb-operator/pull/4217), [@KanShiori](https://github.com/KanShiori))

- 当 `Backup` 备份运行时被删除，修复 `Backup` 备份数据可能残留的问题 ([#4133](https://github.com/pingcap/tidb-operator/pull/4133), [@KanShiori](https://github.com/KanShiori))

