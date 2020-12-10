---
title: Pause Sync of a TiDB Cluster in Kubernetes
summary: Introduce how to pause sync of a TiDB cluster in Kubernetes
---

# Pause Sync of a TiDB Cluster in Kubernetes

This document introduce how to pause sync of a TiDB cluster in Kubernetes using the configuration file.

## What is sync in TiDB Operator

In TiDB Operator, a non-terminating control loop (controller) regulates the state of the TiDB cluster in Kubernetes. The controller constantly compares the desired state recorded in the `TidbCluster` object with the actual state of the TiDB cluster. This process is referred to as **sync** generally. For more details, refer to [TiDB Operator Architecture](architecture.md).

## Use scenarios

Here are some cases where you might need to pause sync of a TiDB cluster in Kubernetes.

- Avoiding unexpected rolling update

    Suppose the TiDB cluster is unexpectedly rolling updated due to a compatible issue of a new TiDB Operator version or an operation error (user fault), and you want to pause this unexpected rolling update. You can pause sync of the TiDB cluster to avoid TiDB cluster being updated unexpectedly.

- Maintenance window

    In some situations, you can configure the status of the TiDB cluster only during a maintenance window. When outside the maintenance window, you can pause sync of the TiDB cluster, so that any modification to spec does not take effect. When inside the maintenance window, you can resume sync of the TiDB cluster to allow changes to status of TiDB cluster.

## Pause sync

You could append `paused: true` to `spec` item in the config file of the TiDB cluster, and apply the config file. Sync of TiDB cluster's components (PD, TiKV, TiDB, Pump) will be paused. 

1. Edit the configuration file as follows:

    {{< copyable "" >}}
    
    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: basic
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

2. Execute the following command to apply the above config file. `${tidb-cluster-file}` represents the TiDB cluster config file, and `${tidb-cluster-namespace}` refers to the TiDB cluster namespace.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl apply -f ${tidb-cluster-file} -n ${tidb-cluster-namespace}
    ```

3. Execute the following command to confirm the sync status of a TiDB cluster. `${controller-pod-name}` is the name of Controller Pod, and `${tidb-operator-namespace}` is the namespace of TiDB Operator.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${controller-pod-name} -n `${tidb-operator-namespace}` | grep paused
    ```
    
    The expected output is as follows. The sync of all components in the TiDB cluster is paused.
    
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

## Resume sync

After troubleshooting, if you want to resume the sync of the TiDB cluster, configure `spec.paused` to `false`, and apply the config file. 

1. Edit the configuration file as follows:

    {{< copyable "" >}}
    
    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: basic
    spec:
      ...
      paused: false  # Resuming Sync of TiDB Cluster
      pd:
        ...
      tikv:
        ...
      tidb:
        ...
    ```

2. Execute the following command to apply the above config file. `${tidb-cluster-file}` represents the TiDB cluster config file, and `${tidb-cluster-namespace}` refers to the TiDB cluster namespace.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl apply -f ${tidb-cluster-file} -n ${tidb-cluster-namespace}
    ```

3. After resuming sync of the TiDB cluster, execute the following command to confirm sync status of the TiDB cluster. `${controller-pod-name}` represents the name of Controller Pod, `${tidb-operator-namespace}` represents the namespace of TiDB Operator.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${controller-pod-name} -n `${tidb-operator-namespace}` | grep "Finished syncing TidbCluster"
    ```
    
    The expected output is as follows. The `finished syncing` timestamp is later than the `pausing` timestamp, which indicates that sync of the TiDB cluster has been resumed.
    
    ```
    I1207 11:14:59.361353       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (368.816685ms)
    I1207 11:15:28.982910       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (97.486818ms)
    I1207 11:15:29.360446       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (377.51187ms)
    ```
