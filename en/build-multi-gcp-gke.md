---
title: Build Multiple Interconnected GCP GKE Clusters
summary: Learn how to build multiple interconnected GCP GKE clusters and prepare for deploying a TiDB cluster across multiple GKE clusters.
---

# Build Multiple Interconnected GCP GKE Clusters

This document describes how to create multiple GCP GKE clusters and configure network peering between these clusters. These interconnected clusters can be used for [deploying TiDB clusters across multiple Kubernetes clusters](deploy-tidb-cluster-across-multiple-kubernetes.md). The example in this document shows how to configure three-cluster network peering.

If you need to deploy TiDB on a single GCP GKE cluster, refer to [Deploy TiDB on GCP GKE](deploy-on-gcp-gke.md).

## Prerequisites

Before you deploy GKE clusters, make sure you have completed the following preparations:

* Install [Helm 3](https://helm.sh/docs/intro/install/). You need to use Helm to install TiDB Operator.
* Install [gcloud](https://cloud.google.com/sdk/gcloud): `gcloud` is the CLI for creating and managing GCP services
* Complete the *Before you begin* section in [GKE Quickstart](https://cloud.google.com/kubernetes-engine/docs/quickstart#before-you-begin).

## Configure GCP service

Configure your GCP project by running the following command:

{{< copyable "shell-regular" >}}

```bash
gcloud config set core/project <gcp-project>
```

## Step 1. Create a VPC network

1. Create a VPC network with custom subnets:

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud compute networks create ${network_name} --subnet-mode=custom
    ```

2. In the VPC network created above, create three subnets that belong to different regions. The CIDR block of each subnet does not overlap with that of each other.

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud compute networks subnets create ${subnet_1} \
        --region=${region_1} \
        --network=${network_name} \
        --range=10.0.0.0/16 \
        --secondary-range pods=10.10.0.0/16,services=10.100.0.0/16
    ```

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud compute networks subnets create ${subnet_2} \
        --region=${region_2} \
        --network=${network_name} \
        --range=10.1.0.0/16 \
        --secondary-range pods=10.11.0.0/16,services=10.101.0.0/16
    ```

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud compute networks subnets create ${subnet_3} \
        --region=${region_3} \
        --network=${network_name} \
        --range=10.2.0.0/16 \
        --secondary-range pods=10.12.0.0/16,services=10.102.0.0/16
    ```

    `${subnet_1}`, `${subnet_2}`, and `${subnet_3}` refer to the names of the three subnets.

    `--range=10.0.0.0/16` specifies the CIDR block of the `${subnet_1}` in the cluster. The CIDR blocks of all cluster subnets **must not** overlap with each other.

    `--secondary-range pods=10.11.0.0/16,services=10.101.0.0/16` specifies the CIRD block used by Kubernetes Pods and Services. This CIRD block will be used later.

## Step 2. Start the Kubernetes cluster

Create three GKE clusters, and each cluster uses one of the subnets created in Step 1.

1. Create three GKE clusters. Each cluster has a default node pool.

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud beta container clusters create ${cluster_1} \
        --region ${region_1} --num-nodes 1 \
        --network ${network_name} --subnetwork ${subnet_1} \
        --cluster-dns clouddns --cluster-dns-scope vpc \
        --cluster-dns-domain ${cluster_domain_1} \
        --enable-ip-alias \
        --cluster-secondary-range-name=pods --services-secondary-range-name=services
    ```

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud beta container clusters create ${cluster_2} \
        --region ${region_2} --num-nodes 1 \
        --network ${network_name} --subnetwork ${subnet_2} \
        --cluster-dns clouddns --cluster-dns-scope vpc \
        --cluster-dns-domain ${cluster_domain_2} \
        --enable-ip-alias \
        --cluster-secondary-range-name=pods --services-secondary-range-name=services
    ```

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud beta container clusters create ${cluster_3} \
        --region ${region_3} --num-nodes 1 \
        --network ${network_name} --subnetwork ${subnet_3} \
        --cluster-dns clouddns --cluster-dns-scope vpc \
        --cluster-dns-domain ${cluster_domain_3} \
        --enable-ip-alias \
        --cluster-secondary-range-name=pods --services-secondary-range-name=services
    ```

    In the commands above, `${cluster_domain_n}` refers to the domain name of the `n`th cluster. In the following deployment steps, you need to configure `spec.clusterDomain` in TidbCluster CR to `${cluster_domain_n}`.

    In the commands above, the [Cloud DNS](https://cloud.google.com/kubernetes-engine/docs/how-to/cloud-dns) in VPC scope is used so that the cluster can parse the Pod and Service addresses in other clusters.

2. Create the dedicated node pools used by PD, TiKV, and TiDB for each cluster.

    Take cluster 1 as an example:

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud container node-pools create pd --cluster ${cluster_1} --machine-type n1-standard-4 --num-nodes=1 \
        --node-labels=dedicated=pd --node-taints=dedicated=pd:NoSchedule
    gcloud container node-pools create tikv --cluster ${cluster_1}  --machine-type n1-highmem-8 --num-nodes=1 \
        --node-labels=dedicated=tikv --node-taints=dedicated=tikv:NoSchedule
    gcloud container node-pools create tidb --cluster ${cluster_1}  --machine-type n1-standard-8 --num-nodes=1 \
        --node-labels=dedicated=tidb --node-taints=dedicated=tidb:NoSchedule
    ```

3. Obtain the Kubernetes context of each cluster. The context will be used in the subsequent `kubectl` commands.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl config get-contexts
    ```

    The expected output is as follows. The context is in the `NAME` column.

    ```
    CURRENT   NAME                          CLUSTER                       AUTHINFO                            NAMESPACE
    *         gke_pingcap_us-west1_tidb-1   gke_pingcap_us-west1_tidb-1   gke_pingcap_us-west1_tidb-1
              gke_pingcap_us-west2_tidb-2   gke_pingcap_us-west2_tidb-2   gke_pingcap_us-west2_tidb-2
              gke_pingcap_us-west3_tidb-3   gke_pingcap_us-west3_tidb-3   gke_pingcap_us-west3_tidb-3
    ```

    In the following sections, `${context_1}`, `${context_2}`, and `${context_3}` refer to the context of each cluster.

### Configure the firewall rules

1. Update the firewall rules for cluster 1.

    1. Obtain the name of the firewall rule used for communication between GKE Pods. The name of the firewall rule is similar to `gke-${cluster_1}-${hash}-all`.

        {{< copyable "shell-regular" >}}

        ```bash
        gcloud compute firewall-rules list --filter='name~gke-${cluster_1}-.*-all'
        ```

        The expected output is as follows. The rule name is in the `NAME` column.

        ```
        NAME                           NETWORK     DIRECTION  PRIORITY  ALLOW                         DENY  DISABLED
        gke-${cluster_1}-b8b48366-all  ${network}  INGRESS    1000      tcp,udp,icmp,esp,ah,sctp            False
        ```

    2. Update the source range of the firewall rule. Add the CIDR blocks of the Pod network of the other two clusters to the source range:

        {{< copyable "shell-regular" >}}

        ```bash
        gcloud compute firewall-rules update ${firewall_rule_name} --source-ranges 10.10.0.0/16,10.11.0.0/16,10.12.0.0/16
        ```

        Run the following command to check whether the firewall rule is successfully updated:

        {{< copyable "shell-regular" >}}

        ```bash
        gcloud compute firewall-rules describe ${firewall_rule_name}
        ```

2. Follow the same steps to update the firewall rules for cluster 2 and cluster 3.

## Step 3. Verify the network interconnectivity

Before you deploy the TiDB cluster, you need to verify that the network between the GKE clusters is interconnected.

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

2. Deploy the nginx service in the namespaces of three clusters.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl --context ${context_1} -n default apply -f sample-nginx.yaml

    kubectl --context ${context_2} -n default apply -f sample-nginx.yaml

    kubectl --context ${context_3} -n default apply -f sample-nginx.yaml
    ```

3. Access the nginx services of each cluster to verify the network interconnectivity.

    The following command verifies the network from cluster 1 to cluster 2:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl --context ${context_1} exec sample-nginx -- curl http://sample-nginx.sample-nginx-peer.default.svc.${cluster_domain_2}:80
    ```

    If the output is the welcome page of nginx, the network is connected.

4. After the verification, delete the nginx services:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl --context ${context_1} -n default delete -f sample-nginx.yaml
    kubectl --context ${context_2} -n default delete -f sample-nginx.yaml
    kubectl --context ${context_3} -n default delete -f sample-nginx.yaml
    ```

## Step 4. Deploy TiDB Operator

The `TidbCluster` CR of each cluster is managed by TiDB Operator of the cluster. Therefore, you must deploy TiDB Operator for each cluster.

Refer to [Deploy TiDB Operator](deploy-tidb-operator.md) and deploy TiDB Operator in each GKE cluster. Note that you need to use `kubectl --context ${context}` and `helm --kube-context ${context}` in the commands to deploy TiDB Operator for each GKE cluster.

## Step 5. Deploy TiDB clusters

Refer to [Deploy a TiDB Cluster across Multiple Kubernetes Clusters](deploy-tidb-cluster-across-multiple-kubernetes.md), and deploy a `TidbCluster` CR for each GKE cluster.

In the `TidbCluster` CR, the `spec.clusterDomain` field must be the same as `${cluster_domain_n}` defined in [Step 2](#step-2-start-the-kubernetes-cluster).

For example, when you deploy the `TidbCluster` CR to cluster 1, specify `spec.clusterDomain` as `${cluster_domain_1}`:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
# ...
spec:
  #..
  clusterDomain: "${cluster_domain_1}"
  acrossK8s: true
```

## What's next

* Read [Deploy a TiDB Cluster across Multiple Kubernetes Clusters](deploy-tidb-cluster-across-multiple-kubernetes.md) to learn how to manage a TiDB cluster across multiple Kubernetes clusters.
