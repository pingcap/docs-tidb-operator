---
title: Suspend TiDB cluster
summary: Learn how to suspend the TiDB cluster on Kubernetes through configuration.
---

# Suspend TiDB cluster

This document introduces how to suspend the TiDB cluster or suspend the TiDB cluster components on Kubernetes by configuring the `TidbCluster` object. After suspending the cluster, you can stop the Pods of all components or one specfic component and retain the `TidbCluster` object and other resources (such as Service and PVC).

In some test scenarios, if you need to save resources, you can suspend the TiDB cluster when you are not using it.

> **Note:**
>
> To suspend the TiDB cluster, the TiDB Operator version must be >= v1.3.7.

## Configure TiDB cluster suspending

If you need to suspend the TiDB cluster, take the following steps:

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

    TiDB Operator also supports suspending one or more components in TiDB clusters. Taking TiKV as an example, you can suspend TiKV in the TiDB cluster by configuring `spec.tikv.suspendAction` field in the `TidbCluster` object:

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

2. After suspending the TiDB cluster, you can run the following command to observe that the Pods of the suspended component are gradually deleted.

    ```shell
    kubectl -n ${namespace} get pods
    ```

    Pods of each suspended component will be deleted in the following order:

    * TiDB
    * TiFlash
    * TiCDC
    * TiKV
    * Pump
    * TiProxy
    * PD

> **Notes:**
>
> If [PD microservices](pd-microservices.md) (introduced in TiDB v8.0.0) are deployed in a cluster, the Pods of PD microservices are deleted after the PD Pods are deleted.

## Restore TiDB cluster

After a TiDB cluster or its component is suspended, if you need to restore the TiDB cluster, take the following steps:

1. In the `TidbCluster` object, configure the `spec.suspendAction` field to restore the entire suspended TiDB cluster:

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

    TiDB Operator also supports restoring one or more components in the TiDB cluster. Taking TiKV as an example, you can restore TiKV in the TiDB cluster by configuring `spec.tikv.suspendAction` field in the `TidbCluster` object.

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

2. After restoring the TiDB cluster, you can run the following command to observe that the Pods of the suspended component are gradually created.

    ```shell
    kubectl -n ${namespace} get pods
    ```
