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

对于按照 Custom Resource (CR) 生成的容器，你可以配置 Pod 级别或容器级别的安全上下文。不同 CR 支持的字段有所不同。

### 配置 Pod 级别的安全上下文

`podSecurityContext` 对生成的 Pod 中的所有容器生效，并控制卷所有权等 Pod 级别的设置。

对于 `TidbCluster` 和 `DMCluster`，你可以在以下级别配置 `podSecurityContext`：

- 集群级别：配置 `spec.podSecurityContext`，对所有组件生效：

    ```yaml
    spec:
      podSecurityContext:
        runAsUser: 1000
        runAsGroup: 2000
        fsGroup: 2000
    ```

- 组件级别：配置 `spec.<component>.podSecurityContext`，仅对指定组件生效。例如，为 `TidbCluster` 的 TiDB 组件配置 `spec.tidb.podSecurityContext`，或为 `DMCluster` 的 master 组件配置 `spec.master.podSecurityContext`：

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

如果同时配置了这两个级别，该组件将使用组件级别的 `podSecurityContext` 替代集群级别的 `podSecurityContext`。

`TidbDashboard`、`TidbNGMonitoring`、`TidbInitializer`、`TidbMonitor`、`Backup`、`BackupSchedule` 和 `Restore` 等其他 CR 也支持 Pod 级别的安全上下文设置。有关支持的字段和路径，请参考 [API 文档](<https://github.com/pingcap/tidb-operator/blob/{{{ .tidb_operator_version }}}/docs/api-references/docs.md>)。

### 配置容器级别的安全上下文

从 TiDB Operator v1.6.6 起，以下 CR 支持[容器级别的安全上下文](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-container)：

- 对于 `TidbCluster` 和 `DMCluster`，配置 `spec.<component>.securityContext`，例如 `spec.pd.securityContext`、`spec.tidb.securityContext`、`spec.master.securityContext` 或 `spec.worker.securityContext`。这些 CR 不支持集群级别的 `spec.securityContext`。
- 对于 `TidbDashboard`，配置 `spec.securityContext`。
- 对于 `TidbNGMonitoring`，配置 `spec.ngMonitoring.securityContext`。在顶层配置 `spec.securityContext` 不会对生成的容器生效。
- 对于 `TidbMonitor`，分别为生成的容器配置 `securityContext`。支持的路径包括 `spec.initializer.securityContext`、`spec.prometheus.securityContext`、`spec.grafana.securityContext`、`spec.reloader.securityContext`、`spec.prometheusReloader.securityContext`、`spec.thanos.securityContext` 和 `spec.dm.initializer.securityContext`。

`TidbInitializer`、`Backup`、`BackupSchedule` 和 `Restore` 不支持容器级别的 `securityContext`。

有关 `ComponentSpec.securityContext` 的完整字段说明，请参考 [`ComponentSpec` API 文档](<https://github.com/pingcap/tidb-operator/blob/{{{ .tidb_operator_version }}}/docs/api-references/docs.md#componentspec>)。

例如，以下配置让 PD 容器以非 root 用户运行，设置其卷的组所有权，并禁止容器进程获得超出其父进程的特权：

```yaml
spec:
  pd:
    podSecurityContext:
      fsGroup: 2000
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      runAsGroup: 2000
      allowPrivilegeEscalation: false
```

> **注意：**
>
> - 容器级别的配置仅应用于对应字段所生成的容器定义，并覆盖有效 `podSecurityContext` 中的同名字段。
> - `fsGroup` 等影响 Pod 卷的字段只能配置在 `podSecurityContext` 中。
> - 更新已部署组件的 `securityContext` 会修改其 Pod 模板，并触发受影响 Pod 的滚动更新。
> - 如需单独配置 TiDB 慢日志 sidecar、TiKV 日志 sidecar、TiFlash 日志 sidecar 或 TiFlash init container，请分别使用 `spec.tidb.slowLogTailer.securityContext`、`spec.tikv.logTailer.securityContext`、`spec.tiflash.logTailer.securityContext` 或 `spec.tiflash.initializer.securityContext`。

> **警告：**
>
> `spec.tikv.privileged` 和 `spec.tiflash.privileged` 已弃用。一旦配置了对应组件的 `securityContext` 对象，即使对象为空，TiDB Operator 也会忽略原有的 `privileged` 字段。如果容器仍需以 privileged 模式运行，请显式配置 `securityContext.privileged: true`，否则组件可能无法启动。
