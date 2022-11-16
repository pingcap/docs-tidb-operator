---
title: TiDB Operator 1.4.0-beta.2 Release Notes
---

# TiDB Operator 1.4.0-beta.2 Release Notes

Release date: November 11, 2022

TiDB Operator version: 1.4.0-beta.2

## Bug fixes

- Fix the issue that `BackupSchedule` does not set prefix when using Azure Blob Storage ([#4767](https://github.com/pingcap/tidb-operator/pull/4767), [@WizardXiao](https://github.com/WizardXiao))

- Upgrade AWS SDK to v1.44.72 to support the Asia Pacific (Jakarta) region (`ap-southeast-3`) in AWS ([#4771](https://github.com/pingcap/tidb-operator/pull/4771), [@WizardXiao](https://github.com/WizardXiao))
