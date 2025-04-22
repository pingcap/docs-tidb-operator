---
title: 以非 root 用户运行容器
summary: 了解如何以非 root 用户运行容器。
---

# 以非 root 用户运行容器

在某些 Kubernetes 环境中，无法用 root 用户运行容器。出于安全考虑，建议在生产环境中以非 root 用户运行容器，这可以减少容器被攻击时的安全风险。本文介绍如何通过配置 [`securityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-pod) 来以非 root 用户运行容器。

## 配置 TiDB Operator 相关的容器

对于 TiDB Operator 相关的容器，你可以在 Helm 的 `values.yaml` 文件中配置安全上下文 (security context)。

以下是一个配置示例：

```yaml
controllerManager:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

## 配置按照 CR 生成的容器

对于按照 Custom Resource (CR) 生成的容器，你同样可以在任意一种 CR (`PDGroup`/`TiDBGroup`/`TiKVGroup`/`TiFlashGroup`/`TiCDCGroup`/`Backup`/`CompactBackup`/`BackupSchedule`/`Restore`) 中配置安全上下文 (security context)。

对于 `PDGroup`、`TiDBGroup`、`TiKVGroup`、`TiFlashGroup`、`TiCDCGroup` 等 CR，你可以通过 [Overlay](overlay.md) 的方式配置安全上下文。例如，为 PDGroup 配置:

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
spec:
  template:
    spec:
      overlay:
        pod:
          spec:
            securityContext:
              runAsUser: 1000
              runAsGroup: 2000
              fsGroup: 2000
```

对于 `Backup`、`CompactBackup`、`BackupSchedule`、`Restore` 等 CR，可以在 spec 中配置 `podSecurityContext`。例如，为 Backup 配置:

```yaml
apiVersion: br.pingcap.com/v1alpha1
kind: Backup
metadata:
  name: backup
spec:
  podSecurityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```
