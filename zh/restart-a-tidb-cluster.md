---
title: 重启 Kubernetes 上的 TiDB 集群
summary: 了解如何重启 Kubernetes 集群上的 TiDB 集群，包括优雅滚动重启 TiDB 集群中某个组件的所有 Pod，以及单独重启某个 Pod。
---

# 重启 Kubernetes 上的 TiDB 集群

在使用 TiDB 集群的过程中，如果某个 Pod 存在内存泄漏等问题，可能需要重启集群。本文介绍如何优雅滚动重启 TiDB 集群中某个组件的所有 Pod，或单独优雅重启某个 Pod。

> **警告：**
>
> 在生产环境中，强烈建议不要强制删除 TiDB 集群的 Pod。虽然 TiDB Operator 会自动重新创建被删除的 Pod，但这仍可能会导致部分访问 TiDB 集群的请求失败。

## 优雅滚动重启某个组件的所有 Pod

要优雅滚动重启某个组件（例如 PD、TiKV 或 TiDB）的所有 Pod，需要修改该组件对应的 Component Group Custom Resource (CR) 配置，在 `.spec.template.metadata` 部分添加 `pingcap.com/restartedAt` 的 label 或 annotation，并将其值设置为一个保证幂等性的字符串，例如当前时间。

以下示例展示如何为 PD 组件添加一个 annotation，从而触发对该 `PDGroup` 下所有 PD Pod 的优雅滚动重启：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
spec:
  replicas: 3
  template:
    metadata:
      annotations:
        pingcap.com/restartedAt: 2025-06-30T12:00
```

## 优雅重启某个组件的单个 Pod

你可以单独重启 TiDB 集群中的特定 Pod。不同组件的 Pod，操作略有不同。

对于 TiKV Pod，为确保有足够时间驱逐 Region leader，在删除 Pod 时需要指定 `--grace-period` 选项，否则操作可能失败。以下示例为 TiKV Pod 设置了 60 秒的宽限期：

```shell
kubectl -n ${namespace} delete pod ${pod_name} --grace-period=60
```

其他组件的 Pod 可以直接删除，TiDB Operator 会自动优雅重启这些 Pod：

```shell
kubectl -n ${namespace} delete pod ${pod_name}
```
