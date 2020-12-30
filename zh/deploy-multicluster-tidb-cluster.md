---
title: 跨 Kubernetes 集群的 TiDB 多集群部署
summary: 本文档介绍如何实现跨 Kubernetes 集群的 TiDB 多集群部署
---

## 什么是跨 Kubernetes 集群的 TiDB 多集群部署

跨 Kubernetes 集群的 TiDB 多集群部署是指在 VPC 原生 Kubernetes 集群上部署数据联通, 可以在集群间容灾, 扩缩容的 TiDB 多集群. 所谓 VPC 原生 Kubernetes 集群, 指部署的目标 Kubernetes 集群都处于同一网络环境下(如同一 VPC 下), POD IP 在任意集群上和集群间可互相访问, FQDN 记录是集群上和集群间均可被解析的. 满足上述条件的 Kubernetes 集群可以进行 TiDB 多集群部署. 您可以参考 GKE 上关于 [创建 VPC 原生集群](https://cloud.google.com/kubernetes-engine/docs/how-to/alias-ips) 相关章节了解更多细节.

## 前置条件

- 各集群上的 POD IP 可以在同一网络/VPC 内被互相访问
- 集群上 Service 的 FQDN 记录可以在集群间解析和访问

## 目前支持场景

- 部署新的开启跨 Kubernetes 集群的 TiDB 多集群, 允许在其他 Kubernetes 集群上部署开启此功能的新集群加入同样开启此功能的集群

## 不支持场景

- 两个已有数据集群互相连通, 对于这一场景应通过数据迁移完成
- 对已有数据的集群从未开启此功能状态变为开启此功能状态, 目前需要通过数据迁移完成此需求

## 跨 Kubernetes 集群的 TiDB 多集群部署

部署跨 Kubernetes 集群的 TiDB 多集群, 默认您已部署好此场景所需要的 VPC 原生 Kubernetes 集群, 在此基础上进行下面的部署工作. 如果还没有部署好相应的 Kubernetes 集群, 请通过各计算服务提供商的创建 VPC 原生集群的相关文档完成 Kubernetes 部署工作.

下面以部署两个集群为例进行介绍, 其中集群1为初始集群, 按照下面给出的配置进行创建, 先于集群2部署, 集群1正常运行后, 按照下面给出配置创建集群2, 等集群完成创建和部署工作后, 两集群正常运行.

### 部署初始集群

通过如下命令部署初始化集群, 实际使用中需要根据您的实际情况设置 `cluster1_name` 和 `cluster1_domain` 变量的内容, 其中 `cluster1_name` 为集群1的集群名称, `cluster1_domain` 为集群1的 cluster domain, `cluster1_namespace` 为集群1的命名空间 

```bash
# 集群1的集群名称
cluster1_name="cluster1"
# 集群1的cluster domain
cluster1_domain="cluster1.com"
# 集群1的命名空间
cluster1_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster1_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster1_name}"
  namespace: pingcap
spec:
  version: v4.0.9
  timezone: UTC
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster1_domain}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "1Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: {}
EOF
```

### 部署新集群加入初始集群

等待集群1完成部署, 完成部署后, 创建集群2, 相关命令如下. 在实际使用中, 集群1并不一定是初始集群, 可以指定多集群内的任一集群加入即可.

```bash
# 集群1的集群名称
cluster1_name="cluster1"
# 集群1的cluster domain
cluster1_domain="cluster1.com"
# 集群1的命名空间
cluster1_namespace="pingcap"

# 集群2的集群名称
cluster2_name="cluster2"
# 集群2的cluster domain
cluster2_domain="cluster2.com"
# 集群2的命名空间
cluster2_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster2_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster2_name}"
  namespace: pingcap
spec:
  version: v4.0.9
  timezone: UTC
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster2_domain}"
  cluster:
    name: "${cluster1_name}"
    namespace: "${cluster1_namespace}"
    clusterDomain: "${cluster1_clusterdomain}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "1Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: {}
EOF
```

## 开启 TLS 的跨 Kubernetes 集群的 TiDB 多集群部署

在部署跨 Kubernetes 集群的 TiDB 多集群过程中, TLS 需要显示声明，需要创建新的 `Secret` 证书文件，使用和目标集群相同的 CA (Certification Authority) 颁发。如果使用 `cert-manager` 方式，需要使用和目标集群相同的 `Issuer` 来创建 `Certificate`。

在为跨 Kubernetes 集群的 TiDB 多集群开启 TiDB 组件间 TLS 中, 需要注意证书授权对象是否包含了多集群上的各个组件

其他 TLS 相关信息，可参考以下文档：

- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)

### 部署初始集群

通过如下命令部署初始化集群, 实际使用中需要根据您的实际情况设置 `cluster1_name` 和 `cluster1_domain` 变量的内容, 其中 `cluster1_name` 为集群1的集群名称, `cluster1_domain` 为集群1的 cluster domain, `cluster1_namespace` 为集群1的命名空间 

```bash
# 集群1的集群名称
cluster1_name="cluster1"
# 集群1的cluster domain
cluster1_domain="cluster1.com"
# 集群1的命名空间
cluster1_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster1_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster1_name}"
  namespace: pingcap
spec:
  version: v4.0.9
  timezone: UTC
  tlsCluster:
   enabled: true
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster1_domain}"
  discovery: {}
  pd:
    baseImage: registry.cn-beijing.aliyuncs.com/tidb/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: registry.cn-beijing.aliyuncs.com/tidb/tikv
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: registry.cn-beijing.aliyuncs.com/tidb/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: 
      security:
       cert-allowed-cn:
         - TiDB
EOF
```

### 部署新集群加入初始集群

等待集群1完成部署, 完成部署后, 创建集群2, 相关命令如下. 在实际使用中, 集群1并不一定是初始集群, 可以指定多集群内的任一集群加入即可.

```bash
# 集群1的集群名称
cluster1_name="cluster1"
# 集群1的cluster domain
cluster1_domain="cluster1.com"
# 集群1的命名空间
cluster1_namespace="pingcap"

# 集群2的集群名称
cluster2_name="cluster2"
# 集群2的cluster domain
cluster2_domain="cluster2.com"
# 集群2的命名空间
cluster2_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster2_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster2_name}"
  namespace: pingcap
spec:
  version: v4.0.9
  timezone: UTC
  tlsCluster:
   enabled: true
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster2_domain}"
  cluster:
    name: "${cluster1_name}"
    namespace: "${cluster1_namespace}"
    clusterDomain: "${cluster1_clusterdomain}"
  discovery: {}
  pd:
    baseImage: registry.cn-beijing.aliyuncs.com/tidb/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: registry.cn-beijing.aliyuncs.com/tidb/tikv
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: registry.cn-beijing.aliyuncs.com/tidb/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: 
      security:
       cert-allowed-cn:
         - TiDB
EOF
```

更多示例信息, 请参阅 [`multi-cluster`](https://github.com/pingcap/tidb-operator/tree/master/examples/multi-cluster)