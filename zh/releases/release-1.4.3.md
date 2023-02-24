---
title: TiDB Operator 1.4.3 Release Notes
---

# TiDB Operator 1.4.3 Release Notes

发布日期: 2023 年 2 月 24 日

TiDB Operator 版本：1.4.3

## Bug 修复

- 修复开启 `preferIPv6` 的情况下， TiFlash 的 metric server 没有监听正确的 IPv6 地址的问题 ([#4850](https://github.com/pingcap/tidb-operator/pull/4889), [@KanShiori](https://github.com/KanShiori))

- 修复在 AWS 环境中，如果打开了 feature gate `VolumeModifying` 并且 `StorageClass` 缺少 EBS 相关参数时，TiDB Operator 会一直尝试修改 EBS 参数的问题 ([#4850](https://github.com/pingcap/tidb-operator/pull/4892), [@liubog2008](https://github.com/liubog2008))
