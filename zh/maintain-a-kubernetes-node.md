---
title: 维护 TiDB 集群所在的 Kubernetes 节点
summary: 介绍如何维护 TiDB 集群所在的 Kubernetes 节点。
---

# 维护 TiDB 集群所在的 Kubernetes 节点

TiDB 是高可用数据库，即使部分节点下线，集群也能正常运行。因此，你可以安全地对 TiDB 集群所在的 Kubernetes 节点执行停机维护操作。

本文介绍在不同存储类型和维护时长下，如何安全地维护 Kubernetes 节点。

## 前提条件

- 安装 [`kubectl`](https://kubernetes.io/zh-cn/docs/tasks/tools/)

> **注意：**
>
> 维护节点前，请确保 Kubernetes 集群的剩余资源足以支撑 TiDB 集群的正常运行。

## 维护节点步骤

### 第 1 步：准备工作

1. 使用 `kubectl cordon` 命令将待维护节点标记为不可调度，防止新的 Pod 被调度到该节点：

    ```shell
    kubectl cordon ${node_name}
    ```

2. 检查待维护节点上是否运行 TiDB 集群组件的 Pod：

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/managed-by=tidb-operator | grep ${node_name}
    ```

    - 如果节点上存在 TiDB 集群组件的 Pod，请按照后续步骤迁移这些 Pod。
    - 如果节点上没有 TiDB 集群组件的 Pod，则无需迁移 Pod，可直接进行节点维护。
    
### 第 2 步：迁移 TiDB 集群组件 Pod

根据 Kubernetes 节点的存储类型，选择相应的 Pod 迁移策略：

- **可自动迁移存储**：使用[方法 1：重调度 Pod](#方法-1重调度-pod适用于可自动迁移的存储)
- **不可自动迁移存储**：使用[方法 2：重建实例](#方法-2重建实例适用于本地存储)

#### 方法 1：重调度 Pod（适用于可自动迁移的存储）

如果 Kubernetes 节点使用的存储支持自动迁移（如 [Amazon EBS](https://aws.amazon.com/cn/ebs/)），可以通过[优雅重启某个组件的单个 Pod](restart-a-tidb-cluster.md#优雅重启某个组件的单个-pod) 的方式重调度各个组件 Pod。以 PD 组件为例：

1. 查看待维护节点上的 PD Pod：

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/component=pd | grep ${node_name}
    ```

2. 获取该 PD Pod 对应的实例名称：

    ```shell
    kubectl get pod -n ${namespace} ${pod_name} -o jsonpath='{.metadata.labels.pingcap\.com/instance}'
    ```

3. 为该 PD 实例添加一个新标签以触发重调度：

    ```shell
    kubectl label pd -n ${namespace} ${pd_instance_name} pingcap.com/restartedAt=2025-06-30T12:00
    ```

4. 确认该 PD Pod 已成功调度到其他节点：

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

5. 按相同步骤迁移 TiKV、TiDB 等其他组件 Pod，直至该维护节点上的所有 TiDB 集群组件 Pod 都迁移完成。

#### 方法 2：重建实例（适用于本地存储）

如果 Kubernetes 节点使用的存储不支持自动迁移（如本地存储），你需要重建实例。

> **警告：**
>
> 重建实例会导致数据丢失。对于 TiKV 等有状态组件，请确保集群副本数充足，以保障数据安全。

以重建 TiKV 实例为例：

1. 删除 TiKV 实例的 CR。TiDB Operator 会自动删除其关联的 PVC 和 ConfigMap 等资源，并创建新实例：

    ```shell
    kubectl delete -n ${namespace} tikv ${tikv_instance_name}
    ```

2. 等待新创建的 TiKV 实例状态变为 `Ready`：

    ```shell
    kubectl get -n ${namespace} tikv ${tikv_instance_name}
    ```

3. 确认 TiDB 集群状态正常且数据同步完成后，再继续维护其他组件。

### 第 3 步：确认迁移完成

完成 Pod 迁移后，该节点上应仅运行由 DaemonSet 管理的 Pod（如网络插件、监控代理等）：

```shell
kubectl get pod --all-namespaces -o wide | grep ${node_name}
```

### 第 4 步：执行节点维护

现在，你可以安全地对节点执行维护操作，例如重启、更新操作系统或进行硬件维护。

### 第 5 步：维护后恢复（仅适用于临时维护）

如果计划长期维护或永久下线节点，请跳过此步骤。

对于临时维护，节点维护完成后需要执行以下恢复操作：

1. 确认节点健康状态：

    ```shell
    watch kubectl get node ${node_name}
    ```

    当节点状态变为 `Ready` 后，继续下一步。

2. 使用 `kubectl uncordon` 命令解除节点的调度限制：

    ```shell
    kubectl uncordon ${node_name}
    ```

3. 观察 Pod 是否全部恢复正常运行：

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

    当所有 Pod 正常运行后，维护操作完成。
