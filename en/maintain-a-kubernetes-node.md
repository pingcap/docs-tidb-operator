---
title: Maintain Kubernetes Nodes that Hold the TiDB Cluster
summary: Learn how to maintain Kubernetes nodes that hold the TiDB cluster.
---

# Maintain Kubernetes Nodes that Hold the TiDB Cluster

TiDB is a highly available database that can run smoothly when some of the database nodes go offline. For this reason, you can safely shut down and maintain the Kubernetes nodes at the bottom layer without influencing TiDB's service.

This document describes in detail how to perform maintenance operations on Kubernetes nodes. Different operation strategies are provided based on maintenance duration and storage type.

## Prerequisites

- [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

> **Note:**
>
> Before you maintain a node, you need to make sure that the remaining resources in the Kubernetes cluster are enough for running the TiDB cluster.

## Maintain a node

### Step 1: Preparation

1. Use the `kubectl cordon` command to mark the node to be maintained as unschedulable to prevent new Pods from being scheduled to the node:

    ```shell
    kubectl cordon ${node_name}
    ```

2. Check if there are TiDB cluster component Pods on the node to be maintained:

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/managed-by=tidb-operator | grep ${node_name}
    ```

### Step 2: Migrate TiDB cluster component Pods

Choose the appropriate Pod migration strategy based on your storage type:

#### Option A: Reschedule Pods (for automatically migratable storage)

If the node storage can be automatically migrated (such as [Amazon EBS](https://aws.amazon.com/ebs/)), you can refer to [Gracefully restart a single Pod of a component](restart-a-tidb-cluster.md) to reschedule component Pods. Using the PD component as an example:

1. Check the PD Pods on the node to be maintained:

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/component=pd | grep ${node_name}
    ```

2. Check the instance name corresponding to the PD Pod:

    ```shell
    kubectl get pod -n ${namespace} ${pod_name} -o jsonpath='{.metadata.labels.pingcap\.com/instance}'
    ```

3. Add a new label to the PD instance to trigger rescheduling:

    ```shell
    kubectl label pd -n ${namespace} ${pd_instance_name} pingcap.com/restartedAt=2025-06-30T12:00
    ```

4. Confirm that the PD Pod has been successfully scheduled to other nodes:

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

5. Repeat the above steps for other components (TiKV, TiDB, etc.) until all TiDB cluster component Pods on the maintenance node have been migrated.

#### Option B: Recreate instances (for local storage)

If the node storage cannot be automatically migrated (such as local storage), you need to recreate instances:

> **Warning:**
>
> Recreating instances will cause data loss. For stateful components like TiKV, ensure that the cluster has sufficient replicas to guarantee data safety.

Using recreating a TiKV instance as an example:

1. Delete the TiKV instance CR. TiDB Operator will delete its associated PVC, ConfigMap, and other resources, and automatically create a new instance:

    ```shell
    kubectl delete -n ${namespace} tikv ${tikv_instance_name}
    ```

2. Wait for the newly created TiKV instance status to become ready:

    ```shell
    kubectl get -n ${namespace} tikv ${tikv_instance_name}
    ```

3. After confirming that the TiDB cluster status is normal and data synchronization is complete, you can continue to maintain other components.

### Step 3: Confirm migration completion

At this point, there should only be Pods managed by DaemonSets (such as network plugins, monitoring agents, etc.):

```shell
kubectl get pod --all-namespaces -o wide | grep ${node_name}
```

### Step 4: Perform node maintenance

At this point, you can safely perform node maintenance operations (such as restart, system update, hardware maintenance, etc.).

### Step 5: Post-maintenance recovery (only for temporary maintenance)

If it is temporary maintenance, you need to restore the node after maintenance is completed:

1. Confirm the node health status:

    ```shell
    watch kubectl get node ${node_name}
    ```

    After observing that the node enters the `Ready` state, proceed to the next step.

2. Use the `kubectl uncordon` command to remove the node's scheduling restrictions:

    ```shell
    kubectl uncordon ${node_name}
    ```

3. Observe whether all Pods have returned to normal operation:

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

    After the Pods return to normal operation, the maintenance operation is complete.

If it is long-term maintenance or permanent node removal, this step is not required.
