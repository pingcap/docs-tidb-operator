---
title: TiDB Operator 1.3.0-beta.1 Release Notes
---
# TiDB Operator 1.3.0-beta.1 Release Notes

发布日期:  2022 年 1 月 12 日

TiDB Operator 版本：1.3.0-beta.1

## 滚动升级改动

- 由于 [#4358](https://github.com/pingcap/tidb-operator/pull/4358) 的变更，如果使用小于或等与 v1.2 operator 部署了 v5.4 版本的 TidbCluster，升级 Operator 到 1.3.0-beta.1 版本会导致 Tiflash 组件滚动升级
- 由于 [#4169](https://github.com/pingcap/tidb-operator/pull/4169) 的变更，如果部署了大于或等于 v5.0.0 版本的 TidbCluster 并且设置了 `seperateRocksDBLog` 字段值为`true`，升级 Operator 到 1.3.0-beta.1 版本会导致 TiKV 组件滚动升级

## 新功能

- 支持为 TiFlash 的 init container 配置资源使用量 ([#4304](https://github.com/pingcap/tidb-operator/pull/4304), [@KanShiori](https://github.com/KanShiori))
- 支持为 TiDB 集群开启[持续性能分析](access-dashboard.md#启用持续性能分析) ([#4287](https://github.com/pingcap/tidb-operator/pull/4287), [@KanShiori](https://github.com/KanShiori))
- 支持通过配置 annotation 的方式优雅重启 TiKV 组件 ([#4279](https://github.com/pingcap/tidb-operator/pull/4279), [@july2993](https://github.com/july2993))
- 支持为 Discovery 组件配置 PodSecurityContext ([#4259](https://github.com/pingcap/tidb-operator/pull/4259), [@csuzhangxc](https://github.com/csuzhangxc))
- 支持为 TidbCluster CR 配置 PodManagementPolicy ([#4211](https://github.com/pingcap/tidb-operator/pull/4211), [@mianhk](https://github.com/mianhk))
- 支持为 Discovery 组件自定义更多配置 ([#4208](https://github.com/pingcap/tidb-operator/pull/4208), [@KanShiori](https://github.com/KanShiori))
- 支持在 TidbMonitor CR 中配置 Prometheus 分片 ([#4198](https://github.com/pingcap/tidb-operator/pull/4198), [@mikechengwei](https://github.com/mikechengwei))
- 支持兼容地使用 `v1` 和 `v1beta1` 版本的 `Ingress` ([#4195](https://github.com/pingcap/tidb-operator/pull/4195), [@KanShiori](https://github.com/KanShiori))

## 优化提升

- 由于 v5.4.0 版本 TiFlash 的配置变动，Operator 中去除和变更了一些 TiFlash 的默认配置。如果使用 v1.2 operator 部署了 v5.4 版本的 TidbCluster，升级 Operator 到 1.3.0-beta.1 版本会导致 Tiflash 组件滚动升级 ([#4358](https://github.com/pingcap/tidb-operator/pull/4358), [@KanShiori](https://github.com/KanShiori))
- 为跨 Kubernetes 集群部署的 TidbCluster 添加 e2e 测试用例([#4354](https://github.com/pingcap/tidb-operator/pull/4354), [#4352](https://github.com/pingcap/tidb-operator/pull/4352), [#4314](https://github.com/pingcap/tidb-operator/pull/4314), [#4300](https://github.com/pingcap/tidb-operator/pull/4300), [@just1900](https://github.com/just1900))
- 为跨 Kubernetes 集群部署的 TidbCluster 添加部署和删除集群的 e2e 测试用例 ([#4289](https://github.com/pingcap/tidb-operator/pull/4289), [@handlerww](https://github.com/handlerww))
- 优化：废弃 pod 的 validating 和 mutating webhook ([#4209](https://github.com/pingcap/tidb-operator/pull/4209), [@mianhk](https://github.com/mianhk))
- 在 TidbMonitor controller 中去除对 firstTC 和 firstDC 的依赖 ([#4272](https://github.com/pingcap/tidb-operator/pull/4272), [@mikechengwei](https://github.com/mikechengwei))
- 当 TidbCluster 是异构或跨集群部署时，从当前的 TidbCluster 中获取 tls 证书 ([#4249](https://github.com/pingcap/tidb-operator/pull/4249), [@KanShiori](https://github.com/KanShiori))
- 分离 dm 和 TidbMonitor 的代码逻辑 ([#4243](https://github.com/pingcap/tidb-operator/pull/4243), [@mikechengwei](https://github.com/mikechengwei))
- 优化 secret 的查询逻辑 ([#4166](https://github.com/pingcap/tidb-operator/pull/4166), [@mianhk](https://github.com/mianhk))
- 优化 TidbMonitor 部署示例 ([#4242](https://github.com/pingcap/tidb-operator/pull/4242), [@mianhk](https://github.com/mianhk))
- 当 Kubernetes 版本高于 v1.19 时，使用 scheduler configuration 来运行 tidb-scheduler ([#4202](https://github.com/pingcap/tidb-operator/pull/4202), [@KanShiori](https://github.com/KanShiori))
- 将 TidbCluster 和与它异构部署的 TidbCluster 的 metrics 集成到同一个 dashboards 中 ([#4210](https://github.com/pingcap/tidb-operator/pull/4210), [@mikechengwei](https://github.com/mikechengwei))
- 当 PD 的副本数小于 2 时，默认强制升级 PD 组件 ([#4107](https://github.com/pingcap/tidb-operator/pull/4107), [@mianhk](https://github.com/mianhk))
- 在 TidbMonitor 中使用 secretRef 来获取 Grafana 的密码([#4135](https://github.com/pingcap/tidb-operator/pull/4135), [@mianhk](https://github.com/mianhk))
- 当 TiKV 的副本数小于 2 时，默认强制升级 TiKV 组件 ([#4091](https://github.com/pingcap/tidb-operator/pull/4091), [@mianhk](https://github.com/mianhk))

## 其他改进

- 将拆分 `pkg/apis` 和 `pkg/client` 为 golang 子模块 ([#4134](https://github.com/pingcap/tidb-operator/pull/4134), [@KanShiori](https://github.com/KanShiori))
- 允许所有组件的最小副本数为 0 ([#4288](https://github.com/pingcap/tidb-operator/pull/4288), [@handlerww](https://github.com/handlerww))
- 使用新版本的 busybox 镜像作为 helper 镜像 ([#4260](https://github.com/pingcap/tidb-operator/pull/4260), [@dveeden](https://github.com/dveeden))
- 升级 Grafana 镜像版本为 7.5.11，提升安全性 ([#4212](https://github.com/pingcap/tidb-operator/pull/4212), [@makocchi-git](https://github.com/makocchi-git))
- 删除不再使用的函数 SyncAutoScalerAnn 和相关代码([#4192](https://github.com/pingcap/tidb-operator/pull/4192), [@mianhk](https://github.com/mianhk))
- 升级 Kubernetes 的依赖为 v1.19.14 ([#4161](https://github.com/pingcap/tidb-operator/pull/4161), [@KanShiori](https://github.com/KanShiori))
- Helm chart 支持配置 tidb-controller-manager 的 workers 数量 ([#4111](https://github.com/pingcap/tidb-operator/pull/4111), [@mianhk](https://github.com/mianhk))
