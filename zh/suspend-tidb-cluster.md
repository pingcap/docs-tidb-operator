---
title: 挂起 TiDB 集群
summary: 了解如何通过配置挂起 Kubernetes 上的 TiDB 集群。
---

# 挂起 TiDB 集群

本文介绍如何通过配置 `TidbCluster` 对象来挂起 Kubernetes 上的 TiDB 集群，或挂起 TiDB 集群组件。挂起集群后，你可以停止所有组件或某个组件的 Pod，保留 `TidbCluster` 对象以及其他资源（例如 Service、PVC 等）。

在某些测试场景下，如果你需要节省资源，你可以在不使用 TiDB 集群时挂起集群。

> **注意：**
>
> 挂起 TiDB 集群，要求 TiDB Operator 版本 >= 1.3.7。

## 配置挂起 TiDB 集群

如果你需要挂起 TiDB 集群，执行以下步骤：

1. 在 `TidbCluster` 对象中，配置 `spec.suspendAction` 字段，挂起整个 TiDB 集群：

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      suspendAction:
        suspendStatefulSet: true
      # ...
    ```

    TiDB Operator 也支持挂起一个或多个 TiDB 集群的组件。以 TiKV 为例，通过配置 `TidbCluster` 对象的 `spec.tikv.suspendAction` 字段来挂起 TiDB 集群中的 TiKV。

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      tikv:
        suspendAction:
          suspendStatefulSet: true
      # ...
    ```

2. 挂起 TiDB 集群后，通过以下命令观察到挂起的组件的 Pod 逐步被删除。

    ```shell
    kubectl -n ${namespace} get pods
    ```

    每个挂起的组件的 Pod 会按照以下的顺序被删除：

    * TiDB
    * TiFlash
    * TiCDC
    * TiKV
    * Pump
    * TiProxy
    * PD

> **注意：**
>
> - PD 从 v8.0.0 版本开始支持微服务架构。
> - 若你的 TiDB 集群中部署了 PD 微服务组件，PD 微服务组件的 Pod 会在删除 PD 之后被删除。

## 恢复 TiDB 集群

在 TiDB 集群或组件被挂起后，如果你需要恢复 TiDB 集群，执行以下步骤：

1. 在 `TidbCluster` 对象中，配置 `spec.suspendAction` 字段，恢复被挂起的整个 TiDB 集群：

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      suspendAction:
        suspendStatefulSet: false
      # ...
    ```

    TiDB Operator 也支持恢复一个或多个 TiDB 集群的组件。以 TiKV 为例，通过配置 `TidbCluster` 对象的 `spec.tikv.suspendAction` 字段来恢复 TiDB 集群中的 TiKV。

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      tikv:
        suspendAction:
          suspendStatefulSet: false
      # ...
    ```

2. 恢复 TiDB 集群后，通过以下命令观察到挂起的组件的 Pod 逐步被创建。

    ```shell
    kubectl -n ${namespace} get pods
    ```
