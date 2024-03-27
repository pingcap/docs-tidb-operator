---
title: TiDB Operator 1.6.0-beta.1 Release Notes
summary: 了解 TiDB Operator 1.6.0-beta.1 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.0-beta.1 Release Notes

发布日期：2024 年 3 月 27 日

TiDB Operator 版本：1.6.0-beta.1

## 新功能

- 支持以[微服务模式](https://docs.pingcap.com/zh/tidb/dev/pd-microservices)部署 PD v8.0.0 及以上版本（实验特性）([#5398](https://github.com/pingcap/tidb-operator/pull/5398), [@HuSharp](https://github.com/HuSharp))
- 支持对 TiDB 组件进行并行的扩容与缩容操作 ([#5570](https://github.com/pingcap/tidb-operator/pull/5570), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 Discovery 组件设置 `livenessProbe` 与 `readinessProbe` ([#5565](https://github.com/pingcap/tidb-operator/pull/5565), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TiDB 组件设置 `startupProbe` ([#5588](https://github.com/pingcap/tidb-operator/pull/5588), [@fgksgf](https://github.com/fgksgf))

## 优化提升

- 升级 Kubernetes 依赖库至 v1.28 版本，建议不再部署 tidb-scheduler ([#5495](https://github.com/pingcap/tidb-operator/pull/5495), [@csuzhangxc](https://github.com/csuzhangxc))
- 通过 Helm Chart 部署时支持设置 tidb-controller-manager 用于 leader 选举的 lock resource，默认值为 `.Values.controllerManager.leaderResourceLock: leases`。当从 v1.6 之前的版本升级到 v1.6.0-beta.1 及之后的版本时，推荐先设置 `.Values.controllerManager.leaderResourceLock: endpointsleases` 并待新的 tidb-controller-manager 正常运行后再设置为 `.Values.controllerManager.leaderResourceLock: leases` 以更新部署 ([#5450](https://github.com/pingcap/tidb-operator/pull/5450), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TiFlash 直接挂载 ConfigMap 而不再依赖 InitContainer 对配置文件进行处理 ([#5552](https://github.com/pingcap/tidb-operator/pull/5552), [@ideascf](https://github.com/ideascf))
- 增加对 TiFlash `storageClaims` 配置中 `resources.request.storage` 的检查 ([#5489](https://github.com/pingcap/tidb-operator/pull/5489), [@unw9527](https://github.com/unw9527))

## Bug 修复

- 修复滚动重启 TiKV 时，没有对最后一个 TiKV Pod 执行 `tikv-min-ready-seconds` 检查的问题 ([#5544](https://github.com/pingcap/tidb-operator/pull/5544), [@wangz1x](https://github.com/wangz1x))
- 修复仅能使用非 `cluster.local` clusterDomain 的 TLS 证书时 TiDB 集群无法启动的问题 ([#5560](https://github.com/pingcap/tidb-operator/pull/5560), [@csuzhangxc](https://github.com/csuzhangxc))
