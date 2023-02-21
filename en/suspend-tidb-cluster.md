---
title: Suspend TiDB cluster
summary: Learn how to suspend the TiDB cluster on Kubernetes through configuration.
---

# Suspend TiDB cluster

This document introduces how to suspend the TiDB cluster  or suspend the TiDB cluster components on Kubernetes by configuring the `TidbCluster` object. After suspending the cluster, you can stop the Pods of all components or one component, and retain the `TidbCluster` object and other resources (such as Service, PVC, etc.).

In some test scenarios, if you need to save resources, you can suspend the TiDB cluster when you are not using it,

> **Note:**
>
> Suspending the TiDB cluster requires TiDB Operator version >= 1.3.7.

## Configure TiDB cluster suspending

If you need to suspend the TiDB cluster, execute the following steps:

1. In the `TidbCluster` object, configure `spec.suspendAction` field to suspend the entire TiDB cluster:

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

    TiDB Operator also supports suspending one or more components in TiDB clusters. Take TiKV as an example, suspend TiKV in the TiDB cluster by configuring `spec.tikv.suspendAction` field in the `TidbCluster` object.

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

2. After suspending the TiDB cluster, observe that the Pod of the suspended component is gradually deleted through the following command.

    ```shell
    kubectl -n ${namespace} get pods
    ```

    Pods of each suspended component will be deleted in the following order:

    * TiDB
    * TiFlash
    * TiCDC
    * TiKV
    * Pump
    * PD

## Restore TiDB cluster

After the TiDB cluster or component is suspended, if you need to restore the TiDB cluster, execute the following steps:

1. In the `TidbCluster` object, configure `spec.suspendAction` field to restore the entire suspended TiDB cluster:

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

    TiDB Operator also supports to restore one or more components in the TiDB clusters. Take TiKV as an example, restore TiKV in the TiDB cluster by configuring `spec.tikv.suspendAction` field in the `TidbCluster` object.

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

2. After restoring the TiDB cluster, observe that the Pod of the suspended component is gradually created through the following command.

    ```shell
    kubectl -n ${namespace} get pods
    ```
