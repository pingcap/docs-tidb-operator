---
title: 构建多个 AWS EKS 集群
summary: 介绍如何构建多个 AWS EKS 集群互通网络，为跨 Kubernetes 集群部署 TiDB 集群作准备
---

# 构建多个 AWS EKS 集群互通网络

本文介绍了如何构建多个 AWS EKS 集群互通网络，为跨 Kubernetes 集群部署 TiDB 集群作准备。

如果仅需要部署一个 TiDB 集群到一个 AWS EKS 集群，请参考[在 AWS EKS 上部署 TiDB 集群](deploy-on-aws-eks.md)文档。

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

定义三个 EKS 集群的配置文件分别为 `cluster-1.yaml`、`cluster-2.yaml` 和 `cluster-3.yaml`，并使用 `eksctl` 命令创建三个 EKS 集群。

1. 定义集群 1 的配置文件，并创建集群 1 。
   
   将如下配置保存为 `cluster-1.yaml` 文件，其中 `${cluster_1}` 为 EKS 集群的名字，`${region_1}` 为部署 EKS 集群到的 Region，`${cidr_block_1}` 为 EKS 集群所属的 VPC 的 CIDR block。
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

   节点池 `nodeGroups` 字段的配置可以参考 [创建 EKS 集群和节点池](deploy-on-aws-eks#创建-eks-集群和节点池) 一节。

   执行以下命令创建集群 1 ：

   {{< copyable "shell-regular" >}}

   ```shell
   eksctl create cluster -f cluster-1.yaml
   ```

   该命令需要等待 EKS 集群创建完成，以及节点组创建完成并加入进去，耗时约 5~20 分钟。可参考 [eksctl 文档](https://eksctl.io/usage/creating-and-managing-clusters/#using-config-files)了解更多集群配置选项。

2. 以集群 1 的配置文件为例，定义集群 2 与集群 3 的配置文件，并通过 `eksctl` 命令创建集群 2 与集群 3 。
   
   需要注意，每个集群所属的 VPC 的 CIDR block **必须** 与其他集群不重叠。

后文中，我们使用 `${cluster_1}`、`${cluster_2}` 与 `${cluster_3}` 分别代表三个集群的名字，使用 `${region_1}`、`${region_2}` 与 `${region_1}` 分别代表三个集群所处的 Region，使用 `${cidr_block_1}`、`${cidr_block_2}` 与 `${cidr_block_3}` 分别代表三个集群所属的 VPC 的 CIDR block。

在所有集群创建完毕后，我们需要获取每个集群的 Kubernetes Context，以方便后续我们使用 `kubectl` 命令操作每个集群。

{{< copyable "shell-regular" >}}

```shell
kubectl config get-contexts
```

<details>
<summary>点击查看输出，其中的 `NAME` 项就是我们需要使用的 context 。</summary>
<pre><code>
CURRENT   NAME                                 CLUSTER                      AUTHINFO                            NAMESPACE
*         pingcap@tidb-1.us-west-1.eksctl.io   tidb-1.us-west-1.eksctl.io   pingcap@tidb-1.us-west-1.eksctl.io
         pingcap@tidb-2.us-west-2.eksctl.io   tidb-2.us-west-2.eksctl.io   pingcap@tidb-2.us-west-2.eksctl.io
         pingcap@tidb-3.us-east-1.eksctl.io   tidb-2.us-east-1.eksctl.io   pingcap@tidb-3.us-east-1.eksctl.io
</code></pre>
</details>

后文中，我们使用 `${context_1}`、`${context_2}` 与 `${context_3}` 分别代表各个集群的 context。

## 配置网络

### 设置 VPC peering

为了联通三个集群的网络，我们需要为每两个集群所在 VPC 创建一个 VPC peering。关于 VPC peering 可以参考 [AWS 官方文档](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html)。

1. 通过 `eksctl` 命令得到每个集群所在的 VPC 的 ID。以集群 1 为例：
   
    {{< copyable "shell-regular" >}}
    
    ```shell
    eksctl get cluster ${cluster_1} --region ${region_1}
    ```

   <details>
   <summary>点击查看示例输出，其中 `VPC` 项就是该集群所在 VPC 的 ID。</summary>
   <pre><code>
   CURRENT   NAME                                 CLUSTER                      AUTHINFO                            NAMESPACE
   *         pingcap@tidb-1.us-west-1.eksctl.io   tidb-1.us-west-1.eksctl.io   pingcap@tidb-1.us-west-1.eksctl.io
            pingcap@tidb-2.us-west-2.eksctl.io   tidb-2.us-west-2.eksctl.io   pingcap@tidb-2.us-west-2.eksctl.io
            pingcap@tidb-3.us-east-1.eksctl.io   tidb-2.us-east-1.eksctl.io   pingcap@tidb-3.us-east-1.eksctl.io
   </code></pre>
   </details>

   后文中，我们使用 `${vpc_id_1}`、`${vpc_id_2}` 与 `${vpc_id_3}` 分别代表各个集群所在的 VPC 的 ID。

2. 构建集群 1 与集群 2 的 VPC peering。

   1. 按照 [AWS VPC peering 文档](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#create-vpc-peering-connection-local)  创建 VPC peering。`${vpc_id_1}` 作为 requester VPC，`${vpc_id_2}` 作为 accepter VPC 。

   2. 按照 [AWS VPC Peering 文档](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#accept-vpc-peering-connection) 完成 VPC peering 的构建。

3. 以步骤 2 为例，构建集群 1 与集群 3，以及集群 2 与集群 3 的 VPC peering。

4. 按照[更新路由表文档](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-routing.html)，更新三个集群的路由表。

   你需要更新集群使用的所有 Subnet 的路由表。每个路由表需要添加两个路由项，以集群 1 为例：
   
   | Destination     | Target           | Status | Propagated |
   | --------------- | ---------------- | ------ | ---------- |
   | ${cidr_block_2} | ${vpc_peering_1} | Active | No         |
   | ${cidr_block_3} | ${vpc_peering_2} | Active | No         |

   每个路由项的 **Destination** 为另一个集群的 CIDR block，**Target** 为这两个集群的 VPC peering ID。

### 更新实例的安全组

1. 更新集群 1 的安全组
   
   1. 进入 [**AWS Security Groups 控制台**](https://us-west-2.console.aws.amazon.com/ec2/v2/home#SecurityGroups)，找到集群 1 的安全组，其安全组命名类似于 `eksctl-${cluster_1}-cluster/ClusterSharedNodeSecurityGroup`.

   2. 添加 Inbound rules 到安全组，以允许来自集群 2 和集群 3 的流量：

      | Type        | Protocol | Port range | Source                 | Descrption                                    |
      | ----------- | -------- | ---------- | ---------------------- | --------------------------------------------- |
      | All traffic | All      | All        | Custom ${cidr_block_2} | Allow cluster 2 to communicate with cluster 1 |
      | All traffic | All      | All        | Custom ${cidr_block_3} | Allow cluster 3 to communicate with cluster 1 |

2. 按照步骤 1 更新集群 2 与集群 3 的安全组。

到这里，我们已经打通了三个集群之间的网络，可以尝试在各个集群中部署 Pod 并相互 ping 来验证网络是否成功互通。

### 配置负载均衡器

每个集群的 CoreDNS 服务需要通过一个 [**Network Load Balancer**](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html) 暴露给其他集群。

1. 创建 Load Balancer Service 定义文件 `dns-lb.yaml`，其文件内容如下：
   
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

2. 在每个集群中部署 Load Balancer Service。

   {{< copyable "shell-regular" >}}

   ```shell
   kubectl --context ${context_1} apply -f dns-lb.yaml

   kubectl --context ${context_2} apply -f dns-lb.yaml

   kubectl --context ${context_3} apply -f dns-lb.yaml
   ```

3. 获取各集群的 Load Balancer 的名字，并等待所有集群的 Load Balancer 变为 `Active` 状态。

   以集群 1 为例，我们可以使用以下命令来查询我们部署的 Load Balancer 的名字。

   {{< copyable "shell-regular" >}}
   
   ```bash
   lb_name_1=$(kubectl --context ${context_1} -n kube-system get svc across-cluster-dns-tcp -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" | cut -d - -f 1)

   lb_name_2=$(kubectl --context ${context_2} -n kube-system get svc across-cluster-dns-tcp -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" | cut -d - -f 1)

   lb_name_3=$(kubectl --context ${context_3} -n kube-system get svc across-cluster-dns-tcp -o jsonpath="{.status.loadBalancer.ingress[0].hostname}" | cut -d - -f 1)
   ```

   执行以下命名来查看三个集群的 Load Balancer 的状态，所有的命令输出结果都为 "active" 时，表明 Load Balancer 为 `Active` 状态。

   {{< copyable "shell-regular" >}}

   ```bash
   aws elbv2 describe-load-balancers --names ${lb_name_1} --region ${region_1} --query 'LoadBalancers[*].State' --output text

   aws elbv2 describe-load-balancers --names ${lb_name_2} --region ${region_2} --query 'LoadBalancers[*].State' --output text

   aws elbv2 describe-load-balancers --names ${lb_name_3} --region ${region_3} --query 'LoadBalancers[*].State' --output text
   ```

   <details>
   <summary>点击查看期望输出</summary>
   <pre><code>active
   active
   active</code></pre>
   </details>

4. 查询各集群的 Load Balancer 关联的 IP 地址。

   以集群 1 为例，执行下面命令查询集群 1 的 Load Balancer 关联的所有 IP 地址。

   ```bash
   aws ec2 describe-network-interfaces --region ${region_1} --filters Name=description,Values="ELB net/${lb_name_1}*" --query 'NetworkInterfaces[*].PrivateIpAddress' --output text
   ```

   <details>
   <summary>点击查看期望输出</summary>
   <pre><code>10.1.175.233 10.1.144.196</code></pre>
   </details>

   后文中，我们将各集群的 Load Balancer 关联 IP 地址称为 `${lb_ip_list_1}`、`${lb_ip_list_2}` 与 `${lb_ip_list_3}`。
   
   不同 Region 的 Load Balancer 可能有着不同数量的 IP 地址。例如上述示例中，`${lb_ip_list_1}` 就是 `10.1.175.233 10.1.144.196` 。

### 配置 CoreDNS

为了能够让集群中的 Pod 访问其他集群的 Service，我们需要配置每个集群的 CoreDNS 服务以能够转发 DNS 请求给其他集群的 CoreDNS 服务。

我们通过修改 CoreDNS 对应的 ConfigMap 来进行配置，更多配置项可以参考文档 [Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#coredns)。

1. 修改集群 1 的 CoreDNS 配置

   1. 备份当前的 CoreDNS 配置

      {{< copyable "shell-regular" >}}

      ```shell
      kubectl --context ${context_1} -n kube-system get configmap coredns -o yaml > ${cluster_1}-coredns.yaml.bk
      ```

   2. 修改 ConfigMap

      {{< copyable "shell-regular" >}}

      ```shell
      kubectl --context ${context_1} -n kube-system edit configmap coredns
      ```

      修改 `data.Corefile` 字段如下，其中 `${namspeace_2}` 和 `${namspeace_3}` 分别为集群 2 和集群 3 将要部署的 TidbCluster 所在的 namespace。

      > **警告：**
      >
      > 因为 EKS 集群无法修改集群的 cluster domain，因此我们需要使用 namespace 作为 DNS 请求转发的识别条件，所以 `${namspeace_1}`、`${namspeace_2}` 和 `${namspeace_3}` **必须** 不一样。

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
             forward . ${lb_ip_list_2} {
                 force_tcp
             }
         }  
         ${namspeace_3}.svc.cluster.local:53 {
             errors
             cache 30
             forward . ${lb_ip_list_3} {
                 force_tcp
             }
         }
      ```
   
   3. 等待 CoreDNS 重新加载配置，大约需要 30s 左右。

2. 以步骤 1 为例，修改集群 2 和集群 3 的 CoreDNS 配置。

   对于每个集群，你需要将 `${namspeace_2}` 与 `${namspeace_3}` 修改为另外两个集群将要运行 Pod 的 namespace，将配置中的 IP 地址配置为另外两个集群的 Load Balancer 的 IP 地址。

后文中，使用 `${namspeace_1}`、`${namspeace_2}` 与 `${namspeace_3}` 分别代表各个集群的将要部署的 TidbCluster 所在的 namespace。

## 部署 TiDB Operator

每个集群的 TidbCluster 定义由当前集群的 TiDB Operator 管理，因此每个集群都需要部署 TiDB Operator。

每个集群的部署步骤参考文档[**在 Kubernetes 上部署 TiDB Operator**](deploy-tidb-operator.md)。区别在于，我们需要通过命令 `kubectl --context ${context}` 与 `helm --kube-context ${context}` 来为每个 EKS 集群部署 TiDB Operator。

## 部署 TiDB 集群

参考[**跨多个 Kubernetes 集群部署 TiDB 集群**](deploy-tidb-cluster-across-multiple-kubernetes.md)为每个集群部署一个 TidbCluster 定义，需要注意的是：
* **必须**将各集群的 TidbCluster 部署到 [配置 CoreDNS](#配置-coredns) 一节中对应的 namespace 下，否则 TiDB 集群运行将会失败。
* 各集群的 cluster domain **必须** 设置为 "cluster.local"。

例如，部署初始集群的 TidbCluster 定义到集群 1 时，将 `metadata.namespace` 指定为 `${namespace_1}`:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
   name: ${tc_name}
   namespace: ${namespace_1}
spec:
  # ...
  clusterDomain: "cluster.local"
```

