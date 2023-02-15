---
title: Build Multiple Interconnected AWS EKS Clusters
summary: Learn how to build multiple interconnected AWS EKS clusters and prepare for deploying a TiDB cluster across multiple EKS clusters.
---

# Build Multiple Interconnected AWS EKS Clusters

This document describes how to create multiple AWS EKS clusters and configure network peering between these clusters. These interconnected clusters can be used for [deploying TiDB clusters across multiple Kubernetes clusters](deploy-tidb-cluster-across-multiple-kubernetes.md). The example in this document shows how to configure three-cluster network peering.

If you need to deploy TiDB on a single AWS EKS cluster, refer to [Deploy TiDB on AWS EKS](deploy-on-aws-eks.md).

## Prerequisites

Before you deploy EKS clusters, make sure you have completed the following preparations:

- Install [Helm 3](https://helm.sh/docs/intro/install/). You need to use Helm to install TiDB Operator.

- Complete all steps in [Getting started with Amazon EKS—eksctl](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html).

    This tutorial includes the following tasks:

    - Install and configure the AWS CLI (`awscli`).
    - Install and configure the CLI for creating Kubernetes clusters (`eksctl`).
    - Install the Kubernetes CLI (`kubectl`)

- Grant AWS Access Key the [minimum permissions required for `eksctl`](https://eksctl.io/usage/minimum-iam-policies/) and the [permissions required for creating a Linux bastion](https://aws-quickstart.github.io/quickstart-linux-bastion/#_aws_account).

To verify whether you have correctly configured the AWS CLI, run the `aws configure list` command. If the output shows the values of `access_key` and `secret_key`, you have successfully configured the AWS CLI. Otherwise, you need to reconfigure the AWS CLI.

## Step 1. Start the Kubernetes cluster

Define the configuration files of three EKS clusters as `cluster_1.yaml`, `cluster_2.yaml`, and `cluster_3.yaml`, and create three clusters using `eksctl`.

1. Define the configuration file of cluster 1, and create cluster 1.

    1. Save the following content as `cluster_1.yaml`. `${cluster_1}` is the name of the EKS cluster. `${region_1}` is the Region that the EKS cluster is deployed in. `${cidr_block_1}` is the CIDR block for the VPC that the EKS cluster is deployed in.

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

    2. Create cluster 1 by running the following command:

        {{< copyable "shell-regular" >}}

        ```bash
        eksctl create cluster -f cluster_1.yaml
        ```

    After running the command above, wait until the EKS cluster is successfully created and the node group is created and added to the EKS cluster. This process might take 5 to 20 minutes. For more cluster configuration, refer to [Using Config Files](https://eksctl.io/usage/creating-and-managing-clusters/#using-config-files).

2. Follow the instructions in the previous step and create cluster 2 and cluster 3.

    The CIDR block for each EKS cluster **must not** overlap with that of each other.

    In the following sections:

    - `${cluster_1}`, `${cluster_2}`, and `${cluster_3}` refer to the cluster names.
    - `${region_1}`, `${region_2}`, and `${region_3}` refer to the Regions that the clusters are deployed in.
    - `${cidr_block_1}`, `${cidr_block_2}`, and `${cidr_block_3}` refer to the CIDR blocks for the VPCs that the clusters are deployed in.

3. After the clusters are created, obtain the Kubernetes context of each cluster. The contexts are used in the subsequent `kubectl` commands.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl config get-contexts
    ```

    <details>
    <summary>Expected output</summary>

    The context is in the <code>NAME</code> column.

    <pre><code>
    CURRENT   NAME                                 CLUSTER                      AUTHINFO                            NAMESPACE
    *         pingcap@tidb-1.us-west-1.eksctl.io   tidb-1.us-west-1.eksctl.io   pingcap@tidb-1.us-west-1.eksctl.io
              pingcap@tidb-2.us-west-2.eksctl.io   tidb-2.us-west-2.eksctl.io   pingcap@tidb-2.us-west-2.eksctl.io
              pingcap@tidb-3.us-east-1.eksctl.io   tidb-3.us-east-1.eksctl.io   pingcap@tidb-3.us-east-1.eksctl.io
    </code></pre>
    </details>

    In the following sections, `${context_1}`, `${context_2}`, and `${context_3}` refer to the context of each cluster.

## Step 2. Configure the network

### Set up VPC peering

To allow the three clusters to access each other, you need to create a VPC peering connection between the VPCs of every two clusters. For details on VPC peering, see [AWS documentation](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html).

1. Get the VPC ID of each cluster.

    The following example gets the VPC ID of cluster 1:

    {{< copyable "shell-regular" >}}

    ```bash
    eksctl get cluster ${cluster_1} --region ${region_1}
    ```

    <details>
    <summary>Expected output</summary>

    The VPC ID is in the <code>VPC</code> column.

    <pre><code>
    NAME          VERSION STATUS  CREATED                 VPC                       SUBNETS                                                                                                                   SECURITYGROUPS
    tidb-1        1.20    ACTIVE  2021-11-22T06:40:20Z    vpc-0b15ed35c02af5288   subnet-058777d55881c4095, subnet-06def2041b6fa3fa0,subnet-0869c7e73e09c3174,subnet-099d10845f6cbaf82,subnet-0a1a58db5cb087fed, subnet-0f68b302678c4d36b     sg-0cb299e7ec153c595
    </code></pre>
    </details>

    In the following sections, `${vpc_id_1}`, `${vpc_id_2}`, and `${vpc_id_3}` refer to the VPC ID of each cluster.

2. Create a VPC peering connection between cluster 1 and cluster 2.

    1. Refer to [AWS documentation](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#create-vpc-peering-connection-local) and create a VPC peering. Use `${vpc_id_1}` as the requester VPC and `${vpc_id_2}` as the accepter VPC.

    2. Refer to [AWS documentation](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#accept-vpc-peering-connection) and complete creating a VPC peering.

3. Follow the instructions in the previous step. Create a VPC peering connection between cluster 1 and cluster 3 and a VPC peering connection between cluster 2 and cluster 3.

4. [Update the route tables](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-routing.html) for the VPC peering connection of the three clusters.

    You need to update the route tables of all subnets used by the clusters. Add two routes in each route table.

    The following example shows the route table of cluster 1:

    | Destination     | Target               | Status | Propagated |
    | --------------- | -------------------- | ------ | ---------- |
    | `${cidr_block_2}` | `${vpc_peering_id_12}` | Active | No         |
    | `${cidr_block_3}` | `${vpc_peering_id_13}` | Active | No         |

    The **Destination** of each route is the CIDR block of another cluster. The **Target** is the VPC peering ID of the two clusters.

### Update the security groups for the instances

1. Update the security group for cluster 1.

    1. Enter the [AWS Security Groups Console](https://us-west-2.console.aws.amazon.com/ec2/v2/home#SecurityGroups) and select the security group of cluster 1. The name of the security group is similar to `eksctl-${cluster_1}-cluster/ClusterSharedNodeSecurityGroup`.

    2. Add inbound rules to the security group to allow traffic from cluster 2 and cluster 3.

        | Type        | Protocol | Port range | Source                 | Description                                   |
        | ----------- | -------- | ---------- | ---------------------- | --------------------------------------------- |
        | All traffic | All      | All        | Custom `${cidr_block_2}` | Allow cluster 2 to communicate with cluster 1 |
        | All traffic | All      | All        | Custom `${cidr_block_3}` | Allow cluster 3 to communicate with cluster 1 |

2. Follow the instructions in the previous step to update the security groups for cluster 2 and cluster 3.

### Configure load balancers

Each cluster needs to expose its CoreDNS service to other clusters via a [network load balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html). This section describes how to configure load balancers.

1. Create a load balancer service definition file `dns-lb.yaml` as follows:

    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      labels:
        k8s-app: kube-dns
      name: across-cluster-dns-tcp
      namespace: kube-system
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
        service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
        service.beta.kubernetes.io/aws-load-balancer-internal: "true"
    spec:
      ports:
      - name: dns
        port: 53
        protocol: TCP
        targetPort: 53
      selector:
        k8s-app: kube-dns
      type: LoadBalancer
    ```

2. Deploy the load balancer service in each cluster:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl --context ${context_1} apply -f dns-lb.yaml

    kubectl --context ${context_2} apply -f dns-lb.yaml

    kubectl --context ${context_3} apply -f dns-lb.yaml
    ```

3. Get the load balancer name of each cluster, and wait for all load balancers to become `Active`.

    Get the load balancer names by running the following commands:

    {{< copyable "shell-regular" >}}

    ```bash
    lb_name_1=$(kubectl --context ${context_1} -n kube-system get svc across-cluster-dns-tcp -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" | cut -d - -f 1)

    lb_name_2=$(kubectl --context ${context_2} -n kube-system get svc across-cluster-dns-tcp -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" | cut -d - -f 1)

    lb_name_3=$(kubectl --context ${context_3} -n kube-system get svc across-cluster-dns-tcp -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" | cut -d - -f 1)
    ```

    Check the load balancer status of each cluster by running the following commands. If the output of all commands is `active`, all load balancers are in the `Active` state.

    {{< copyable "shell-regular" >}}

    ```bash
    aws elbv2 describe-load-balancers --names ${lb_name_1} --region ${region_1} --query 'LoadBalancers[*].State' --output text

    aws elbv2 describe-load-balancers --names ${lb_name_2} --region ${region_2} --query 'LoadBalancers[*].State' --output text

    aws elbv2 describe-load-balancers --names ${lb_name_3} --region ${region_3} --query 'LoadBalancers[*].State' --output text
    ```

    <details>
    <summary>Expected output</summary>
    <pre><code>
    active
    active
    active</code></pre>
    </details>

4. Check the IP address associated with the load balancer of each cluster.

    Check the IP address associated with the load balancer of cluster 1:

    {{< copyable "shell-regular" >}}

    ```bash
    aws ec2 describe-network-interfaces --region ${region_1} --filters Name=description,Values="ELB net/${lb_name_1}*" --query  'NetworkInterfaces[*].PrivateIpAddress' --output text
    ```

    <details>
    <summary>Expected output</summary>
    <pre><code>10.1.175.233 10.1.144.196</code></pre>
    </details>

    Repeat the same step for cluster 2 and cluster 3.

    In the following sections, `${lb_ip_list_1}`, `${lb_ip_list_2}`, and `${lb_ip_list_3}` refer to the IP addresses associated with the load balancer of each cluster.

    The load balancers in different Regions might have different numbers of IP addresses. For example, in the example above, `${lb_ip_list_1}` is `10.1.175.233 10.1.144.196`.

### Configure CoreDNS

To allow Pods in a cluster to access services in other clusters, you need to configure CoreDNS for each cluster to forward DNS requests to the CoreDNS services of other clusters.

You can configure CoreDNS by modifying the ConfigMap corresponding to the CoreDNS. For information on more configuration items, refer to [Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#coredns).

1. Modify the CoreDNS configuration of cluster 1.

    1. Back up the current CoreDNS configuration:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl --context ${context_1} -n kube-system get configmap coredns -o yaml > ${cluster_1}-coredns.yaml.bk
        ```

    2. Modify the ConfigMap:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl --context ${context_1} -n kube-system edit configmap coredns
        ```

        Modify the `data.Corefile` field as follows. In the example below, `${namespace_2}` and `${namespace_3}` are the namespaces that cluster 2 and cluster 3 deploy `TidbCluster` in.

        > **Warning:**
        >
        > Because you cannot modify the cluster domain of an EKS cluster, you need to use the namespace as an identifier for DNS forwarding. Therefore, `${namespace_1}`, `${namespace_2}`, and `${namespace_3}` must be different from each other.

        ```yaml
        apiVersion: v1
        kind: ConfigMap
        # ...
        data:
          Corefile: |
             .:53 {
                # Do not modify the default configuration.
             }
             ${namespace_2}.svc.cluster.local:53 {
                 errors
                 cache 30
                 forward . ${lb_ip_list_2} {
                     force_tcp
                 }
             }
             ${namespace_3}.svc.cluster.local:53 {
                 errors
                 cache 30
                 forward . ${lb_ip_list_3} {
                     force_tcp
                 }
             }
        ```

    3. Wait for the CoreDNS to reload the configuration. It might take around 30 seconds.

2. Follow the instructions in the previous step, and modify the CoreDNS configuration of cluster 2 and cluster 3.

    For the CoreDNS configuration of each cluster, you need to perform the following operations:

    - Configure `${namespace_2}` and `${namespace_3}` to the namespace that the other two clusters deploy `TidbCluster` in.
    - Configure the IP address to the IP addresses of the load balancers of the other two clusters.

In the following sections, `${namespace_1}`, `${namespace_2}`, and `${namespace_3}` refer to the namespaces that each cluster deploy `TidbCluster` in.

## Step 3. Verify the network interconnectivity

Before you deploy the TiDB cluster, you need to verify that the network between the EKS clusters is interconnected.

1. Save the following content in the `sample-nginx.yaml` file.

    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: sample-nginx
      labels:
        app: sample-nginx
    spec:
      hostname: sample-nginx
      subdomain: sample-nginx-peer
      containers:
      - image: nginx:1.21.5
        imagePullPolicy: IfNotPresent
        name: nginx
        ports:
          - name: http
            containerPort: 80
      restartPolicy: Always
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: sample-nginx-peer
    spec:
      ports:
        - port: 80
      selector:
        app: sample-nginx
      clusterIP: None
    ```

2. Deploy the nginx service to the namespaces of the three clusters:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl --context ${context_1} -n ${namespace_1} apply -f sample-nginx.yaml

    kubectl --context ${context_2} -n ${namespace_2} apply -f sample-nginx.yaml

    kubectl --context ${context_3} -n ${namespace_3} apply -f sample-nginx.yaml
    ```

3. Access the nginx services of each cluster to verify the network interconnectivity.

    The following command verifies the network from cluster 1 to cluster 2:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl --context ${context_1} -n ${namespace_1} exec sample-nginx -- curl http://sample-nginx.sample-nginx-peer.${namespace_2}.svc.cluster.local:80
    ```

    If the output is the welcome page of nginx, the network is connected.

4. After the verification, delete the nginx services:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl --context ${context_1} -n ${namespace_1} delete -f sample-nginx.yaml

    kubectl --context ${context_2} -n ${namespace_2} delete -f sample-nginx.yaml

    kubectl --context ${context_3} -n ${namespace_3} delete -f sample-nginx.yaml
    ```

## Step 4. Deploy TiDB Operator

The `TidbCluster` CR of each cluster is managed by TiDB Operator of the cluster. Therefore, you must deploy TiDB Operator for each cluster.

Refer to [Deploy TiDB Operator](deploy-tidb-operator.md) and deploy TiDB Operator in each EKS cluster. Note that you need to use `kubectl --context ${context}` and `helm --kube-context ${context}` in the commands to deploy TiDB Operator for each EKS cluster.

## Step 5. Deploy TiDB clusters

Refer to [Deploy a TiDB Cluster across Multiple Kubernetes Clusters](deploy-tidb-cluster-across-multiple-kubernetes.md) and deploy a `TidbCluster` CR for each EKS cluster. Note the following operations:

* You must deploy the TidbCluster CR in the corresponding namespace configured in the [Configure CoreDNS](#configure-coredns) section. Otherwise, the TiDB cluster will fail to start.

* The cluster domain of each cluster must be set to "cluster.local".

Take cluster 1 as an example. When you deploy the `TidbCluster` CR to cluster 1, specify `metadata.namespace` as `${namespace_1}`:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
   name: ${tc_name_1}
   namespace: ${namespace_1}
spec:
  # ...
  clusterDomain: "cluster.local"
  acrossK8s: true
```

## What's next

* Read [Deploy a TiDB Cluster across Multiple Kubernetes Clusters](deploy-tidb-cluster-across-multiple-kubernetes.md) to learn how to manage a TiDB cluster across multiple Kubernetes clusters.
