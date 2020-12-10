---
title: 暂停同步 Kubernetes 上的 TiDB 集群
summary: 介绍如何暂停同步 Kubernetes 上的 TiDB 集群
---

# 暂停同步 Kubernetes 上的 TiDB 集群

本文介绍如何通过配置文件暂停同步 Kubernetes 上的 TiDB 集群。

## 什么是同步

在TiDB Operator中，控制器运行一个非中止循环来调整 TiDB 集群状态。控制器会不断对比 `TidbCluster` 对象中记录的期望状态与 TiDB 集群的实际状态，并调整 Kubernetes 中的资源以驱动 TiDB 集群满足期望状态。这个不断调整的过程通常被称为**同步**。更多细节参见[TiDB Operator架构](architecture.md)。

## 暂停同步的应用场景

以下为一些暂停同步的应用场景。

- 避免意外的滚动升级

    假设你发现由于 TiDB Operator 新版本的兼容新问题或者操作失误，导致 TiDB 集群发生意外的滚动升级，你可以暂停 TiDB 集群的同步过程，避免 TiDB 集群被错误地升级。

- 维护时间窗口

    在某些情况下，只允许在特定时间窗口内配置 TiDB 集群的状态。因此可以在维护时间窗口之外的时间段暂停 TiDB 集群的同步过程，这样在维护时间窗口之外对 TiDB 集群的任何配置都不会生效；在维护时间窗口时，可以通过恢复 TiDB 集群同步来允许配置 TiDB 集群的状态。

## 暂停同步 TiDB 集群

在 TiDB 集群配置文件的 `spec` 配置项中新增 `paused: true`，并应用该配置文件，TiDB 集群各组件 (PD、TiKV、TiDB、Pump) 的同步过程将会被暂停。

1. 修改配置文件如下：

    {{< copyable "" >}}
    
    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: basic
    spec:
      ...
      paused: true  # 暂停同步
      pd:
        ...
      tikv:
        ...
      tidb:
        ...
    ```

2. 使用以下命令应用上述配置文件，暂停 TiDB 集群同步。其中 `${tidb-cluster-file}` 表示 TiDB 集群配置文件, `${tidb-cluster-namespace}` 表示 TiDB 集群所在的 namespace。

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl apply -f ${tidb-cluster-file} -n ${tidb-cluster-namespace}
    ```

3. TiDB 集群同步暂停后，可以使用以下命令查看 Controller Pod 日志确认 TiDB 集群同步状态。其中 `${controller-pod-name}` 表示 Controller Pod 的名称，`${tidb-operator-namespace}` 表示 TiDB Operator 所在的 namespace。

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${controller-pod-name} -n `${tidb-operator-namespace}` | grep paused
    ```

    输出类似下方结果则表示 TiDB 集群同步已经暂停，可见 TiDB 集群各组件的同步已经被暂停。
    
    ```
    I1207 11:09:59.029949       1 pd_member_manager.go:92] tidb cluster default/basic is paused,     skip syncing for pd service
    I1207 11:09:59.029977       1 pd_member_manager.go:136] tidb cluster default/basic is paused,     skip syncing for pd headless service
    I1207 11:09:59.035437       1 pd_member_manager.go:191] tidb cluster default/basic is paused,     skip syncing for pd statefulset
    I1207 11:09:59.035462       1 tikv_member_manager.go:116] tikv cluster default/basic is paused,     skip syncing for tikv service
    I1207 11:09:59.036855       1 tikv_member_manager.go:175] tikv cluster default/basic is paused,     skip syncing for tikv statefulset
    I1207 11:09:59.036886       1 tidb_member_manager.go:132] tidb cluster default/basic is paused,     skip syncing for tidb headless service
    I1207 11:09:59.036895       1 tidb_member_manager.go:258] tidb cluster default/basic is paused,     skip syncing for tidb service
    I1207 11:09:59.039358       1 tidb_member_manager.go:188] tidb cluster default/basic is paused,     skip syncing for tidb statefulset
    ```

## 恢复同步 TiDB 集群

当故障排除后，如果想要恢复 TiDB 集群的同步，可以在配置文件的 `spec` 配置项中，将 `paused: true` 更改为 `paused: false` 并应用该配置文件，即可取消暂停指令，恢复同步 TiDB 集群。

1. 修改配置文件如下：

    {{< copyable "" >}}
    
    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: basic
    spec:
      ...
      paused: false  # 恢复同步
      pd:
        ...
      tikv:
        ...
      tidb:
        ...
    ```

2. 使用以下命令应用配置文件，恢复 TiDB 集群同步。其中 `${tidb-cluster-file}` 表示 TiDB 集群配置文件， `${tidb-cluster-namespace}` 表示 TiDB 集群所在的 namespace。

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl apply -f ${tidb-cluster-file} -n ${tidb-cluster-namespace}
    ```

3. 恢复 TiDB 集群同步后，可以使用以下命令查看 Controller Pod 日志确认 TiDB 集群同步状态。其中 `${controller-pod-name}` 表示 Controller Pod 的名称，`${tidb-operator-namespace}` 表示 TiDB Operator 所在的 namespace。

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${controller-pod-name} -n `${tidb-operator-namespace}` | grep "Finished syncing TidbCluster"
    ```
    
    输出类似下方结果，可以看到同步成功时间戳大于暂停同步日志中显示的时间戳，表示 TiDB 集群同步已经被恢复。
    
    ```
    I1207 11:14:59.361353       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (368.816685ms)
    I1207 11:15:28.982910       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (97.486818ms)
    I1207 11:15:29.360446       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (377.51187ms)
    ```
