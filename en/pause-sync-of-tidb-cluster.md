---
title: Pause Sync of TiDB Cluster in Kubernetes
summary: Introduce how to pause sync of TiDB Cluster in Kubernetes
---

# Pause Sync of TiDB Cluster in Kubernetes

This document introduce how to pause sync of TiDB cluster in Kubernetes with config file.

## What is Sync in TiDB Operator

In TiDB Operator, a non-terminating control loop (controller) regulates the state of TiDB cluster in Kubernetes. The controller constantly compares the desired state recorded in the `TidbCluster` object with the actual state of the TiDB cluster. This process is referred to as **sync** generally. More details in [TiDB Operator Architecture](architecture.md).

## Some Cases where Pausing Sync could be used

Here are some cases where you might need to pause sync of TiDB cluster in Kubernetes.

- Avoiding unexpected rolling-update
    Supposing you find a unexpected rolling-update of TiDB cluster caused by a compatible issue of new TiDB Operator version or an operation error (user fault), and want to pause this unexpected rolling-update. You can pause sync of TiDB cluster to avoid TiDB cluster being updated unexpectedly.

- Maintenance Window
    In some situations, the status of TiDB cluster is allowed to be configured only during maintenance window. When outside the maintenance window, you can pause sync of TiDB cluster, so that any modification to spec will not take effect. When inside the maintenance window, you can resume sync of TiDB cluster to allow changes to status of TiDB cluster.

## Pausing Sync of TiDB Cluster

You could append `paused: true` to `spec` item in config file of TiDB cluster, and apply the config file. Sync of TiDB cluster's components (PD, TiKV, TiDB, Pump) will be paused. 

1. Edit the configuration file like below.

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

2. Execute following command to apply above config file. `${tidb-cluster-file}` represents config file of TiDB cluster, `${tidb-cluster-namespace}` refers to namespace of TiDB cluster.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl apply -f ${tidb-cluster-file} -n ${tidb-cluster-namespace}
    ```

3. If sync of TiDB cluster has been paused, execute following command to confirm the sync status of TiDB cluster. `${controller-pod-name}` represemnts the name of Controller Pod, `${tidb-operator-namespace}` represents the namespace of TiDB Operator.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${controller-pod-name} -n `${tidb-operator-namespace}` | grep paused
    ```
    
    The expected output is as follows, it shows that sync of components of TiDb cluster have been paused.
    
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

## Resuming Sync of TiDB Cluster

After troubleshooting, if you want to resume the sync of TiDB cluster, you can change config item `spec.paused` of TiDB CLuster config file from `true` to `false`, and apply the config file. 

1. Edit the configuration file like below.

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

2. Execute following command to apply config file, `${tidb-cluster-file}` refers to config file name of TiDB cluster, `${tidb-cluster-namespace}` refers to namespace of TiDB cluster.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl apply -f ${tidb-cluster-file} -n ${tidb-cluster-namespace}
    ```

3. After resuming sync of TiDB cluster, execute following command to confirm sync status of TiDB cluster. `${controller-pod-name}` represemnts the name of Controller Pod, `${tidb-operator-namespace}` represents the namespace of TiDB Operator.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl logs ${controller-pod-name} -n `${tidb-operator-namespace}` | grep "Finished syncing TidbCluster"
    ```
    
    We can see that the timestamp of finishd syncing is later than tiemstamp of pasuing, it indicates that sync of TiDB cluster has been resumed.
    
    ```
    I1207 11:14:59.361353       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (368.816685ms)
    I1207 11:15:28.982910       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (97.486818ms)
    I1207 11:15:29.360446       1 tidb_cluster_controller.go:136] Finished syncing TidbCluster     "default/basic" (377.51187ms)
    ```
