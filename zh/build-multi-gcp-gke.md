---
title: 构建多个网络互通的 GCP GKE 集群
summary: 介绍如何构建多个 GCP GKE 集群互通网络，为跨 Kubernetes 集群部署 TiDB 集群作准备
---

# 构建多个网络互通的 GCP GKE 集群

本文介绍了如何构建多个 GCP GKE 集群，并配置集群之间的网络互通，为跨 Kubernetes 集群部署 TiDB 集群作准备。

如果仅需要部署一个 TiDB 集群到一个 GCP GKE 集群，请参考[在 GCP GKE 上部署 TiDB 集群](deploy-on-gcp-gke.md)文档。

## 环境准备

部署前，请确认已完成以下环境准备：

* [Helm 3](https://helm.sh/docs/intro/install/)：用于安装 TiDB Operator
* [gcloud](https://cloud.google.com/sdk/gcloud)：用于创建和管理 GCP 服务的命令行工具
* 完成 [GKE 快速入门](https://cloud.google.com/kubernetes-engine/docs/quickstart#before-you-begin) 中的**准备工作** (Before you begin)

## 配置 GCP 服务

{{< copyable "shell-regular" >}}

```bash
gcloud config set core/project <gcp-project>
```

使用以上命令，设置好你的 GCP 项目。

## 第 1 步：创建网络

1. 创建一个自定义子网的 VPC 网络。

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud compute networks create ${network_name} --subnet-mode=custom
    ```

2. 在新创建的 VPC 网络下创建三个属于不同 Region 的子网，子网的 CIDR 块相互不重叠。

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
    gcloud compute networks subnets create ${subnet_1} \
        --region=${region_1} \
        --network=${network_name} \
        --range=10.1.0.0/16 \
        --secondary-range pods=10.11.0.0/16,services=10.101.0.0/16
    ```

    {{< copyable "shell-regular" >}}

    ```bash
        gcloud compute networks subnets create ${subnet_1} \
        --region=${region_1} \
        --network=${network_name} \
        --range=10.2.0.0/16 \
        --secondary-range pods=10.12.0.0/16,services=10.102.0.0/16
    ```

    参数 `--range=10.0.0.0/16` 指定集群的子网的 CIRD 块，所有集群的子网的 CIDR 块**必须**不相互重叠。
  
    参数 `--secondary-range pods=10.11.0.0/16,services=10.101.0.0/16` 中的指定了 Kubernetes 的 Pod 与 Service 使用的 CIRD 块，我们将会在后面使用到。

## 第 2 步：启动 Kubernetes 集群

创建三个 GKE 集群，每个集群使用上述创建的子网。

1. 创建三个 GKE 集群，每个集群有一个默认的节点池：

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud beta container clusters create ${cluster_1} \
        --region ${region_1} --num-nodes 1 \
        --network ${network_name} --subnetwork ${subnet_1} \
        --cluster-dns clouddns --cluster-dns-scope vpc \
        --cluster-dns-domain ${cluster_domain_1}
        --enable-ip-alias \
        --cluster-secondary-range-name=pods --services-secondary-range-name=services
    ```

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud beta container clusters create ${cluster_2} \
        --region ${region_2} --num-nodes 1 \
        --network ${network_name} --subnetwork ${subnet_2} \
        --cluster-dns clouddns --cluster-dns-scope vpc \
        --cluster-dns-domain ${cluster_domain_2}
        --enable-ip-alias \
        --cluster-secondary-range-name=pods --services-secondary-range-name=services
    ```

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud beta container clusters create ${cluster_3} \
        --region ${region_2} --num-nodes 1 \
        --network ${network_name} --subnetwork ${subnet_3} \
        --cluster-dns clouddns --cluster-dns-scope vpc \
        --cluster-dns-domain ${cluster_domain_3}
        --enable-ip-alias \
        --cluster-secondary-range-name=pods --services-secondary-range-name=services
    ```

    上述命令中，`${cluster_domain_n}` 表示第 n 个集群的 cluster domain。在后续部署 TiDB 集群时，需要配置部署的 TidbCluster CR 中的 `spec.clusterDomain`。

    我们使用 VPC 范围的 [**Cloud DNS 服务**](https://cloud.google.com/kubernetes-engine/docs/how-to/cloud-dns)，使得集群可以解析其他集群的 Pod 和 Service 地址。

2. 为每个集群创建 PD、TiKV 和 TiDB 使用的独立的节点池。

    以集群 1 为例：

    {{< copyable "shell-regular" >}}

    ```bash
    gcloud container node-pools create pd --cluster ${cluster_1} --machine-type n1-standard-4 --num-nodes=1 \
        --node-labels=dedicated=pd --node-taints=dedicated=pd:NoSchedule
    gcloud container node-pools create tikv --cluster ${cluster_1}  --machine-type n1-highmem-8 --num-nodes=1 \
        --node-labels=dedicated=tikv --node-taints=dedicated=tikv:NoSchedule
    gcloud container node-pools create tidb --cluster ${cluster_1}  --machine-type n1-standard-8 --num-nodes=1 \
        --node-labels=dedicated=tidb --node-taints=dedicated=tidb:NoSchedule
    ```

3. 获取每个集群的 Kubenetes context，后续当我们需要使用 `kubectl` 命令操作特定的集群时，需要指定对应的 context。

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl config get-contexts
    ```

    输出类似如下，其中的 `NAME` 项就是我们后续需要使用的 context。

    ```
    CURRENT   NAME                          CLUSTER                       AUTHINFO                            NAMESPACE
    *         gke_pingcap_us-west1_tidb-1   gke_pingcap_us-west1_tidb-1   gke_pingcap_us-west1_tidb-1
              gke_pingcap_us-west2_tidb-2   gke_pingcap_us-west2_tidb-2   gke_pingcap_us-west2_tidb-2
              gke_pingcap_us-west3_tidb-3   gke_pingcap_us-west3_tidb-3   gke_pingcap_us-west3_tidb-3
    ```

    后文中，使用 `${context_1}`、`${context_2}` 与 `${context_3}` 分别代表各个集群的 context。

### 配置防火墙规则

1. 更新集群 1 的防火墙规则
   
   1. 找到用于 GKE Pod 间通信的防火墙规则的名字，防火墙规则命名规则类似于：`gke-${cluster_1}-${hash}-all`
        
        {{< copyable "shell-regular" >}}

        ```bash
        gcloud compute firewall-rules list --filter='name~gke-${cluster_1}-.*-all'
        ```

        输出类似如下，其 `NAME` 项为规则的名字。

        ```
        NAME                           NETWORK     DIRECTION  PRIORITY  ALLOW                         DENY  DISABLED
        gke-${cluster_1}-b8b48366-all  ${network}  INGRESS    1000      tcp,udp,icmp,esp,ah,sctp            False
        ```

   2. 更新该防火墙规则的 source range，加上另外两个集群的 Pod 网络的 CIDR 块。

        {{< copyable "shell-regular" >}}

        ```bash
        gcloud compute firewall-rules update ${firewall_rule_name} --source-ranges 10.10.0.0/16,10.11.0.0/16,10.12.0.0/16
        ```

        你可以通过以下命令检查防火墙规则是否成功更新。

        {{< copyable "shell-regular" >}}

        ```bash
        gcloud compute firewall-rules describe ${firewall_rule_name}
        ```

2. 按照步骤 1，更新集群 2 与集群 3 的防火墙规则。

## 验证网络连通性

在部署 TiDB 集群之前，我们需要先验证一下多个集群之间的网络连通性。

1. 将下面定义保存到 `sample-nginx.yaml` 文件。

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

2. 在三个集群对应的命名空间下部署 nginx 服务。
   
   {{< copyable "shell-regular" >}}

   ```bash
   kubectl --context ${context_2} -n default apply -f sample-nginx.yaml

   kubectl --context ${context_2} -n default apply -f sample-nginx.yaml

   kubectl --context ${context_3} -n default apply -f sample-nginx.yaml
   ```

3. 通过访问其他集群的 nginx 服务，来验证网络是否连通。
   
   以验证集群 1 到集群 2 的网络连通性为例，执行以下命令。

   {{< copyable "shell-regular" >}}

   ```bash
   kubectl --context ${context_1} exec sample-nginx -- curl http://sample-nginx.sample-nginx-peer.default.svc.${cluster_domain_2}:80
   ```

   如果输出为 nginx 的欢迎页面，那么就表明网络是正常连通的。

## 第 3 步：部署 TiDB Operator

每个集群的 TidbCluster 定义由当前集群的 TiDB Operator 管理，因此每个集群都需要部署 TiDB Operator。

每个集群的部署步骤参考文档[**在 Kubernetes 上部署 TiDB Operator**](deploy-tidb-operator.md)。区别在于，需要通过命令 `kubectl --context ${context}` 与 `helm --kube-context ${context}` 操作各个集群。

## 第 4 步：部署 TiDB 集群

参考[**跨多个 Kubernetes 集群部署 TiDB 集群**](deploy-tidb-cluster-across-multiple-kubernetes.md)为每个集群部署一个 TidbCluster 定义。需要注意的是：

* 在配置 TidbCluster 定义时使用的 `clusterDomain` 字段需要和 [启动 Kubernetes 集群](#启动-kubernetes-集群) 一节定义的一致。

例如，部署初始集群 TidbCluster 定义时，将 `spec.clusterDomain` 指定为 `${cluster_domain_1}`:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
# ...
spec:
  #..
  clusterDomain: "${cluster_domain_1}"
```

## 探索更多

* 阅读文档 [**跨多个 Kubernetes 集群部署 TiDB 集群**](deploy-tidb-cluster-across-multiple-kubernetes.md) 了解如何管理跨 Kubernetes 集群的 TiDB 集群。
