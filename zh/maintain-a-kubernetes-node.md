---
title: 维护 TiDB 集群所在的 Kubernetes 节点
summary: 介绍如何维护 TiDB 集群所在的 Kubernetes 节点。
---

# 维护 TiDB 集群所在的 Kubernetes 节点

TiDB 是高可用数据库，可以在部分数据库节点下线的情况下正常运行，因此，我们可以安全地对底层 Kubernetes 节点进行停机维护。

本文档将详细介绍如何对 Kubernetes 节点进行维护操作。根据维护时长和存储类型，提供不同的操作策略。

## 环境准备

- [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

> **注意：**
>
> 维护节点前，需要保证 Kubernetes 集群的剩余资源足够运行 TiDB 集群。

## 维护节点

### 步骤 1：准备工作

1. 使用 `kubectl cordon` 命令标记待维护节点为不可调度，防止新的 Pod 调度到待维护节点上：

    ```shell
    kubectl cordon ${node_name}
    ```

2. 检查待维护节点上是否有 TiDB 集群组件 Pod：

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/managed-by=tidb-operator | grep ${node_name}
    ```

### 步骤 2：迁移 TiDB 集群组件 Pod

根据您的存储类型，选择合适的 Pod 迁移策略：

#### 选项 A：重调度 Pod（适用于存储可自动迁移）

如果使用的是可自动迁移的存储（如 [Amazon EBS](https://aws.amazon.com/cn/ebs/)），可以参考[优雅重启某个组件的单个 Pod](restart-a-tidb-cluster.md)来重调度各个组件 Pod。以 PD 组件为例：

1. 查看待维护节点上的 PD Pod:

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/component=pd | grep ${node_name}
    ```

2. 查看该 PD Pod 对应的实例名称：

    ```shell
    kubectl get pod -n ${namespace} ${pod_name} -o jsonpath='{.metadata.labels.pingcap\.com/instance}'
    ```

3. 给该 PD 实例添加一个新的 label 来触发重调度：

    ```shell
    kubectl label pd -n ${namespace} ${pd_instance_name} pingcap.com/restartedAt=2025-06-30T12:00
    ```

4. 确认该 PD Pod 已成功调度到其它节点：

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

5. 对其他组件（TiKV、TiDB 等）重复上述步骤，直到该维护节点上所有 TiDB 集群组件 Pod 都迁移完成。

#### 选项 B：重建实例（适用于本地存储）

如果节点存储不可以自动迁移（比如使用本地存储），你需要重建实例：

> **警告：**
>
> 重建实例会导致数据丢失。对于 TiKV 等有状态组件，请确保集群有足够的副本来保证数据安全。

以重建 TiKV 实例为例：

1. 删除 TiKV 实例 CR，TiDB Operator 会删除其关联的 PVC 和 ConfigMap 等资源，并自动创建新的实例：

    ```shell
    kubectl delete -n ${namespace} tikv ${tikv_instance_name}
    ```

2. 等待新创建的 TiKV 实例状态变为就绪：

    ```shell
    kubectl get -n ${namespace} tikv ${tikv_instance_name}
    ```

3. 确认 TiDB 集群状态正常，数据同步完成后，可以继续维护其他组件。

### 步骤 3：确认迁移完成

此时应该只剩下 DaemonSet 管理的 Pod（如网络插件、监控代理等）：

```shell
kubectl get pod --all-namespaces -o wide | grep ${node_name}
```

### 步骤 4：进行节点维护

此时可以安全地进行节点维护操作（如重启、更新系统、硬件维护等）。

### 步骤 5：维护后恢复（仅适用于临时维护）

如果是临时维护，节点维护完成后需要恢复节点：

1. 确认节点健康状态：

    ```shell
    watch kubectl get node ${node_name}
    ```

    观察到节点进入 `Ready` 状态后，继续下一步操作。

2. 使用 `kubectl uncordon` 命令解除节点的调度限制：

    ```shell
    kubectl uncordon ${node_name}
    ```

3. 观察 Pod 是否全部恢复正常运行：

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

    Pod 恢复正常运行后，维护操作完成。

如果是长期维护或节点永久移除，则不需要执行此步骤。
