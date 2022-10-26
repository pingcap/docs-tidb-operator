---
title: TiDB Operator 1.4.0-beta.1 Release Notes
---

# TiDB Operator 1.4.0-beta.1 Release Notes

发布日期：2022 年 10 月 26 日

TiDB Operator 版本：1.4.0-beta.1


## 新功能

- br: support ebs snapshot ([#4698](https://github.com/pingcap/tidb-operator/pull/4698), [@gozssky](https://github.com/gozssky))


## 错误修复

- 修改 tidb operator 重启时，日志备份的 checkpoint ts 无法更新的问题 ([#4746](https://github.com/pingcap/tidb-operator/pull/4746), [@WizardXiao](https://github.com/WizardXiao))

- 修改 tidb 集群开启 TLS 认证时，日志备份的 checkpoint ts 无法更新的问题 ([#4716](https://github.com/pingcap/tidb-operator/pull/4716), [@WizardXiao](https://github.com/WizardXiao))