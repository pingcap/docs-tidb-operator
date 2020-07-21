---
title: 在 AWS EKS 上部署 TiDB
summary: 介绍如何在 AWS EKS (Elastic Kubernetes Service) 上部署 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/deploy-on-aws-eks/']
---

# 在 AWS EKS 上部署 TiDB 集群

本文介绍了如何在 AWS EKS (Elastic Kubernetes Service) 上部署 TiDB 集群。

## 环境配置准备

部署前，请确认已安装以下软件：

* [helm](https://helm.sh/docs/intro/install/) is required to install TiDB Operator (the latest helm 3 is recommended)

并完成 AWS [eksctl 入门](https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/getting-started-eksctl.html) 中所有操作。

该教程会指导安装并配置好 AWS 的命令行工具 awscli 以及用来创建 Kubernetes 集群的 eksctl 工具。同时 Kubernetes 命令行 kubectl 也会下载并安装好。

> **注意：**
>
> 本文档操作，需要 AWS Access Key 至少具有 [eksctl 所需最少权限](https://eksctl.io/usage/minimum-iam-policies/) 和创建 [Linux 堡垒机所涉及的服务权限](https://docs.aws.amazon.com/quickstart/latest/linux-bastion/architecture.html#aws-services)。

## 部署

### 创建 EKS 和节点池

{{< copyable "shell-regular" >}}

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: <clusterName>
  region: us-west-2

nodeGroups:
  - name: admin
    desiredCapacity: 1
    labels:
      role: admin

  - name: tidb
    desiredCapacity: 1
    labels:
      role: tidb
    taints:
      dedicated: tidb:NoSchedule

  - name: pd
    desiredCapacity: 1
    labels:
      role: pd
    taints:
      dedicated: pd:NoSchedule

  - name: tikv
    desiredCapacity: 3
    labels:
      role: tikv
    taints:
      dedicated: tikv:NoSchedule
```

将以上配置存为 cluster.yaml 文件，并替换 `<clusterName>` 为自己想命名的集群名字后，执行以下命令创建集群：

{{< copyable "shell-regular" >}}

```shell
eksctl create cluster -f cluster.yaml 
```

可参考 [eksctl 文档](https://eksctl.io/usage/creating-and-managing-clusters/#using-config-files) 了解更多集群配置选项。

### 部署 TiDB Operator

参考快速上手中[部署 TiDB Operator](#部署-tidb-operator)，将 TiDB Operator 部署进 Kubernetes 集群。

### 部署 TiDB 集群和监控

1. 准备 TidbCluster 和 TidbMonitor CR 文件：

    {{< copyable "shell-regular" >}}

    ```shell
    curl -LO https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/aws/tidb-cluster.yaml &&
    curl -LO https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/aws/tidb-monitor.yaml
    ```

2. 创建 `Namespace`：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create namespace tidb-cluster
    ```

    > **注意：**
    >
    > `namespace` 是[命名空间](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)。本文档使用 `tidb-cluster` 为例，若使用了其他名字，修改相应的 `-n` 或 `--namespace` 参数为对应的名字即可。

3. 部署 TiDB 集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create -f tidb-cluster.yaml -n tidb-cluster &&
    kubectl create -f tidb-monitor.yaml -n tidb-cluster
    ```

4. 查看 TiDB 集群启动状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pods -n tidb-cluster
    ```
   
    当所有 pods 都处于 Running & Ready 状态时，则可以认为 TiDB 集群已经成功启动。一个正常运行的 TiDB 集群的案例：
    
    ```
    NAME                              READY   STATUS    RESTARTS   AGE
    tidb-discovery-5cb8474d89-n8cxk   1/1     Running   0          47h
    tidb-monitor-6fbcc68669-dsjlc     3/3     Running   0          47h
    tidb-pd-0                         1/1     Running   0          47h
    tidb-pd-1                         1/1     Running   0          46h
    tidb-tidb-0                       2/2     Running   0          47h
    tidb-tidb-1                       2/2     Running   0          46h
    tidb-tikv-0                       1/1     Running   0          47h
    tidb-tikv-1                       1/1     Running   0          47h
    tidb-tikv-2                       1/1     Running   0          47h
    tidb-tikv-3                       1/1     Running   0          46h
    ```

### 为 TiDB 服务 LoadBalancer 开启 Cross-Zone Load Balancing

由于 AWS Network Load Balancer (NLB) [问题](https://github.com/kubernetes/kubernetes/issues/82595)，为 TiDB 服务创建的 NLB 无法自动开启 Cross-Zone Load Balancing，请参考以下步骤手动开启：

1. 获取 TiDB 服务 NLB 名字：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get svc basic-tidb -n tidb-cluster
    ```

    示例：

    ```
    NAME        TYPE           CLUSTER-IP      EXTERNAL-IP                                                                     PORT(S)                          AGE
    tidb-tidb   LoadBalancer   172.20.39.180   a7aa544c49f914930b3b0532022e7d3c-83c0c97d8b659075.elb.us-west-2.amazonaws.com   4000:32387/TCP,10080:31486/TCP   3m46s
    ```

    `EXTERNAL-IP` 字段值中以 `-` 分隔的第一个字段即为 NLB 名字，上述示例中 `a7aa544c49f914930b3b0532022e7d3c` 即为 NLB 名字。

2. 获取 NLB LoadBalancerArn：

    {{< copyable "shell-regular" >}}

    ```shell
    aws elbv2 describe-load-balancers --name ${LoadBalancerName} --query 'LoadBalancers[*].LoadBalancerArn' --output text
    ```

    示例：

    ```
    $ aws elbv2 describe-load-balancers --name abfc623004ccb4cc3b363f3f37475af1 --query 'LoadBalancers[*].LoadBalancerArn' --output text
    arn:aws:elasticloadbalancing:us-west-2:385595570414:loadbalancer/net/abfc623004ccb4cc3b363f3f37475af1/9774d22c27310bc1
    ```

3. 查看 NLB 属性：

    {{< copyable "shell-regular" >}}

    ```shell
    aws elbv2 describe-load-balancer-attributes --load-balancer-arn ${LoadBalancerArn}
    ```

    `${LoadBalancerArn}` 为第二步获取的 NLB LoadBalancerArn。

    示例：

    ```
    $ aws elbv2 describe-load-balancer-attributes --load-balancer-arn "arn:aws:elasticloadbalancing:us-west-2:385595570414:loadbalancer/net/abfc623004ccb4cc3b363f3f37475af1/9774d22c27310bc1" --output yaml
    Attributes:
    - Key: access_logs.s3.enabled
      Value: 'false'
    - Key: load_balancing.cross_zone.enabled
      Value: 'false'
    - Key: access_logs.s3.prefix
      Value: ''
    - Key: deletion_protection.enabled
      Value: 'false'
    - Key: access_logs.s3.bucket
      Value: ''
    ```

    如果 `load_balancing.cross_zone.enabled` 的值为 `false`，继续下一步，为 NLB 开启 Cross-Zone Load Balancing。

4. 为 NLB 开启 Cross-Zone Load Balancing：

    {{< copyable "shell-regular" >}}

    ```shell
    aws elbv2 modify-load-balancer-attributes --load-balancer-arn ${LoadBalancerArn} --attributes Key=load_balancing.cross_zone.enabled,Value=true
    ```

    `${LoadBalancerArn}` 为第二步获取的 NLB LoadBalancerArn。

    示例：

    ```
    $ aws elbv2 modify-load-balancer-attributes --load-balancer-arn "arn:aws:elasticloadbalancing:us-west-2:385595570414:loadbalancer/net/abfc623004ccb4cc3b363f3f37475af1/9774d22c27310bc1" --attributes Key=load_balancing.cross_zone.enabled,Value=true --output yaml
    Attributes:
    - Key: access_logs.s3.enabled
      Value: 'false'
    - Key: load_balancing.cross_zone.enabled
      Value: 'true'
    - Key: access_logs.s3.prefix
      Value: ''
    - Key: deletion_protection.enabled
      Value: 'false'
    - Key: access_logs.s3.bucket
      Value: ''
    ```

5. 确认 NLB Cross-Zone Load Balancing 属性已经开启：

    {{< copyable "shell-regular" >}}

    ```shell
    aws elbv2 describe-load-balancer-attributes --load-balancer-arn ${LoadBalancerArn}
    ```

    `${LoadBalancerArn}` 为第二步获取的 NLB LoadBalancerArn。

    示例：

    ```
    $ aws elbv2 describe-load-balancer-attributes --load-balancer-arn "arn:aws:elasticloadbalancing:us-west-2:385595570414:loadbalancer/net/abfc623004ccb4cc3b363f3f37475af1/9774d22c27310bc1" --output yaml
    Attributes:
    - Key: access_logs.s3.enabled
      Value: 'false'
    - Key: load_balancing.cross_zone.enabled
      Value: 'true'
    - Key: access_logs.s3.prefix
      Value: ''
    - Key: deletion_protection.enabled
      Value: 'false'
    - Key: access_logs.s3.bucket
      Value: ''
    ```

    确认 `load_balancing.cross_zone.enabled` 的值为 `true`。

## 访问数据库

### 准备一台可以访问集群的机器

我们为 TiDB 集群创建的是内网 LoadBalancer 。我们可在集群 VPC 内创建一台 [堡垒机](https://aws.amazon.com/quickstart/architecture/linux-bastion/) 访问数据库。

参考 AWS [Linux 堡垒机](https://aws.amazon.com/quickstart/architecture/linux-bastion/) 文档在 AWS Console 上创建即可。

VPC 和 Subnet 需选择集群的 VPC 和 Subnet ，在下拉框通过集群名字确认是否正确。并可通过以下命令查看集群的 VPC 和 Subnet 来验证：

{{< copyable "shell-regular" >}}

```shell
eksctl get cluster -n <clusterName>
```

同时需允许本机网络访问，并选择正确的 Key Pair 以便能通过 SSH 登录机器。

> **注意：**
>
> 也可以使用 [VPC Peering](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) 连接现有机器到集群 VPC。
> 若 EKS 是在已经存在的 VPC 中创建的，可使用 VPC 内现有机器。

### 安装 MySQL 客户端并连接

待创建好堡垒机后，我们可以通过 SSH 远程连接到堡垒机，再通过 MySQL 客户端 来访问 TiDB 集群。

{{< copyable "shell-regular" >}}

```shell
ssh [-i /path/to/your/private-key.pem] ec2-user@<bastion-public-dns-name>
```

安装 MySQL 客户端：

{{< copyable "shell-regular" >}}

```shell
sudo yum install mysql -y
```

{{< copyable "shell-regular" >}}

```shell
mysql -h <tidb-nlb-dnsname> -P 4000 -u root
```

`<tidb-nlb-dnsname>` 为 TiDB Service 的 LoadBalancer 域名，可以通过 `kubectl get svc basic-tidb -n tidb-cluster` 输出中的 `EXTERNAL-IP` 字段查看。

示例：

```shell
$ mysql -h abfc623004ccb4cc3b363f3f37475af1-9774d22c27310bc1.elb.us-west-2.amazonaws.com -P 4000 -u root
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 1189
Server version: 5.7.25-TiDB-v4.0.2 TiDB Server (Apache License 2.0) Community Edition, MySQL 5.7 compatible

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [(none)]> show status;
+--------------------+--------------------------------------+
| Variable_name      | Value                                |
+--------------------+--------------------------------------+
| Ssl_cipher         |                                      |
| Ssl_cipher_list    |                                      |
| Ssl_verify_mode    | 0                                    |
| Ssl_version        |                                      |
| ddl_schema_version | 22                                   |
| server_id          | ed4ba88b-436a-424d-9087-977e897cf5ec |
+--------------------+--------------------------------------+
6 rows in set (0.00 sec)
```

> **注意：**
>
> TiDB（v4.0.2 起）默认会定期收集使用情况信息，并将这些信息分享给 PingCAP 用于改善产品。若要了解所收集的信息详情及如何禁用该行为，请参见[遥测](https://docs.pingcap.com/zh/tidb/stable/telemetry)。

## Grafana 监控

先获取 Grafana 的 LoadBalancer 域名：

{{< copyable "shell-regular" >}}

```shell
kubectl get svc basic-grafana
```

示例：

```
$ kubectl get svc basic-grafana
NAME            TYPE           CLUSTER-IP      EXTERNAL-IP                                                             PORT(S)          AGE
basic-grafana   LoadBalancer   10.100.199.42   a806cfe84c12a4831aa3313e792e3eed-1964630135.us-west-2.elb.amazonaws.com 3000:30761/TCP   121m
```

其中 `EXTERNAL-IP` 栏即为 LoadBalancer 域名。

你可以通过浏览器访问 `<grafana-lb>:3000` 地址查看 Grafana 监控指标。其中 `<grafana-lb>` 替换成前面获取的域名。

Grafana 默认登录信息：

- 用户名：admin
- 密码：admin

## 升级 TiDB 集群

要升级 TiDB 集群，可以通过 `kubectl edit tc basic -n tidb-cluster` 修改 `spec.version`。

升级过程会持续一段时间，你可以通过 `kubectl get pods -n tidb-cluster --watch` 命令持续观察升级进度。

## 扩容 TiDB 集群

要升级 TiDB 集群，可以通过 `kubectl edit tc basic -n tidb-cluster` 修改各组件的 `replicas`。

注意扩容前需要多相应的节点组进行扩容，以便新的实例有足够的资源运行。

下面是将集群 `<clusterName>` 的 `tikv` 组扩容到 4 节点的示例：

{{< copyable "shell-regular" >}}

```shell
eksctl scale nodegroup --cluster <clusterName> --name tikv --nodes 4 --nodes-min 4 --nodes-max 4
```

更多可参考 eksctl [节点组管理](https://eksctl.io/usage/managing-nodegroups/)文档。

## 部署 TiFlash/TiCDC

### 新增节点组

```
  - name: tiflash
    desiredCapacity: 1
    labels:
      role: tiflash
    taints:
      dedicated: tiflash:NoSchedule
  - name: ticdc
    desiredCapacity: 1
    labels:
      role: ticdc
    taints:
      dedicated: ticdc:NoSchedule
```

注：`desiredCapacity` 决定期望的节点数，根据实际需求而定。

### 配置并部署

如果要部署 TiFlash，可以在 tidb-cluster.yaml 中配置 `spec.tiflash`，例如：

```yaml
spec:
  ...
  tiflash:
    baseImage: pingcap/tiflash
    replicas: 1
    storageClaims:
    - resources:
        requests:
          storage: 100Gi
    tolerations:
    - effect: NoSchedule
      key: dedicated
      operator: Equal
      value: tiflash
```

> **警告：**
>
> 由于 TiDB Operator 会按照 `storageClaims` 列表中的配置**按顺序**自动挂载 PV，如果需要为 TiFlash 增加磁盘，请确保只在列表原有配置**最后添加**，并且**不能**修改列表中原有配置的顺序。

如果要部署 TiCDC，可以在 tidb-cluster.yaml 中配置 `spec.ticdc`，例如：

```yaml
spec:
  ...
  ticdc:
    baseImage: pingcap/ticdc
    replicas: 1
    tolerations:
    - effect: NoSchedule
      key: dedicated
      operator: Equal
      value: ticdc
```

根据实际情况修改 `replicas` 等参数。

更多可参考 [API 文档](https://github.com/pingcap/tidb-operator/blob/master/docs/api-references/docs.md)和[集群配置文档](configure-a-tidb-cluster.md)完成 CR 文件配置。

## 使用企业版

值得注意的是，如果需要部署企业版的 TiDB/PD/TiKV/TiFlash/TiCDC，需要将 tidb-cluster.yaml 中 `spec.<tidb/pd/tikv/tiflash/ticdc>.baseImage` 配置为企业版镜像，格式为 `pingcap/<tidb/pd/tikv/tiflash/ticdc>-enterprise`。

例如:

```yaml
spec:
  ...
  pd:
    baseImage: pingcap/pd-enterprise
  ...
  tikv:
    baseImage: pingcap/tikv-enterprise
```

## 使用本地存储

AWS 部分实例类型提供额外的 [NVMe SSD 本地存储卷](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html)。可以为 TiKV 节点池选择这一类型的实例，以便提供更高的 IOPS 和低延迟。

> **注意：**
> 
> 由于 EKS 升级过程中节点重建，本地盘数据会[丢失](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html#instance-store-lifetime)。若无法接受 EKS 升级或其他原因导致节点重建，需要迁移 TiKV 数据，不建议在生产环境中使用本地盘。

了解哪些实例可提供本地存储卷，可以查看 [AWS 实例列表](https://aws.amazon.com/ec2/instance-types/)。以下以 `c5d.4xlarge` 为例： 

1, 为 TiKV 创建附带本地存储的节点组

修改 `eksctl` 配置文件中 TiKV 节点组实例类型为 `c5d.4xlarge`：

```
  - name: tikv
    instanceType: c5d.4xlarge
    labels:
      role: tikv
    taints:
      dedicated: tikv:NoSchedule
    ...
```

创建节点组：

{{< copyable "shell-regular" >}}

```shell
eksctl create nodegroups -f cluster.yaml
```

若 tikv 组已存在，可先删除再创建，或者修改名字规避名字冲突。

2, 部署 local volume provisioner

本地存储需要使用 [local-volume-provisioner](https://sigs.k8s.io/sig-storage-local-static-provisioner) 程序发现并管理。以下命令会部署并创建一个 `local-storage` 的 Storage Class。

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/eks/local-volume-provisioner.yaml
```

3, 使用本地存储

完成前面步骤后，local-volume-provisioner 即可发现集群内所有本地 NVMe SSD 盘。修改 tidb-cluster.yaml 中 `tikv.storageClassName` 为 `local-storage` 即可。

运行中的 TiDB 集群不能动态更换 storage class ，可创建一个新的 TiDB 集群测试。
