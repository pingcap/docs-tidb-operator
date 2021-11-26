---
title: 构建多个 AWS EKS 集群互通网络
summary: 介绍如何构建多个 AWS EKS 集群互通网络，为跨 Kubernetes 集群部署 TiDB 集群作准备
---

# 构建多个 AWS EKS 集群互通网络

本文介绍了如何构建多个 AWS EKS 集群互通网络，为跨 Kubernetes 集群部署 TiDB 集群作准备。

如果仅需要部署一个 TiDB 集群到一个 AWS EKS 集群，请参考[部署到 AWS EKS](deploy-on-aws-eks.md)文档。

## 环境准备

部署前，请确认已完成以下环境准备：

- 安装 [Helm 3](https://helm.sh/docs/intro/install/)：用于安装 TiDB Operator。

- 完成 AWS [eksctl 入门](https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/getting-started-eksctl.html)中所有操作。

    该教程包含以下内容：

    - 安装并配置 AWS 的命令行工具 awscli
    - 安装并配置创建 Kubernetes 集群的命令行工具 eksctl
    - 安装 Kubernetes 命令行工具 kubectl

要验证 AWS CLI 的配置是否正确，请运行 `aws configure list` 命令。如果此命令的输出显示了 `access_key` 和 `secret_key` 的值，则 AWS CLI 的配置是正确的。否则，你需要重新配置 AWS CLI。

> **注意：**
>
> 本文档的操作需要 AWS Access Key 至少具有 [eksctl 所需最少权限](https://eksctl.io/usage/minimum-iam-policies/)和创建 [Linux 堡垒机所涉及的服务权限](https://docs.aws.amazon.com/quickstart/latest/linux-bastion/architecture.html#aws-services)。

## 启动 Kubernetes 集群

1. 使用 `eksctl` 工具创建三个 EKS 集群，每个集群所在的 VPC 的 CIDR 块不与其他集群重叠。

    以三个 region 部署三个集群为例，每个集群部署三个节点：

    {{< copyable "shell-regular" >}}
    
    ```shell
    eksctl create cluster --name ${cluster_1} --with-oidc --managed --region ${region_1} --nodes 3 --vpc-cidr ${cidr_block_1}
    ```

    {{< copyable "shell-regular" >}}
    
    ```shell
    eksctl create cluster --name ${cluster_2} --with-oidc --managed --region ${region_2} --nodes 3 --vpc-cidr ${cidr_block_2}
    ```

    {{< copyable "shell-regular" >}}
    
    ```shell
    eksctl create cluster --name ${cluster_3} --with-oidc --managed --region ${region_3} --nodes 3 --vpc-cidr ${cidr_block_3}
    ```

    可以参考[部署到 AWS EKS](deploy-on-aws-eks.md)文档来配置每个 EKS 集群。

    > **警告：**
    >
    > 因为 CIDR 块不能在创建集群后修改，因此必须确保所有集群所在的 VPC 的 CIRD 块**必须**不重叠。

    本文后续中，使用 `${cluster_1}`、`${cluster_2}` 与 `${cluster_3}` 分别代表各个集群的名字。

2. 进入 [AWS EKS 控制台](https://us-west-2.console.aws.amazon.com/eks/)，观察各个集群的状态，等待所有集群创建完毕并为 Active 状态。

3. 获取每个集群的 Kubenetes context，后续当我们需要使用 `kubectl` 命令操作特定的集群时，需要指定对应的 context。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl config get-contexts
    ```

    输出类似如下，其中的 `NAME` 项就是我们后续需要使用的 context。

    ```
    CURRENT   NAME                                 CLUSTER                      AUTHINFO                            NAMESPACE
    *         pingcap@tidb-1.us-west-1.eksctl.io   tidb-1.us-west-1.eksctl.io   pingcap@tidb-1.us-west-1.eksctl.io
              pingcap@tidb-2.us-west-2.eksctl.io   tidb-2.us-west-2.eksctl.io   pingcap@tidb-2.us-west-2.eksctl.io
    ```

    后文中，使用 `${context_1}`、`${context_2}` 与 `${context_3}` 分别代表各个集群的 context。

## 配置网络

### 设置 VPC peering

为了联通三个集群的网络，我们需要为每两个集群所在 VPC 创建一个 VPC peering。关于 VPC peering 可以参考 [AWS 官方文档](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html)。

1. 通过 `eksctl` 命令得到每个集群所在的 VPC 的 ID。以集群 1 为例：
   
    {{< copyable "shell-regular" >}}
    
    ```shell
    eksctl get cluster ${cluster_1}
    ```

    输出类似如下，其中 `VPC` 项就是该集群所在 VPC 的 ID。

    ```
    NAME          VERSION STATUS  CREATED                 VPC                      SUBNETS                                                                                                                  SECURITYGROUPS
    ${cluster_1}  1.20    ACTIVE  2021-11-22T06:40:20Z    vpc-0b15ed35c02af5288   subnet-058777d55881c4095,subnet-06def2041b6fa3fa0,subnet-0869c7e73e09c3174,subnet-099d10845f6cbaf82,subnet-0a1a58db5cb087fed,subnet-0f68b302678c4d36b     sg-0cb299e7ec153c595
    ```

    后文中，我们以 `${vpc_id_1}`、`${vpc_id_2}` 与 `${vpc_id_3}` 分别代表各个集群所在的 VPC 的 ID。

2. 构建集群 1 与集群 2 的 VPC peering。

   1. 按照 [AWS VPC peering 文档](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#create-vpc-peering-connection-local)  创建 VPC peering。`${vpc_id_1}` 作为 requester VPC，`${vpc_id_2}` 作为 accepter VPC

   2. 按照 [AWS VPC Peering 文档](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#accept-vpc-peering-connection) 完成 VPC peering 的构建。

3. 以步骤 2 为例，构建集群 1 与集群 3，以及集群 2 与集群 3 的 VPC peering。

4. 按照[更新路由表文档](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-routing.html)，更新每个集群的路由表。
   
   每个集群需要添加两个路由项，每个路由项的 **Destination** 为另一个集群的 CIDR block，**Target** 为这两个集群的的 VPC peering ID。

### 更新实例的安全组

1. 更新集群 1 的安全组
   
   1. 进入 [**AWS Security Groups 控制台**](https://us-west-2.console.aws.amazon.com/ec2/v2/home#SecurityGroups)，找到集群 1 的安全组，其安全组命名类似于 `eks-cluster-sg-${cluster_1}-${id}`.

   2. 添加 Inbound rules 到安全组，以允许来自集群 2 和集群 3 的流量：

      | Type        | Protocol | Port range | Source                 | Descrption                                    |
      | ----------- | -------- | ---------- | ---------------------- | --------------------------------------------- |
      | All traffic | All      | All        | Custom ${cidr_block_2} | Allow cluster 2 to communicate with cluster 1 |
      | All traffic | All      | All        | Custom ${cidr_block_3} | Allow cluster 3 to communicate with cluster 1 |

2. 按照步骤 1 更新集群 2 与集群 3 的安全组。

### 配置负载均衡器

每个集群的 CoreDNS 服务需要通过一个 [**Network Load Balancer**](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html) 暴露给其他集群。

1. 创建 Load Balancer Service 定义文件 `dns-lb.yaml`，其文件内容如下：
   
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
   labels:
      k8s-app: kube-dns
   name: across-cluster-dns
   namespace: kube-system
   annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
   spec:
   ports:
   - name: dns
      port: 53
      protocol: TCP
      targetPort: 53
   selector:
      k8s-app: kube-dns
   type: LoadBalancer
   loadBalancerSourceRanges: ["0.0.0.0/0"]
   ```

2. 在每个集群中部署 Load Balancer Service。

   {{< copyable "shell-regular" >}}

   ```shell
   kubectl --context ${context_1} apply -f dns-lb.yaml

   kubectl --context ${context_2} apply -f dns-lb.yaml

   kubectl --context ${context_3} apply -f dns-lb.yaml
   ```

3. 进入 [AWS Load Balancers 控制台](https://us-west-2.console.aws.amazon.com/ec2/v2/home?#LoadBalancers)，等待所有集群的 Load Balancer 变为 `Active` 状态。
   
   你可以通过 `kubectl get svc -n kube-system across-cluster-dns` 得到该集群的 Load Balancer 的 DNS Name，然后通过 DNS Name 在控制台查询 Load Balancer 的状态。

4. 对每个集群的 Load Balancer 的 DNS Name，使用 `dig` 命令解析出对应的 IP 地址。

   {{< copyable "shell-regular" >}}
  
   ```shell
   dig <nlb-dns-name>
   ```

   对于每个 Load Balancer，你可能会得到多个 IP 地址，你需要将其记录下来，在下一步配置 CoreDNS 时会使用。

   ```
   ...

   ;; ANSWER SECTION:
   a1187e0239d364bf09e309b1a8bb275a-d8437eef39484dbd.elb.us-west-2.amazonaws.com. 60 IN A ${ip1}
   a1187e0239d364bf09e309b1a8bb275a-d8437eef39484dbd.elb.us-west-2.amazonaws.com. 60 IN A ${ip2}
   a1187e0239d364bf09e309b1a8bb275a-d8437eef39484dbd.elb.us-west-2.amazonaws.com. 60 IN A ${ip3}

   ...
   ```

   后文中，我们将使用 `${ipm-n}` 的格式来表示第 n 个集群的 LoadBalancer 第 m 个 IP 地址。

### 配置 CoreDNS

为了能够让集群中的 Pod 访问其他集群的 Service，我们需要配置每个集群的 CoreDNS 服务以能够转发 DNS 请求给其他集群的 CoreDNS 服务。

我们通过修改 CoreDNS 对应的 ConfigMap 来进行配置，更多配置项可以参考文档 [Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#coredns)。

1. 修改集群 1 的 CoreDNS 配置

   1. 备份当前的 CoreDNS 配置

      {{< copyable "shell-regular" >}}

      ```shell
      kubectl --context ${context_1} -n kube-system get configmap coredns -o yaml > ${context_1}-coredns.yaml.bk
      ```

   2. 修改 ConfigMap

      {{< copyable "shell-regular" >}}

      ```shell
      kubectl --context ${context_1} -n kube-system edit configmap coredns
      ```

      修改 `data.Corefile` 字段如下，其中 `${namspeace_2}` 和 `${namspeace_3}` 分别为集群 2 和集群 3 将要部署的 TidbCluster 所在的 namespace。

      ```yaml
      apiVersion: v1
      kind: ConfigMap
      # ...
      data:
      Corefile: |
         .:53 {
            # ... 默认配置不修改
         }
         ${namspeace_2}.svc.cluster.local:53 {
             errors
             cache 30
             forward . ${ip1-2} ${ip2-2} ${ip3-2} {
                 force_tcp
             }
         }  
         ${namspeace_3}.svc.cluster.local:53 {
             errors
             cache 30
             forward . ${ip1-3} ${ip2-3} ${ip3-3} {
                 force_tcp
             }
         }
      ```

2. 以步骤 1 为例，修改集群 2 和集群 3 的 CoreDNS 配置。

   对于每个集群，你需要将 `${namspeace_2}` 与 `${namspeace_3}` 修改为另外两个集群将要运行 Pod 的 namespace，将配置中的 IP 地址配置为另外两个集群的 Load Balancer 的 IP 地址。

后文中，使用 `${namspeace_1}`、`${namspeace_2}` 与 `${namspeace_3}` 分别代表各个集群的将要部署的 TidbCluster 所在的 namespace。

## 部署 TiDB Operator

每个集群的 TidbCluster 定义由当前集群的 TiDB Operator 管理，因此每个集群都需要部署 TiDB Operator。

每个集群的部署步骤参考快速上手中[**部署 TiDB Operator**](get-started.md#部署-tidb-operator)。区别在于，需要通过命令 `kubectl --context ${context}` 与 `helm --kube-context ${context}` 操作各个集群。

## 部署 TiDB 集群

参考[**跨多个 Kubernetes 集群部署 TiDB 集群**](deploy-tidb-cluster-across-multiple-kubernetes.md)为每个集群部署一个 TidbCluster 定义，并且**必须**将各集群的 TidbCluster 部署到 [配置 CoreDNS](#配置-coredns) 一步中对应的 namespace 下，否则 TiDB 集群运行将会失败。

例如，部署初始集群的 TidbCluster 定义时，将 `metadata.namespace` 指定为 `${namspeace_1}`:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
   name: ${tc_name}
   namespace: ${namspeace_1}
spec:
  #..
  clusterDomain: "${cluster_domain_1}"
```