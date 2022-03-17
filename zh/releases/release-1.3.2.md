---
title: TiDB Operator 1.3.2 Release Notes
---

# TiDB Operator 1.3.2 Release Notes

发布日期: 2022 年 3 月 17 日

TiDB Operator 版本：1.3.2

## 优化提升

- 支持在启用了 Istio 的 Kubernetes 集群上部署与运行 TiDB ([#4445](https://github.com/pingcap/tidb-operator/pull/4445), [@rahilsh](https://github.com/rahilsh))
- 支持包括 ARM 系统架构在内的多架构 Docker 镜像 ([#4469](https://github.com/pingcap/tidb-operator/pull/4469), [@better0332](https://github.com/better0332))

## Bug 修复

- 修复 Discovery 服务错误导致 TiDB 集群 PD 组件启动失败的问题 ([#4440](https://github.com/pingcap/tidb-operator/pull/4440), [@liubog2008](https://github.com/liubog2008))