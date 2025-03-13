---
title: TiDB Operator 1.3.3 Release Notes
summary: TiDB Operator 1.3.3 was released on May 17, 2022. The new feature includes adding a new field to customize the tidb service port. Several bug fixes were made, including fixing issues with leader scheduler leakage, incompatibility with ARM architecture, panic when tidb Service has no Endpoints, and loss of Labels and Annotations after TiDB Operator fails to access the Kubernetes server.
---

# TiDB Operator 1.3.3 Release Notes

Release date: May 17, 2022

TiDB Operator version: 1.3.3

## New Feature

- Add a new field `spec.tidb.service.port` to customize the tidb service port ([#4512](https://github.com/pingcap/tidb-operator/pull/4512), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue that evict leader scheduler may leak during cluster upgrade ([#4522](https://github.com/pingcap/tidb-operator/pull/4522), [@KanShiori](https://github.com/KanShiori))

- Update the base image of `tidb-backup-manager` to fix incompatibility with ARM architecture ([#4490](https://github.com/pingcap/tidb-operator/pull/4490), [@better0332](https://github.com/better0332))

- Fix the issue that TiDB Operator may panic when tidb Service does not have any Endpoints ([#4500](https://github.com/pingcap/tidb-operator/pull/4500), [@mikechengwei](https://github.com/mikechengwei))

- Fix the issue that Labels and Annotations of the component Pods may be lost after TiDB Operator fails to access the Kubernetes server and retries ([#4498](https://github.com/pingcap/tidb-operator/pull/4498), [@duduainankai](https://github.com/duduainankai))
