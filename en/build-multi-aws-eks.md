---
title: Build Multiple Connected AWS EKS Clusters
summary:
---

# Build Multiple Connected AWS EKS Clusters

This document describes how to create multiple AWS EKS clusters and configure network connections between the clusters. The connected clusters can be used for [deploying TiDB clusters across multiple Kubernetes clusters](deploy-tidb-cluster-across-multiple-kubernetes.md). The example in this document shows how to build three connected EKS clusters.

If you need to deploy TiDB on a single AWS EKS cluster, refer to [Deploy TiDB on AWS EKS](deploy-on-aws-eks.md).

## Prerequisites

Before you start building multiple connected EKS clusters, make sure you have completed the following preparations:

- Install [Helm 3](https://helm.sh/docs/intro/install/). You need to use Helm to install TiDB Operator.

- Complete all steps in [Getting started with Amazon EKS – eksctl](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html).

    This tutorial includes the following tasks:

    - Install and configure the AWS CLI (`awscli`).
    - Install and configure the CLI for creating Kubernetes clusters (`eksctl`).
    - Install the Kubernetes CLI (`kubectl`)

- AWS Access Key has at least the [minimum permissions required for `eksctl`](https://eksctl.io/usage/minimum-iam-policies/) and the [permissions required for creating a Linux bastion](https://aws-quickstart.github.io/quickstart-linux-bastion/#_aws_account).

To verify whether you have correctly configured the AWS CLI, run the `aws configure list` command. If the output shows the values of `access_key` and `secret_key`, you have successfully configured the AWS CLI. Otherwise, you need to reconfigure the AWS CLI.

## Step 1. Start the Kubernetes cluster

Define the configuration files of three Kubernetes clusters as `cluster_1.yaml`, `cluster_2.yaml`, and `cluster_3.yaml`. Create three clusters using `eksctl`.

1. Define the configuration file of Cluster 1, and create Cluster 1.

    Save the following content as `cluster_1.yaml`. `${cluster_1}` is the name of the EKS cluster. `${region_1}` is the Region that the EKS cluster is deployed in. `${cidr_block_1}` is the CIDR block of the VPC that the EKS cluster belongs to.

    ```yaml
    apiVersion: eksctl.io/v1alpha5
    kind: ClusterConfig

    metadata:
      name: ${cluster_1}
      region: ${region_1}

    # nodeGroups ...

    vpc:
      cidr: ${cidr_block_1}
    ```

    For the configuration of the `nodeGroups` field, refer to [Create an EKS cluster and a node pool](deploy-on-aws-eks.md#create-an-eks-cluster-and-a-node-pool).

    Create Cluster 1 by running the following command:

    {{< copyable "shell-regular" >}}

    ```bash
    eksctl create cluster -f cluster_1.yaml
    ```

    After running the command above, wait until the EKS cluster is successfully created and the node group is created and added to the EKS cluster. This process might take 5 to 20 minutes. For more cluster configuration, refer to [`eksctl` documentation](https://eksctl.io/usage/creating-and-managing-clusters/#using-config-files).

2. Refer to Step 1, define the configuration files of Cluster 2 and Cluster 3, and create Cluster 2 and Cluster 3.

    The CIDR block of the VPC that each EKS cluster belongs to **must not** overlap with that of each other.

    In the following sections:

    - `${cluster_1}`, `${cluster_2}`, and `${cluster_3}` refer to the name of the clusters.
    - `${region_1}`, `${region_2}`, and `${region_3}` refer to the Region that the clusters are deployed in.
    - `${cidr_block_1}`, `${cidr_block_2}`, and `${cidr_block_3}` refer to the CIDR block of the VPC that the clusters belong to.

3. After the clusters are created, obtain the Kubernetes context of each cluster. The context will be used in the subsequent `kubectl` commands.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl config get-contexts
    ```

    <details>
    <summary>Toggle expected output. The context is in the `NAME` column.</summary>
    <pre><code>
    CURRENT   NAME                                 CLUSTER                      AUTHINFO                            NAMESPACE
    *         pingcap@tidb-1.us-west-1.eksctl.io   tidb-1.us-west-1.eksctl.io   pingcap@tidb-1.us-west-1.eksctl.io
             pingcap@tidb-2.us-west-2.eksctl.io   tidb-2.us-west-2.eksctl.io   pingcap@tidb-2.us-west-2.eksctl.io
             pingcap@tidb-3.us-east-1.eksctl.io   tidb-3.us-east-1.eksctl.io   pingcap@tidb-3.us-east-1.eksctl.io
    </code></pre>
    </details>

    In the following sections, `${context_1}`, `${context_2}`, and `${context_3}` refer to the context of each cluster.

## Step 2. Configure network

### Configure VPC peering

To connect the three clusters, you need to create a VPC peering connection between the VPCs of every two clusters. For details on VPC peering, see [AWS documentation](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html).

1. Get the VPC ID of each cluster. The following example gets the VPC ID of Cluster 1:

    {{< copyable "shell-regular" >}}

    ```bash
    eksctl get cluster ${cluster_1} --region ${region_1}
    ```

    <details>
    <summary>Toggle expected output. The VPC ID is in the `VPC` column.</summary>
    <pre><code>
    NAME          VERSION STATUS  CREATED                 VPC                       SUBNETS                                                                                                                   SECURITYGROUPS
    tidb-1        1.20    ACTIVE  2021-11-22T06:40:20Z    vpc-0b15ed35c02af5288   subnet-058777d55881c4095, subnet-06def2041b6fa3fa0,subnet-0869c7e73e09c3174,subnet-099d10845f6cbaf82,subnet-0a1a58db5cb087fed, subnet-0f68b302678c4d36b     sg-0cb299e7ec153c595
    </code></pre>
    </details>

    In the following sections, `${vpc_id_1}`, `${vpc_id_2}`, and `${vpc_id_3}` refer to the VPC ID of each cluster.

2. Create a VPC peering connection between the VPCs of Cluster 1 and Cluster 2.

    1. Refer to [AWS VPC peering documentation](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#create-vpc-peering-connection-local) and create a VPC peering. Use `${vpc_id_1}` as the requester VPC and ${vpc_id_2} as the accepter VPC.

    2. Refer to [AWS VPC peering documentation](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#accept-vpc-peering-connection) and complete creating a VPC peering.

3. Refer to Step 2, create a VPC peering between Cluster 1 and Cluster 3, and create a VPC peering between Cluster 2 and Cluster 3.

4. [Update the route tables](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-routing.html) for the VPC peering.

    You need to update the route tables of all subnets used by the clusters. Add two routes in each route table. Take the route table of Cluster 1 as an example:

    | Destination     | Target               | Status | Propagated |
    | --------------- | -------------------- | ------ | ---------- |
    | ${cidr_block_2} | ${vpc_peering_id_12} | Active | No         |
    | ${cidr_block_3} | ${vpc_peering_id_13} | Active | No         |

    The **Destination** of each route is the CIDR block of another cluster. **Target** is the VPC peering ID of the two clusters.

### Update the security groups for the instances

1. Update the security group for Cluster 1.
