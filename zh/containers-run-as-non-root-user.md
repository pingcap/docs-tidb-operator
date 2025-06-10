---
title: 以非 root 用户运行容器
summary: 了解如何在 Kubernetes 环境中以非 root 用户运行容器。
---

# 以非 root 用户运行容器

在某些 Kubernetes 环境中，容器无法以 root 用户身份运行。出于安全考虑，建议在生产环境中以非 root 用户运行容器，以降低潜在攻击带来的安全风险。本文介绍如何通过配置 [`securityContext`](https://kubernetes.io/zh-cn/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-pod) 实现以非 root 用户运行容器。

## 配置 TiDB Operator 相关的容器

对于 TiDB Operator 相关的容器，可以在 Helm 的 `values.yaml` 文件中配置安全上下文 (`securityContext`)。

以下是一个配置示例：

```yaml
controllerManager:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

## 配置按照 CR 生成的容器

对于按照 Custom Resource (CR) 生成的容器，可以在任意一种 CR（例如 `PDGroup`、`TiDBGroup`、`TiKVGroup`、`TiFlashGroup`、`TiCDCGroup`、`Backup`、`CompactBackup`、`BackupSchedule`、`Restore`）中配置安全上下文 (`securityContext`)。

- 对于 `PDGroup`、`TiDBGroup`、`TiKVGroup`、`TiFlashGroup`、`TiCDCGroup` 等 CR，可以通过 Overlay 的方式配置安全上下文。配置 `PDGroup` CR 的示例如下：

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

- 对于 `Backup`、`CompactBackup`、`BackupSchedule`、`Restore` 等 CR，可以在 `spec` 中配置 `podSecurityContext`。配置 `Backup` CR 的示例如下：

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
