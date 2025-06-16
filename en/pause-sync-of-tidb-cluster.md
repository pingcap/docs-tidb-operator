---
title: Pause Sync of a TiDB Cluster on Kubernetes
summary: Introduce how to pause sync of a TiDB cluster on Kubernetes.
---

# Pause Sync of a TiDB Cluster on Kubernetes

This document introduces how to pause sync of a TiDB cluster on Kubernetes by modifying its configuration.

## What is sync in TiDB Operator

In TiDB Operator, the controller constantly compares the desired state recorded in the Custom Resource (CR) object with the actual state. The controller then creates, updates, or deletes Kubernetes resources to ensure the TiDB cluster matches the desired state. This ongoing adjustment process is referred to as **sync**. For more information, see [TiDB Operator Architecture](architecture.md).

## Usage scenarios

The following lists some cases where you might need to pause sync of a TiDB cluster on Kubernetes:

- Avoid unexpected rolling update

    To prevent new versions of TiDB Operator from introducing compatibility issues into the clusters, before updating TiDB Operator, you can pause sync of TiDB clusters. After updating TiDB Operator, you can resume syncing clusters one by one, or specify a time for resume. In this way, you can observe how the rolling update of TiDB Operator would affect the cluster.

- Avoid multiple rolling restarts

    In some cases, you might need to continuously modify the cluster over a period of time, but do not want to restart the TiDB cluster many times. To avoid multiple rolling restarts, you can pause sync of the cluster. During the sync pausing, any change of the configuration does not take effect on the cluster. After you finish the modification, resume sync of the TiDB cluster. All changes can be applied in a single rolling restart.

- Maintenance window

    In some situations, you can update or restart the TiDB cluster only during a maintenance window. When outside the maintenance window, you can pause sync of the TiDB cluster, so that any modification to the specs does not take effect. When inside the maintenance window, you can resume sync of the TiDB cluster to allow TiDB cluster to rolling update or restart.

## Pause TiDB cluster sync

To pause sync of a TiDB cluster, set `spec.paused: true` in the Cluster CR.

1. Run the following command to modify the TiDB cluster configuration. `${cluster_name}` represents the name of the TiDB cluster, and `${namespace}` represents the TiDB cluster namespace.

    ```shell
    kubectl patch cluster ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"paused": true}}'
    ```

2. After the sync is paused, you can confirm the cluster status by checking the TiDB Operator Pod logs. `${pod_name}` represents the name of TiDB Operator Pod, and `${namespace}` represents the namespace of TiDB Operator.

    ```shell
    kubectl logs ${pod_name} -n ${namespace} | grep paused
    ```

   The following output indicates that the sync of all components in the TiDB cluster is paused.

    ```
    2025-04-25T09:27:27.866Z    INFO    TiCDC    cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.866Z    INFO    TiDB     cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.867Z    INFO    TiFlash  cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.868Z    INFO    PD       cluster paused is updating    {"from": false, "to": true}
    2025-04-25T09:27:27.868Z    INFO    TiKV     cluster paused is updating    {"from": false, "to": true}
    ```

## Resume TiDB cluster sync

To resume the sync of the TiDB cluster, set `spec.paused: false` in the Cluster CR. Once resumed, TiDB Operator immediately processes all configuration changes that accumulated during the pause.

1. Run the following command to modify the TiDB cluster configuration. `${cluster_name}` represents the name of the TiDB cluster, and `${namespace}` represents the TiDB cluster namespace.

    ```shell
    kubectl patch cluster ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"paused": false}}'
    ```

2. After the sync is resumed, you can confirm the cluster status by checking the TiDB Operator Pod logs. `${pod_name}` represents the name of TiDB Operator Pod, and `${namespace}` represents the namespace of TiDB Operator.

    ```shell
    kubectl logs ${pod_name} -n ${namespace} | grep "paused"
    ```

    The following output shows that the timestamp when the `cluster paused` status changes from `true` to `false` is later than the timestamp when it changes from `false` to `true`, indicating that the sync is resumed.

    ```
    2025-04-25T09:32:38.867Z    INFO    TiKV     cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    PD       cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    TiFlash  cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    TiCDC    cluster paused is updating    {"from": true, "to": false}
    2025-04-25T09:32:38.868Z    INFO    TiDB     cluster paused is updating    {"from": true, "to": false}
    ```
