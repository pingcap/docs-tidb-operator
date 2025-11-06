---
title: Maintain Kubernetes Nodes That Hold the TiDB Cluster
summary: Learn how to maintain Kubernetes nodes that hold the TiDB cluster.
---

# Maintain Kubernetes Nodes That Hold the TiDB Cluster

TiDB is a highly available database that can run smoothly when some of the database nodes go offline. Therefore, you can safely shut down and maintain the Kubernetes nodes that host TiDB clusters.

This document describes how to perform maintenance operations on Kubernetes nodes based on maintenance duration and storage type.

## Prerequisites

- Install [`kubectl`](https://kubernetes.io/docs/tasks/tools/).

> **Note:**
>
> Before you maintain a node, make sure that the remaining resources in the Kubernetes cluster are enough for running the TiDB cluster.

## Maintain a node

### Step 1: Preparation

1. Use the `kubectl cordon` command to mark the node to be maintained as unschedulable to prevent new Pods from being scheduled to this node:

    ```shell
    kubectl cordon ${node_name}
    ```

2. Check whether any TiDB cluster component Pods are running on the node to be maintained:

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/managed-by=tidb-operator | grep ${node_name}
    ```

    - If the node has TiDB cluster component Pods, follow the subsequent steps in this document to migrate these Pods.  
    - If the node does not have any TiDB cluster component Pods, there is no need to migrate Pods, and you can proceed directly with node maintenance.

### Step 2: Migrate TiDB cluster component Pods

Based on the storage type of the Kubernetes node, choose the corresponding Pod migration strategy:

- **Automatically migratable storage**: use [Method 1: Reschedule Pods](#method-1-reschedule-pods-for-automatically-migratable-storage).
- **Non-automatically migratable storage**: use [Method 2: Recreate instances](#method-2-recreate-instances-for-local-storage).

#### Method 1: Reschedule Pods (for automatically migratable storage)

If you use storage that supports automatic migration (such as [Amazon EBS](https://aws.amazon.com/ebs/)), you can reschedule component Pods by following [Perform a graceful restart of a single Pod in a component](restart-a-tidb-cluster.md#perform-a-graceful-restart-of-a-single-pod-in-a-component). The following instructions take rescheduling PD Pods as an example:

1. Check the PD Pod on the node to be maintained:

    ```shell
    kubectl get pod --all-namespaces -o wide -l pingcap.com/component=pd | grep ${node_name}
    ```

2. Get the instance name of the PD Pod:

    ```shell
    kubectl get pod -n ${namespace} ${pod_name} -o jsonpath='{.metadata.labels.pingcap\.com/instance}'
    ```

3. Add a new label to the PD instance to trigger rescheduling:

    ```shell
    kubectl label pd -n ${namespace} ${pd_instance_name} pingcap.com/restartedAt=2025-06-30T12:00
    ```

4. Confirm that the PD Pod is successfully scheduled to another node:

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

5. Follow the same steps to migrate Pods of other components such as TiKV and TiDB until all TiDB cluster component Pods on the node are migrated.

#### Method 2: Recreate instances (for local storage)

If the node uses storage that cannot be automatically migrated (such as local storage), you need to recreate instances.

> **Warning:**
>
> Recreating instances causes data loss. For stateful components such as TiKV, ensure that the cluster has sufficient replicas to guarantee data safety.

The following instructions take recreating a TiKV instance as an example:

1. Delete the CR of the TiKV instance. TiDB Operator automatically deletes the associated PVC and ConfigMap resources, and creates a new instance:

    ```shell
    kubectl delete -n ${namespace} tikv ${tikv_instance_name}
    ```

2. Wait for the status of the newly created TiKV instance to become `Ready`:

    ```shell
    kubectl get -n ${namespace} tikv ${tikv_instance_name}
    ```

3. After you confirm that the TiDB cluster status is normal and data synchronization is completed, continue to maintain other components.

### Step 3: Confirm migration completion

After you complete Pod migration, only the Pods managed by DaemonSet (such as network plugins and monitoring agents) should be running on the node:

```shell
kubectl get pod --all-namespaces -o wide | grep ${node_name}
```

### Step 4: Perform node maintenance

You can now safely perform maintenance operations on the node, such as restarting, updating the operating system, or performing hardware maintenance.

### Step 5: Recover after maintenance (for temporary maintenance only)

If you plan to perform long-term maintenance or permanently take the node offline, skip this step.

For temporary maintenance, perform the following recovery operations after the node maintenance is completed:

1. Check the node health status:

    ```shell
    watch kubectl get node ${node_name}
    ```

    When the node status becomes `Ready`, continue to the next step.

2. Use the `kubectl uncordon` command to remove the scheduling restriction on the node:

    ```shell
    kubectl uncordon ${node_name}
    ```

3. Check whether all Pods are running normally:

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

    When all Pods are running normally, the maintenance operation is completed.
