---
title: TiDB Operator 1.6.6 Release Notes
summary: 了解 TiDB Operator 1.6.6 版本的新功能、优化提升，以及 Bug 修复。
---

# TiDB Operator 1.6.6 Release Notes

发布日期：2026 年 7 月 31 日

TiDB Operator 版本：1.6.6

## 新功能

- 支持为 TiDB 集群组件配置 `securityContext` ([#6404](https://github.com/pingcap/tidb-operator/pull/6404), [@fgksgf](https://github.com/fgksgf))
- 支持为 TiDB 集群组件 Pod 配置 `automountServiceAccountToken` ([#6764](https://github.com/pingcap/tidb-operator/pull/6764), [@liubog2008](https://github.com/liubog2008))
- 支持为 discovery 组件启用 mTLS ([#6781](https://github.com/pingcap/tidb-operator/pull/6781), [@liubog2008](https://github.com/liubog2008))
- 支持为 `TidbInitializer` 指定 `serviceAccountName` ([#6872](https://github.com/pingcap/tidb-operator/pull/6872), [@tennix](https://github.com/tennix))
- 支持为 `TidbMonitor` 配置 `automountServiceAccountToken` ([#6906](https://github.com/pingcap/tidb-operator/pull/6906), [@tennix](https://github.com/tennix))

## 优化提升

- 支持通过 `ShebangBash` 和 `NoWaitDNS` 标志，在组件启动脚本中使用 Bash shebang 并跳过 DNS 就绪检查 ([#6767](https://github.com/pingcap/tidb-operator/pull/6767), [@liubog2008](https://github.com/liubog2008))
- 移除 Helm charts 中的通配符选择器 ([#6762](https://github.com/pingcap/tidb-operator/pull/6762), [@liubog2008](https://github.com/liubog2008))
- 当 `automountServiceAccountToken` 被禁用时，支持为 BR 和 discovery 组件显式挂载 ServiceAccount token，便于在执行 `block-automount-serviceaccount-token-pod` 策略的限制环境（如 FedRAMP/Gatekeeper）中运行 TiDB Operator ([#6815](https://github.com/pingcap/tidb-operator/pull/6815), [@liubog2008](https://github.com/liubog2008))
- 为 controller-manager 新增 projected ServiceAccount token 卷支持，使 `automountServiceAccountToken` 被禁用时 controller-manager 仍能向 Kubernetes API 认证 ([#6873](https://github.com/pingcap/tidb-operator/pull/6873), [@tennix](https://github.com/tennix))
- 在符合条件的 TiDB 升级过程中暂停 DDL 任务，通过与 TiDB smooth-upgrade API（`/upgrade/start` 和 `/upgrade/finish`）协同，降低 DDL 对滚动升级的影响，提升升级稳定性 ([#6904](https://github.com/pingcap/tidb-operator/pull/6904), [@tennix](https://github.com/tennix))
- 在 `Backup` 和 `Restore` 状态中暴露最近的 BR operation ID，便于将 Kubernetes 备份/恢复任务与 BR 侧诊断及锁元数据关联 ([#6954](https://github.com/pingcap/tidb-operator/pull/6954), [@RidRisR](https://github.com/RidRisR))

## Bug 修复

- 修复当启用 `--logtostderr` 时 `--stderrthreshold` 标志不生效的问题 ([#6786](https://github.com/pingcap/tidb-operator/pull/6786), [@pierluigilenoci](https://github.com/pierluigilenoci))
- 修复 `TidbInitializer` Job Pod 未按预期禁用 ServiceAccount token 自动挂载的问题，该问题会导致无法通过 FedRAMP/Gatekeeper 的 `block-automount-serviceaccount-token-pod` 策略 ([#6838](https://github.com/pingcap/tidb-operator/pull/6838), [@tennix](https://github.com/tennix))
- 修复当凭证文件为空时，GKE Workload Identity (WIF) 备份认证失败的问题 ([#6888](https://github.com/pingcap/tidb-operator/pull/6888), [@Leavrth](https://github.com/Leavrth))
- 修复当 Prometheus 镜像 tag 不兼容 semver 且未配置 `remote_write` 时，`TidbMonitor` 调谐失败（`Invalid Semantic version`）的问题。此前版本号会被无条件解析，尽管它仅在 `remote_write` 路径中使用 ([#7007](https://github.com/pingcap/tidb-operator/pull/7007), [@time-and-fate](https://github.com/time-and-fate))
