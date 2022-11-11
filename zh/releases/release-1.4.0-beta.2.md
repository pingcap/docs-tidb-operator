---
title: TiDB Operator 1.4.0-beta.2 Release Notes
---

# TiDB Operator 1.4.0-beta.2 Release Notes

发布日期：2022 年 11 月 11 日

TiDB Operator 版本：1.4.0-beta.2

## 错误修复

- 修复 `BackupSchedule` 在使用 Azure Blob Storage 时未设置前缀的问题 ([#4767](https://github.com/pingcap/tidb-operator/pull/4767), [@WizardXiao](https://github.com/WizardXiao))

- 升级 aws sdk 到 v1.44.72 以支持 aws 的 region ap-southeast-3 ([#4771](https://github.com/pingcap/tidb-operator/pull/4771), [@WizardXiao](https://github.com/WizardXiao))
