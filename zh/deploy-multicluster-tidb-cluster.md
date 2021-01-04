---
title: 跨多个 Kubernetes 集群的 TiDB 多集群部署
summary: 本文档介绍如何实现跨多个 Kubernetes 集群的 TiDB 多集群部署
---

## 什么是跨多个 Kubernetes 集群的 TiDB 多集群部署

跨多个 Kubernetes 集群的 TiDB 多集群部署是指在多个互相联通的 Kubernetes 集群部署数据联通, 可以在集群间容灾, 扩缩容的 TiDB 多集群. 所谓 Kubernetes 集群互相连通, 在此文档中指部署的目标 Kubernetes 集群都处于同一网络环境下(如同一 VPC 下), POD IP 在任意集群内和集群间可互相访问, FQDN 记录是集群内和集群间均可被解析的. 满足上述条件的 Kubernetes 集群可以进行 TiDB 多集群部署.

## 前置条件

- 各集群上的 POD IP 可以在同一网络/VPC 内被互相访问
- 集群上使用了 Cluster Domain 的 FQDN 记录可以在集群间解析和访问

## 目前支持场景

- 部署新的开启跨多个 Kubernetes 集群的 TiDB 多集群, 允许在其他 Kubernetes 集群上部署开启此功能的新集群加入同样开启此功能的集群
## 实验性支持场景

- 对已有数据的集群从未开启此功能状态变为开启此功能状态, 生产使用建议通过数据迁移完成此需求

## 不支持场景

- 两个已有数据集群互相连通, 对于这一场景应通过数据迁移完成

## 跨多个 Kubernetes 集群的 TiDB 多集群部署

部署跨多个 Kubernetes 集群的 TiDB 多集群, 默认您已部署好此场景所需要的 Kubernetes 集群, 在此基础上进行下面的部署工作.

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

## 开启 TLS 的跨多个 Kubernetes 集群的 TiDB 多集群部署

在部署跨多个 Kubernetes 集群的 TiDB 多集群过程中, TLS 需要显示声明，需要创建新的 `Secret` 证书文件，使用和目标集群相同的 CA (Certification Authority) 颁发。如果使用 `cert-manager` 方式，需要使用和目标集群相同的 `Issuer` 来创建 `Certificate`。

在为跨多个 Kubernetes 集群的 TiDB 多集群开启 TiDB 组件间 TLS 中, 需要注意证书授权对象是否包含了多集群上的各个组件

其他 TLS 相关信息，可参考以下文档：

- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)

### 签发证书

相较于普通场景, 在跨多个 Kubernetes 集群的 TiDB 多集群场景下, 签发证书的 hosts 中多了`${cluster_name}-pd.${namespace}.svc.${cluster_domain}`此类格式的记录, 例如 PD 的证书

```json
"hosts": [
    "127.0.0.1",
    "::1",
    "${cluster_name}-pd",
    "${cluster_name}-pd.${namespace}",
    "${cluster_name}-pd.${namespace}.svc",
    "${cluster_name}-pd.${namespace}.svc.${cluster_domain}",
    "${cluster_name}-pd-peer",
    "${cluster_name}-pd-peer.${namespace}",
    "${cluster_name}-pd-peer.${namespace}.svc",
    "${cluster_name}-pd-peer.${namespace}.svc.${cluster_domain}",
    "*.${cluster_name}-pd-peer",
    "*.${cluster_name}-pd-peer.${namespace}",
    "*.${cluster_name}-pd-peer.${namespace}.svc",
    "*.${cluster_name}-pd-peer.${namespace}.svc.${cluster_domain}",
],
```

在签发相关 TLS 证书时, 需要注意加上带有 clusterDomain 的格式 host 记录.

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
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
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
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "1Gi"
    config: 
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: 
      security:
       cert-allowed-cn:
         - TiDB
EOF
```

## 已加入集群的退出和回收

当我们需要让一个集群从所加入跨 Kubernetes 部署的TiDB集群退出并回收空间时, 我们可以通过缩容流程来实现上述需求. 在此场景下, 我们需要满足缩容的一些限制, 限制如下:

- 缩容后, 集群中 TiKV 副本数应大于 PD 中设置的 max-replicas 数量, 默认情况下 TiKV 副本数量需要大于3

我们以上面文档创建的 cluster2 集群为例, 先将 PD, TiKV, TiDB 的副本数设置为0, 如果开启了 TiFlash, TiCDC, Pump, Drainer 或其他组件, 也请一并将其副本数设为0

```bash
kubectl patch tc cluster2 --type merge -p '{"spec":{"pd":{"replicas":0},"tikv":{"replicas":0},"tidb":{"replicas":0}}}'
```

等待 cluster2 集群状态变为 Ready, 相关组件被缩容到 0 副本时, cluster2 已经退出集群, 

```bash
watch kubectl get tc cluster2
```

此时我们可以删除该对象, 对相关资源进行回收.

```bash
kubectl delete tc cluster2
```

通过上述步骤, 我们完成了已加入集群的退出和资源回收.

## 已有数据集群开启跨多个 Kubernetes 集群功能并作为 TiDB 多集群的初始集群

*注意: 目前此场景属于实验性支持, 可能会造成数据丢失, 请谨慎使用

编辑已有集群的 tidbcluster 对象

```bash
kubectl edit tidbcluster cluster1
```

在 spec 字段里添加 clusterDomain 字段, 比如 .spec.clusterDomain: "cluster1.com", 可以参考上面初始集群的 YAML 文件修改此处. 修改完成后, TiDB 集群进入滚动更新状态.

滚动更新结束后, 需要进入 PD 容器, 使用容器内的 /pd-ctl 更新 PD 的 `advertise-url` 信息, 具体操作如下:

使用端口转发一个 PD 实例的端口

```bash
kubectl port-forward pods/cluster1-pd-0 2380:2380 2379:2379 -n pingcap
```

获取集群信息

> Note:
>
> 如果开启了 TLS, 则需要配置安全证书. 例如:
> 
> curl --cacert /var/lib/pd-tls/ca.crt --cert /var/lib/pd-tls/tls.crt --key /var/lib/pd-tls/tls.key https://127.0.0.1:2379/v2/members
>
> 后面使用 curl 时都需要带上证书相关信息

```bash
curl http://127.0.0.1:2379/v2/members
```

执行后输出如下结果

```output
{"members":[{"id":"6ed0312dc663b885","name":"cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster.local","peerURLs":["http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster.local:2379"]},{"id":"bd9acd3d57e24a32","name":"cluster1-pd-1.cluster1-pd-peer.pingcap.svc.cluster.local","peerURLs":["http://cluster1-pd-1.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-1.cluster1-pd-peer.pingcap.svc.cluster.local:2379"]},{"id":"e04e42cccef60246","name":"cluster1-pd-2.cluster1-pd-peer.pingcap.svc.cluster.local","peerURLs":["http://cluster1-pd-2.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-2.cluster1-pd-peer.pingcap.svc.cluster.local:2379"]}]}
```

记录 member ID, 使用 member ID 更新 Peer URL

```bash
member_ID="6ed0312dc663b885"
member_peer_url="http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster.local:2380"

curl http://127.0.0.1:2379/v2/members/${member_ID} -XPUT \
-H "Content-Type: application/json" -d '{"peerURLs":["${member_peer_url}"]}'
```

更多示例信息以及开发信息, 请参阅 [`multi-cluster`](https://github.com/pingcap/tidb-operator/tree/master/examples/multi-cluster)