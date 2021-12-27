---
title: 以非 root 用户运行容器
summary: 了解如何以非 root 用户运行容器。
---

# 以非 root 用户运行容器

在某些 Kubernetes 环境中，无法用 root 用户运行容器。本文介绍如何通过配置 [`securityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-pod) 来以非 root 用户运行容器。

## 配置 TiDB Operator 相关的容器

对于 TiDB Operator 相关的容器，你可以在 Helm 的 `values.yaml` 文件中配置安全上下文 (security context)。TiDB operator 的所有相关组件都支持该配置 (`<controllerManager/scheduler/advancedStatefulset/admissionWebhook>.securityContext`)。

以下是一个配置示例：

```yaml
controllerManager:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

## 配置按照 CR 生成的容器

对于按照 CR 生成的容器，你同样可以在任意一种 CR (`TidbCluster`/`DMCluster`/`TiInitializer`/`TiMonitor`/`Backup`/`BackupSchedule`/`Restore`) 中配置安全上下文 (security context)。

你可以采用以下两种 `podSecurityContext` 配置。如果同时配置了集群级别和组件级别，则该组件以组件级别的配置为准。

- 配置在集群级别 (`spec.podSecurityContext`)，对所有组件生效。配置示例如下：

    ```yaml
    spec:
      podSecurityContext:
        runAsUser: 1000
        runAsGroup: 2000
        fsGroup: 2000
    ```

- 配置在组件级别，仅对该组件生效。 例如，配置 `TidbCluster` 的 `spec.tidb.podSecurityContext`，配置 `DMCluster` 的 `spec.master.podSecurityContext`)。配置示例如下：

    ```yaml
    spec:
      pd:
        podSecurityContext:
          runAsUser: 1000
          runAsGroup: 2000
          fsGroup: 2000
      tidb:
        podSecurityContext:
          runAsUser: 1000
          runAsGroup: 2000
          fsGroup: 2000
    ```
