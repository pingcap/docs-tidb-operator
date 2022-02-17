---
title: TiDB Operator 1.2.7 Release Notes
---
# TiDB Operator 1.2.7 Release Notes

发布日期：2022 年 2 月 17 日

TiDB Operator 版本：1.2.7

## 新功能

- 添加新的 `sepc.pd.startUpScriptVersion` 字段，以支持在 PD 启动脚本中使用 `dig` 命令而不是 `nslookup` 命令来解析域名 ([#4379](https://github.com/pingcap/tidb-operator/pull/4379), [@july2993](https://github.com/july2993))

## 优化提升

- 部署或更新组件的 StatefulSet 预先检查配置的 VolumeMount 是否存在，防止集群进行失败的滚动更新 ([#4369](https://github.com/pingcap/tidb-operator/pull/4369), [@july2993](https://github.com/july2993))