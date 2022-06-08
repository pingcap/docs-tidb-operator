---
title: Replace Nodes for a TiDB Cluster on Cloud Disks
summary: Learn how to replace and upgrade nodes without downtime for a TiDB cluster that uses cloud storage.
---

# Replace Nodes for a TiDB Cluster on Cloud Disks

This document describes a method for replacing and upgrading nodes without downtime for a TiDB cluster that uses cloud storage. You can change the nodes to a higher configuration, or upgrade the nodes to a newer version of Kubernetes.

This document uses Amazon EKS as an example and describes how to create a new node group and migrate a TiDB cluster to the new node group using a rolling restart. You can use this method to replace a node group with more compute resources for TiKV or TiDB and upgrade EKS.

For other cloud platforms, refer to [GCP GKE](deploy-on-gcp-gke.md), [Azure AKS](deploy-on-azure-aks.md), or [Alibaba Cloud ACK](deploy-on-alibaba-cloud.md) and operate on the node group.

## Prerequisites

- A TiDB cluster is deployed on the cloud. If not, refer to [Deploy on Amazon EKS](deploy-on-aws-eks.md) and deploy a cluster.
- The TiDB cluster uses cloud storage as its data disk.

## Step 1: Create new node groups

1. Locate the `cluster.yaml` configuration file for the EKS cluster that the TiDB cluster is deployed in, and save a copy of the file as `cluster-new.yaml`.

2. In `cluster-new.yaml`, add new groups (for example, `tidb-1b-new` and `tikv-1a-new`):

    ```yaml
    apiVersion: eksctl.io/v1alpha5
    kind: ClusterConfig
    metadata:
      name: your-eks-cluster
      region: ap-northeast-1

    nodeGroups:
    ...
      - name: tidb-1b-new
        desiredCapacity: 1
        privateNetworking: true
        availabilityZones: ["ap-northeast-1b"]
        instanceType: c5.4xlarge
        labels:
          dedicated: tidb
        taints:
          dedicated: tidb:NoSchedule
      - name: tikv-1a-new
        desiredCapacity: 1
        privateNetworking: true
        availabilityZones: ["ap-northeast-1a"]
        instanceType: r5b.4xlarge
        labels:
          dedicated: tikv
        taints:
          dedicated: tikv:NoSchedule
    ```

    > **Note:**
    >
    > * `availabilityZones` must be the same as that of the original node group to be replaced.
    > * The `tidb-1b-new` and `tikv-1a-new` node groups configured in the YAML above are only for demonstration. You need to configure the node groups according to your needs.

    If you want to scale up a node, modify `instanceType`. If you want to upgrade the Kubernetes version, first upgrade the version of your cluster control plane. For details, see [Updating a Cluster](https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html).

3. In `cluster-new.yaml`, delete the original node groups to be replaced.

    In this example, delete `tidb-1b` and `tikv-1a`. You need to delete node groups according to your needs.

4. In `cluster.yaml`, delete the node groups that **are not to be replaced** and keep the node groups that are to be replaced. The retained node groups will be deleted from the cluster.

    In this example, keep `tidb-1a` and `tikv-1b`, and delete other node groups. You need to keep or delete node groups according to your needs.

5. Create the new node groups:

    {{< copyable "shell-regular" >}}

    ```bash
    eksctl create nodegroup -f cluster_new.yml
    ```

    > **Note:**
    >
    > This command only creates new node groups. Node groups that already exist are ignored and not created again. The command does not delete the node groups that do not exist.

6. Confirm that the new nodes are added to the cluster.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl get no -l alpha.eksctl.io/nodegroup-name=${new_nodegroup1}
    kubectl get no -l alpha.eksctl.io/nodegroup-name=${new_nodegroup2}
    ...
    ```

   `${new_nodegroup}` is the name of a new node group. In this example, the new node groups are `tidb-1b-new` and `tikv-1a-new`. You need to configure the node group name according to your needs.

## Step 2: Mark the original nodes as non-schedulable

You need to mark the original nodes as non-schedulable to ensure that no new Pod is scheduled to it. Run the `kubectl cordon` command:

{{< copyable "shell-regular" >}}

```bash
kubectl cordon -l alpha.eksctl.io/nodegroup-name=${origin_nodegroup1}
kubectl cordon -l alpha.eksctl.io/nodegroup-name=${origin_nodegroup2}
...
```

`${origin_nodegroup}` is the name of an original node group. In this example, the original node groups are `tidb-1b` and `tikv-1a`. You need to configure the node group name according to your needs.

## Step 3: Rolling restart the TiDB cluster

Refer to [Restart a TiDB Cluster in Kubernetes](restart-a-tidb-cluster.md#perform-a-graceful-rolling-restart-to-all-pods-in-a-component) and perform a rolling restart on the TiDB cluster.

## Step 4: Delete the original node groups

Check whether there are TiDB, PD, or TiKV Pods left on nodes of the original node groups:

{{< copyable "shell-regular" >}}

```bash
kubectl get po -n ${namespace} -owide
```

If no TiDB, PD, or TiKV Pods are left on the nodes of the original node groups, you can delete the original node groups:

{{< copyable "shell-regular" >}}

```bash
eksctl delete nodegroup -f cluster.yaml --approve
```
