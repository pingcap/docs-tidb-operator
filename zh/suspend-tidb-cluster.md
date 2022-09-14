---
title: 挂起 TiDB 集群
summary: 介绍如何通过配置挂起 Kubernetes 上的 TiDB 集群
---

本文如何通过配置挂起 Kubernetes 上的 TiDB 集群。挂起集群指的是：保留 `TidbCluster` 对象，并停止所有组件或者某个组件的 Pod。

在某些测试场景下，你可以在不使用 TiDB 集群时挂起集群，并且可以移除 TiDB 集群所占用的 Node 或者 Service，以此来节省成本。等待再次使用时恢复 TiDB 集群。

目前，挂起 TiDB 集群只支持删除组件的 Pod，其他资源（例如 Service、PVC 等）都会被保留。

## 挂起 TiDB 集群

1. 通过配置 TidbCluster 对象的 `spec.suspendAction` 字段来挂起整个 TiDB 集群。
   
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

    TiDB Operator 也支持挂起一个或多个 TiDB 集群的组件。以 TiKV 为例，通过配置 TidbCluster 对象的 `spec.tikv.suspendAction` 字段来挂起 TiDB 集群中的 TiKV。

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
   
    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl -n ${namespace} get pods
    ```

    每个挂起的组件的 Pod 会按照以下的顺序被删除：

    * TiDB
    * TiFlash
    * TiCDC
    * TiKV
    * Pump
    * PD
  
## 恢复 TiDB 集群

1. 通过配置 TidbCluster 对象的 `spec.suspendAction` 字段来恢复整个 TiDB 集群。

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
  
    TiDB Operator 也支持恢复一个或多个 TiDB 集群的组件。以 TiKV 为例，通过配置 TidbCluster 对象的 `spec.tikv.suspendAction` 字段来挂起 TiDB 集群中的 TiKV。

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
   
    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl -n ${namespace} get pods
    ```