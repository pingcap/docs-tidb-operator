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

对于按照 Custom Resource (CR) 生成的容器，你同样可以在任意一种 CR (`TidbCluster`/`DmCluster`/`TidbInitializer`/`TidbMonitor`/`Backup`/`BackupSchedule`/`Restore`) 中配置安全上下文 (security context)。

你可以采用以下两种 `podSecurityContext` 配置。如果同时配置了集群级别和组件级别，则该组件以组件级别的配置为准。

- 配置在集群级别 (`spec.podSecurityContext`)，对所有组件生效。配置示例如下：

    ```yaml
    spec:
      podSecurityContext:
        runAsUser: 1000
        runAsGroup: 2000
        fsGroup: 2000
    ```

- 配置在组件级别，仅对该组件生效。例如，为 PD 组件配置 `spec.pd.podSecurityContext`，为 TiDB 组件配置 `spec.tidb.podSecurityContext`。配置示例如下：

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

从 TiDB Operator v1.6.6 起，你还可以通过 `spec.<component>.securityContext` 为组件的主容器配置[容器级别的安全上下文](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-container)。容器级别的配置仅对该容器生效。当容器级别和 Pod 级别配置了相同字段时，容器级别的配置优先生效。

例如，以下配置让 PD 主容器以非 root 用户运行，并禁止进程获取更多权限：

```yaml
spec:
  pd:
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      runAsGroup: 2000
      allowPrivilegeEscalation: false
```

> **注意：**
>
> - `fsGroup` 等影响 Pod 卷的字段只能配置在 `podSecurityContext` 中。
> - 如果需要为 sidecar 容器或 init container 单独配置安全上下文，请在对应容器的配置中设置 `securityContext`。
> - `spec.tikv.privileged` 和 `spec.tiflash.privileged` 已弃用。请改用对应组件的 `securityContext.privileged`。如果配置了 `securityContext`，TiDB Operator 会忽略原有的 `privileged` 字段。
