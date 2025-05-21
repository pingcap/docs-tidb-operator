---
title: 挂起和恢复 Kubernetes 上的 TiDB 集群
summary: 了解如何通过配置挂起和恢复 Kubernetes 上的 TiDB 集群。
---

# 挂起和恢复 Kubernetes 上的 TiDB 集群

本文介绍如何通过配置 `Cluster` 对象来挂起和恢复 Kubernetes 上的 TiDB 集群。挂起操作会停止集群中所有组件的 Pod，但不会删除 `Cluster` 对象及其相关资源（例如 Service、PVC 等），从而保留集群的数据和配置，便于后续恢复。

## 使用场景

挂起 TiDB 集群适用于以下场景：

- 临时释放测试环境中的计算资源
- 停止长期不使用的开发集群
- 临时停止集群但保留数据和配置

## 注意事项

挂起 TiDB 集群前，需要注意以下事项：

- 挂起操作将中断集群服务
- 已有的连接会被强制断开
- PVC 和数据仍会保留并占用存储空间
- 集群相关的 Service 和配置保持不变

## 挂起 TiDB 集群

如果你需要挂起 TiDB 集群，执行以下步骤：

1. 在 `Cluster` 对象中，将 `spec.suspendAction.suspendCompute` 字段设置为 `true`，以挂起整个 TiDB 集群：

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      suspendAction:
        suspendCompute: true
      # ...
    ```

2. 挂起 TiDB 集群后，通过以下命令观察到 TiDB 集群的 Pod 逐步被删除：

    ```shell
    kubectl -n ${namespace} get pods -w
    ```

## 恢复 TiDB 集群

在 TiDB 集群被挂起后，如果需要恢复 TiDB 集群，执行以下步骤：

1. 在 `Cluster` 对象中，将 `spec.suspendAction.suspendCompute` 字段设置为 `false`，以恢复被挂起的整个 TiDB 集群：

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      suspendAction:
        suspendCompute: false
      # ...
    ```

2. 恢复 TiDB 集群后，通过以下命令观察到 TiDB 集群的 Pod 逐步被创建：

    ```shell
    kubectl -n ${namespace} get pods -w
    ```
