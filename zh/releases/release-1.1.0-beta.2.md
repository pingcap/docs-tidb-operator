---
title: TiDB Operator 1.1 Beta.2 Release Notes
---

# TiDB Operator 1.1 Beta.2 Release Notes

发布日期：2020 年 9 月 15 日

TiDB Operator 版本：1.1.0-beta.2

## 需要采取的行动

- `--default-storage-class-name` 和 `--default-backup-storage-class-name` 已经废弃，现在默认的 storage class 使用的就是 Kubernetes default storage class。如果你曾经将 default storage class 设置为 Kubernetes default storage class 之外的选项，请显示得在 TiDB 集群的 `helm` 或者 YAML 文件中进行设定。([#1581](https://github.com/pingcap/tidb-operator/pull/1581), [@cofyc](https://github.com/cofyc))

## 其他值得注意的改变

- 允许用户为备份和恢复设置亲和性和容忍度 ([#1737](https://github.com/pingcap/tidb-operator/pull/1737), [@Smana](https://github.com/Smana))
- 允许 `AdvancedStatefulSet` 和 `Admission Webhook` 一起使用 ([#1640](https://github.com/pingcap/tidb-operator/pull/1640), [@Yisaer](https://github.com/Yisaer))
- 为自定义的资源增加了一个基本的部署 TiDB 集群的样例 ([#1573](https://github.com/pingcap/tidb-operator/pull/1573), [@aylei](https://github.com/aylei))
- 支持基于 CPU 平均负载的集群自动扩容特性 ([#1731](https://github.com/pingcap/tidb-operator/pull/1731), [@Yisaer](https://github.com/Yisaer))
- 支持数据库与客户端之间用户自定义证书 ([#1714](https://github.com/pingcap/tidb-operator/pull/1714), [@weekface](https://github.com/weekface))
- 为 `tidb-back` 增加一个可以重用已有的 PVC 来恢复集群的选项 ([#1708](https://github.com/pingcap/tidb-operator/pull/1708), [@mightyguava](https://github.com/mightyguava))
- 为 `tidb-backup` 增加 `resources`，`imagePullPolicy` 和 `nodeSelector` 字段 ([#1705](https://github.com/pingcap/tidb-operator/pull/1705), [@mightyguava](https://github.com/mightyguava))
- 为 TiDB server 的证书增加更多的 SANs（Subject Alternative Name） ([#1702](https://github.com/pingcap/tidb-operator/pull/1702), [@weekface](https://github.com/weekface))
- 当 `AdvancedStatfulSet` 开启时，支持自动迁移已有的 `Kubernetes StatefulSets` 到 `Advanced StatefulSets` ([#1580](https://github.com/pingcap/tidb-operator/pull/1580), [@cofyc](https://github.com/cofyc))
- 修复了 `admission webhook` 导致删除 PD pod 失败并且允许在 PVC 找不到的情况下，删除 PD 到 TiKV 之间的 pod ([#1568](https://github.com/pingcap/tidb-operator/pull/1568), [@Yisaer](https://github.com/Yisaer))
- 限制 PD 和 TiKV 的重启频率，同时只允许一个实例进行重启 ([#1532](https://github.com/pingcap/tidb-operator/pull/1532), [@Yisaer](https://github.com/Yisaer))
- 为 `TidbMonitor` 增加默认的与它部署相同的 `ClusterRef` 命名空间，并且修复当 `Spec.PrometheusSpec.logLevel` 丢失的时候，`TidbMonitor` 的 pod 不能被创建出来的问题 ([#1500](https://github.com/pingcap/tidb-operator/pull/1500), [@Yisaer](https://github.com/Yisaer))
- 优化 `TidbMonitor` 和 `TidbInitializer` controller 的日志 ([#1493](https://github.com/pingcap/tidb-operator/pull/1493), [@aylei](https://github.com/aylei))
- 为 `Discovery Service` 和 `Discovery Deployment` 避免不必要的更新 ([#1499](https://github.com/pingcap/tidb-operator/pull/1499), [@aylei](https://github.com/aylei))
- 移除某些没有意义的更新事件 ([#1486](https://github.com/pingcap/tidb-operator/pull/1486), [@weekface](https://github.com/weekface))
