---
title: Pause Sync of a TiDB Cluster in Kubernetes
summary: Introduce how to pause sync of a TiDB cluster in Kubernetes
---

# Pause Sync of a TiDB Cluster in Kubernetes

This document introduce how to pause sync of a TiDB cluster in Kubernetes with configuration.

## What is sync in TiDB Operator

In TiDB Operator, controller regulates the state of the TiDB cluster in Kubernetes. The controller constantly compares the desired state recorded in the `TidbCluster` object with the actual state of the TiDB cluster. This process is referred to as **sync** generally. For more details, refer to [TiDB Operator Architecture](architecture.md).

## Use scenarios

Here are some cases where you might need to pause sync of a TiDB cluster in Kubernetes.

- Avoiding unexpected rolling update

    In order to prevent the compatibility of the new version TiDB Operator from affecting the TiDB clusters, you can pause sync of TiDB clusters before updating the TiDB Operator. After updating TiDB Operator, resume sync of TiDB clusters one by one or resume sync of TiDB clusters at a specified time, so as to observe the impact of TiDB Operator rolling update on the cluster.

- Avoid multiple rolling restarts

    In some cases, the configuration of a TiDB cluster may be modified several times over a period of time, but you do not want to restart the TiDB cluster many times. In order to avoid multiple rolling restarts, you can pause sync of a TiDB cluster first. During this period, any modification to configuration of the TiDB cluster will not take effect. After the cluster configuration modification is completed, resuming sync of TiDB Cluster. At this time, multiple configuration changes during the sync pausing can be applied in one time rolling restart.

- Maintenance window

    In some situations, you can update or restart TiDB cluster only during a maintenance window. When outside the maintenance window, you can pause sync of the TiDB cluster, so that any modification to spec does not take effect. When inside the maintenance window, you can resume sync of the TiDB cluster to allow TiDB cluster rolling update or restart.

## Pause sync

1. Execute the following command to edit configuration of TiDB cluster. `${cluster_name}` represents the name of TiDB cluster, and `${namespace}` refers to the TiDB cluster namespace.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl edit tc/`${cluster_name}` -n ${namespace}
    ```

2. Configure the TidbCluster CR with `spec.paused: true` as following, save changes and exit editor, sync of TiDB cluster's components (PD, TiKV, TiDB, TiFlash, TiCDC,Pump) will be paused. 

    {{< copyable "" >}}
    
    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      ...
    spec:
      ...
      paused: true  # Pausing sync of TiDB cluster
      pd:
        ...
      tikv:
        ...
      tidb:
        ...
    ```

3. Execute the following command to confirm the sync status of a TiDB cluster. `${pod_name}` is the name of Controller Pod, and `${namespace}` is the namespace of TiDB Operator.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${pod_name} -n `${namespace}` | grep paused
    ```
    
    The expected output is as follows. The sync of all components in the TiDB cluster is paused.
    
    ```
    I1207 11:09:59.029949       1 pd_member_manager.go:92] tidb cluster default/basic is paused, skip syncing for pd service
    I1207 11:09:59.029977       1 pd_member_manager.go:136] tidb cluster default/basic is paused, skip syncing for pd headless service
    I1207 11:09:59.035437       1 pd_member_manager.go:191] tidb cluster default/basic is paused, skip syncing for pd statefulset
    I1207 11:09:59.035462       1 tikv_member_manager.go:116] tikv cluster default/basic is paused, skip syncing for tikv service
    I1207 11:09:59.036855       1 tikv_member_manager.go:175] tikv cluster default/basic is paused, skip syncing for tikv statefulset
    I1207 11:09:59.036886       1 tidb_member_manager.go:132] tidb cluster default/basic is paused, skip syncing for tidb headless service
    I1207 11:09:59.036895       1 tidb_member_manager.go:258] tidb cluster default/basic is paused, skip syncing for tidb service
    I1207 11:09:59.039358       1 tidb_member_manager.go:188] tidb cluster default/basic is paused, skip syncing for tidb statefulset
    ```

## Resume sync

If you want to resume the sync of the TiDB cluster, configure the TidbCluster CR with `spec.paused: false`.

1. Execute the following command to edit configuration of TiDB cluster. `${cluster_name}` represents the name of TiDB cluster, and `${namespace}` refers to the TiDB cluster namespace.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl edit tc/`${cluster_name}` -n ${namespace}
    ```

2. Configure the TidbCluster CR with `spec.paused: false` as following, save changes and exit editor, sync of TiDB cluster's components (PD, TiKV, TiDB, TiFlash, TiCDC,Pump) will be resumed. 

    {{< copyable "" >}}
    
    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      ...
    spec:
      ...
      paused: false  # Resuming sync of TiDB cluster
      pd:
        ...
      tikv:
        ...
      tidb:
        ...
    ```

3. After resuming sync of the TiDB cluster, execute the following command to confirm sync status of the TiDB cluster. `${pod_name}` represents the name of Controller Pod, `${namespace}` represents the namespace of TiDB Operator.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${pod_name} -n `${namespace}` | grep "Finished syncing TidbCluster"
    ```
    
    The expected output is as follows. The `finished syncing` timestamp is later than the `pausing` timestamp, which indicates that sync of the TiDB cluster has been resumed.
    
    ```
    I1207 11:14:59.361353       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster "default/basic" (368.816685ms)
    I1207 11:15:28.982910       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster "default/basic" (97.486818ms)
    I1207 11:15:29.360446       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster "default/basic" (377.51187ms)
    ```
