---
title: Replace Nodes for a TiDB Cluster on Local Disks
summary: Learn how to replace and upgrade nodes without downtime for a TiDB cluster that uses local storage.
---

# Replace Nodes for a TiDB Cluster on Local Disks

This document describes a method for replacing and upgrading nodes without downtime for a TiDB cluster that uses local storage.

> **Note:**
>
> If you only need to maintain a specific node in the TiDB cluster, refer to [Maintain Kubernetes Nodes that Hold the TiDB Cluster](maintain-a-kubernetes-node.md).

## Prerequisites

- A TiDB cluster is deployed. If not, refer to [Deploy TiDB in General Kubernetes](deploy-on-general-kubernetes.md) and deploy a cluster.
- The new node is ready and joins the Kubernetes cluster.

## Step 1: Clone the configuration of the original TiDB cluster

1. Export a copy of the cluster configuration file, `tidb-cluster-clone.yaml`, by running the following command:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl get tidbcluster ${origin_cluster_name} -n ${namespace} -oyaml > tidb-cluster-clone.yaml
    ```

    `${origin_cluster_name}` is the name of the original cluster. `${namespace}` is the namespace of the original cluster.

2. Modify `tidb-cluster-clone.yaml` and allow the new clone cluster to join the original TiDB cluster.

    ```yaml
    kind: TidbCluster
    metadata:
      name: ${clone_cluster_name}
    spec:
      cluster:
        name: ${origin_cluster_name}
    ...
    ```

    `${clone_cluster_name}` is the name of the clone cluster. `${origin_cluster_name}` is the name of the original cluster.

## Step 2: Sign certifcates for the clone cluster

If the original cluster enables TLS, you need to sign certificates for the clone cluster. If not, you can skip this step and move to [Step 3](#step-3-mark-the-nodes-to-be-replaced-as-non-schedulable).

### Using cfssl

If you use cfssl to sign certificates, you must sign certificates using the same certification authority (CA) as the original cluster. To complete the signing process, follow instructions in Step 5~7 in [Using cfssl](enable-tls-between-components.md#using-cfssl).

### Using cert-manager

If you use cert-manager, you must sign certificates using the same Issuer as the original cluster. To complete the signing process, follow instructions in Step 3 in [Using cert-manager](enable-tls-between-components.md#using-cert-manager).

## Step 3: Mark the nodes to be replaced as non-schedulable

By marking the nodes to be replaced as non-schedulable, you can ensure that no new Pod is scheduled to the nodes. Run the `kubectl cordon` command:

{{< copyable "shell-regular" >}}

```bash
kubectl cordon ${replace_nodename1} ${replace_nodename2} ...
```

## Step 4: Create the clone cluster

1. Create the clone cluster by running the following command:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl apply -f tidb-cluster-clone.yaml
    ```

2. Confirm that the new TiDB cluster that consists of the clone cluster and the original cluster is running normally.

    - Obtain the count and state of stores in the new cluster:

        {{< copyable "shell-regular" >}}

        ```bash
        # store count
        pd-ctl -u http://<address>:<port> store | jq '.count'
        # store state
        pd-ctl -u http://<address>:<port> store | jq '.stores | .[] | .store.state_name'
        ```

    - [Access the TiDB cluster](access-tidb.md) via MySQL client.

## Step 5: Scale in all TiDB nodes of the original cluster

Scale in all TiDB nodes of the original cluster to 0. For details, refer to [Horizontal scaling](scale-a-tidb-cluster.md#horizontal-scaling).

> **Note:**
>
> If you access the original TiDB cluster via a load balancer or database middleware, before scaling in the original TiDB cluster, you need to modify the configuration to route your application traffic to the target TiDB cluster. Otherwise, your application might be affected.

## Step 6: Scale in all TiKV nodes of the original cluster

Scale in all TiKV nodes of the original cluster to 0. For details, refer to [Horizontal scaling](scale-a-tidb-cluster.md#horizontal-scaling).

## Step 7: Scale in all PD nodes of the original cluster

Scale in all PD nodes of the original cluster to 0. For details, refer to [Horizontal scaling](scale-a-tidb-cluster.md#horizontal-scaling).

## Step 8: Delete the `spec.cluster` field in the clone cluster

Delete the `spec.cluster` field in the clone cluster by running the following command:

{{< copyable "shell-regular" >}}

```bash
kubectl patch -n ${namespace} tc ${clone_cluster_name} --type=json -p '[{"op":"remove", "path":"/spec/cluster"}]'
```

`${namespace}` is the name of the clone cluster (unchanged). `${clone_cluster_name}` is the name of the clone cluster.

## Step 9: Delete the cluster, data, and nodes of the original cluster

1. Delete the `TidbCluster` of the original cluster:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl delete -n ${namespace} tc ${origin_cluster_name}
    ```

    `${namespace}` is the name of the original cluster (unchanged). `${original_cluster_name}` is the name of the original cluster.

2. Delete the data of the original cluster. For details, refer to [Delete PV and data](configure-storage-class.md#delete-pv-and-data).

3. Delete the nodes to be replaced from the Kubernetes cluster:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl delete node ${replace_nodename1} ${replace_nodename2} ...
    ```
