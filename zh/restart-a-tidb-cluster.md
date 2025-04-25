---
title: 重启 Kubernetes 上的 TiDB 集群
summary: 了解如何重启 Kubernetes 集群上的 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/restart-a-tidb-cluster/']
---

# 重启 Kubernetes 上的 TiDB 集群

在使用 TiDB 集群的过程中，如果你发现某个 Pod 存在内存泄漏等问题，需要对集群进行重启，本文描述了如何优雅滚动重启 TiDB 集群内某个组件的所有 Pod，或优雅重启单个 Pod。

> **警告：**
>
> 在生产环境中，未经过优雅重启而手动删除某个 TiDB 集群的 Pod 是一件极其危险的事情，虽然 TiDB Operator 会将 Pod 再次拉起，但这依旧可能会引起部分访问 TiDB 集群的请求失败。

## 优雅滚动重启 TiDB 集群组件的所有 Pod

修改对应 Component Group Custom Resource 的配置，在 `.spec.template.metadata` 添加一个 label 或者 annotation `pingcap.com/restartedAt`，Value 为一个用来保证幂等性的字符串，例如设置为当前时间。

以下示例中，为组件 PD 设置了 annotation，表示将优雅滚动重启该 Group 的三个 PD Pod：

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

## 优雅重启单个 Pod

对于 TiKV Pod，为确保有足够的时间 evict region leader，需要在删除时指定 `--grace-period` 选项，否则会失败。 以下示例中，为 TiKV Pod 设置了 60 秒的宽限期：

{{< copyable "shell-regular" >}}

```shell
kubectl -n ${namespace} delete pod ${pod_name} --grace-period=60
```

对于其他 Pod 直接删除即可，TiDB Operator 会优雅重启该 Pod：

{{< copyable "shell-regular" >}}

```shell
kubectl -n ${namespace} delete pod ${pod_name}
```
