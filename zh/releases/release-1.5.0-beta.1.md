---
title: TiDB Operator 1.5.0-beta.1 Release Notes
---

# TiDB Operator 1.5.0-beta.1 Release Notes

发布日期: 2023 年 4 月 11 日

TiDB Operator 版本：1.5.0-beta.1

## 新功能

- 支持通过给 PD Pod 加上 `tidb.pingcap.com/pd-transfer-leader` Annotation 来优雅重启 PD Pod ([#4896](https://github.com/pingcap/tidb-operator/pull/4896), [@luohao](https://github.com/luohao))

- 支持使用 Advanced StatefulSet 管理 TiCDC ([#4881](https://github.com/pingcap/tidb-operator/pull/4881), [@charleszheng44](https://github.com/charleszheng44))

- 支持使用 Advanced StatefulSet 管理 TiProxy ([#4917](https://github.com/pingcap/tidb-operator/pull/4917), [@xhebox](https://github.com/xhebox))

- TiDB Spec 新增 `bootstrapSQLConfigMapName` 字段，用于指定 TiDB 首次启动时执行的初始 SQL 文件 ([#4862](https://github.com/pingcap/tidb-operator/pull/4862), [@fgksgf](https://github.com/fgksgf))

- 允许用户定义策略来重启失败的备份任务，以提高备份的稳定性 ([#4883](https://github.com/pingcap/tidb-operator/pull/4883), [@WizardXiao](https://github.com/WizardXiao)) ([#4925](https://github.com/pingcap/tidb-operator/pull/4925), [@WizardXiao](https://github.com/WizardXiao))

## 优化提升

- 升级 Kubernetes 依赖库至 v1.20 版本 ([#4954](https://github.com/pingcap/tidb-operator/pull/4954), [@KanShiori](https://github.com/KanShiori))

- 添加与 reconciler 与 worker queue 相关的 Metric 以提高可观测性 ([#4882](https://github.com/pingcap/tidb-operator/pull/4882), [@hanlins](https://github.com/hanlins))

- 在滚动升级 TiKV 节点时，等待当前升级后的 TiKV 节点的 Leader 转移回来后，再升级下一个 TiKV 节点，以降低滚动升级时的性能下降 ([#4863](https://github.com/pingcap/tidb-operator/pull/4863), [@KanShiori](https://github.com/KanShiori))

- 允许用户自定义 Prometheus Scraping 相关配置 ([#4846](https://github.com/pingcap/tidb-operator/pull/4846), [@coderplay](https://github.com/coderplay))

- TiProxy 支持共享部分 TiDB 的证书 ([#4880](https://github.com/pingcap/tidb-operator/pull/4880), [@xhebox](https://github.com/xhebox))

- 当配置 `spec.preferIPv6` 为 `true` 时，所有组件的 Service 的 `ipFamilyPolicy` 将被配置为 `PreferDualStack` ([#4959](https://github.com/pingcap/tidb-operator/pull/4959), [@KanShiori](https://github.com/KanShiori))

## Bug 修复

- 修复了因为 metric 接口冲突而导致 pprof 接口无法访问的问题 ([#4874](https://github.com/pingcap/tidb-operator/pull/4874), [@hanlins](https://github.com/hanlins))
