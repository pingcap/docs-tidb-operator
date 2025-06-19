---
title: Suspend and Resume a TiDB Cluster on Kubernetes
summary: Learn how to suspend and resume a TiDB cluster on Kubernetes by configuring the cluster.
---

# Suspend and Resume a TiDB Cluster on Kubernetes

This document describes how to suspend and resume a TiDB cluster on Kubernetes by configuring the `Cluster` object. When you suspend a cluster, all component Pods are stopped, but the `Cluster` object and associated resources (such as Services and PVCs) are retained. This preserves the cluster's data and configuration for later recovery.

## Usage scenarios

You can suspend a TiDB cluster in the following scenarios:

- Temporarily release compute resources in a test environment.
- Stop a development cluster that is unused for an extended period.
- Pause a cluster temporarily while retaining its data and configuration.

## Before you begin

Before you suspend a TiDB cluster, consider the following:

- Suspending the cluster interrupts cluster services.
- Existing client connections are terminated forcefully.
- PVCs and data are retained and continue to occupy storage space.
- Services and configurations associated with the cluster remain unchanged.

## Suspend a TiDB cluster

To suspend a TiDB cluster, perform the following steps:

1. In the `Cluster` object, set the `spec.suspendAction.suspendCompute` field to `true` to suspend the entire TiDB cluster:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      suspendAction:
        suspendCompute: true
      # ...
    ```

2. After the cluster is suspended, run the following command to observe the Pods being gradually deleted:

    ```shell
    kubectl -n ${namespace} get pods -w
    ```

## Resume a TiDB cluster

To resume a suspended TiDB cluster, perform the following steps:

1. In the `Cluster` object, set the `spec.suspendAction.suspendCompute` field to `false` to resume the suspended TiDB cluster:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: Cluster
    metadata:
      name: ${cluster_name}
      namespace: ${namespace}
    spec:
      suspendAction:
        suspendCompute: false
      # ...
    ```

2. After the cluster is resumed, run the following command to observe the Pods being gradually created:

    ```shell
    kubectl -n ${namespace} get pods -w
    ```
