---
title: 跨多个 Kubernetes 集群部署 TiDB 集群
summary: 本文档介绍如何实现跨多个 Kubernetes 集群部署 TiDB 集群
---

# 跨多个 Kubernetes 集群部署 TiDB 集群

跨多个 Kubernetes 集群部署 TiDB 集群，是指在多个网络互通的 Kubernetes 集群上部署**一个** TiDB 集群，集群各个组件分布在多个 Kubernetes 集群上，实现在 Kubernetes 集群间容灾。所谓 Kubernetes 集群网络互通，是指 Pod IP 在任意集群内和集群间可以被互相访问，Pod FQDN 记录在集群内和集群间均可被解析。

## 前置条件

您需要配置 Kubernetes 的网络插件和 DNS 插件，使得 Kubernetes 集群满足以下条件：

- 各 Kubernetes 集群上的 TiDB 组件有能力访问集群内和集群间所有 TiDB 组件的 Pod IP 
- 各 Kubernetes 集群上的 TiDB 组件有能力解析集群内和集群间所有 TiDB 组件的 Pod FQDN

## 目前支持场景

- 新部署跨多个 Kubernetes 集群的 TiDB 集群
- 在其他 Kubernetes 集群上部署开启此功能的新集群加入同样开启此功能的集群

## 实验性支持场景

- 对已有数据的集群从未开启此功能状态变为开启此功能状态，生产使用建议通过数据迁移完成此需求

## 不支持场景

- 两个已有数据集群互相连通，对于这一场景应通过数据迁移完成

## 跨多个 Kubernetes 集群部署 TiDB 集群

部署跨多个 Kubernetes 集群的 TiDB 集群，默认您已部署好此场景所需要的 Kubernetes 集群，在此基础上进行下面的部署工作。

下面以部署两个集群为例进行介绍，其中集群 1 为初始集群，按照下面给出的配置进行创建，集群 1 正常运行后，按照下面给出配置创建集群 2，等集群完成创建和部署工作后，两个集群正常运行。

### 部署初始集群

通过如下命令部署初始化集群，实际使用中需要根据您的实际情况设置 `cluster1_name` 和 `cluster1_domain` 变量的内容，其中 `cluster1_name` 为集群 1 的集群名称，`cluster1_domain` 为集群 1 的 [Cluster Domain](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#introduction), `cluster1_namespace` 为集群 1 的命名空间。

```bash
# 集群 1 的集群名称
cluster1_name="cluster1"
# 集群 1 的Cluster Domain
cluster1_domain="cluster1.com"
# 集群 1 的命名空间
cluster1_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster1_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster1_name}"
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
      storage: "10Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
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

等待集群 1 完成部署，完成部署后，创建集群 2，相关命令如下。在实际使用中，集群 1 并不一定是初始集群，可以指定多集群内的任一集群加入即可。

```bash
# 集群 1 的集群名称
cluster1_name="cluster1"
# 集群 1 的Cluster Domain
cluster1_domain="cluster1.com"
# 集群 1 的命名空间
cluster1_namespace="pingcap"

# 集群 2 的集群名称
cluster2_name="cluster2"
# 集群 2 的Cluster Domain
cluster2_domain="cluster2.com"
# 集群 2 的命名空间
cluster2_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster2_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster2_name}"
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
      storage: "10Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: {}
EOF
```

## 跨多个 Kubernetes 集群部署开启 TLS 的 TiDB 集群

您也可以按照如下步骤对跨多个 Kubernetes 集群部署的 TiDB 集群开启 TLS 功能。
### 签发证书

部署跨多个 Kubernetes 集群部署开启 TLS 的 TiDB 集群，与普通的 TiDB 集群部署过程相比，签发证书过程有以下几点不同：

1. 需要为每个 Kubernetes 集群上的组件签发证书，并加载到对应的 Kubernetes 集群中。
2. 各个 Kubernetes 内 TiDB 组件所使用的证书需要是同一个 CA (Certification Authroity) 签发的。各个组件会通过证书的 CN(Common Name) 来验证证书是否有效。
3. 如果没有跨多个 Kubernetes 集群的 TLS 证书管理方案，建议使用 `cfssl` 签发证书。这是因为 `cert-manager` 的 `Issuer` 目前没有管理跨多个 Kubernetes 集群的 TLS 证书生命周期管理能力。
4. 需要在签发组件证书时，在 hosts 中加上带有 `.${cluster_domain}` 格式的授权记录， 例如 `${cluster_name}-pd.${namespace}.svc.${cluster_domain}`，以 PD 组件证书为例，可以参考下面的 hosts 列表来配置签发各个组件使用的证书：

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

其他 TLS 相关信息，可参考以下文档：

- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)

### 部署初始集群

通过如下命令部署初始化集群，实际使用中需要根据您的实际情况设置 `cluster1_name` 和 `cluster1_domain` 变量的内容，其中 `cluster1_name` 为集群 1 的集群名称，`cluster1_domain` 为集群 1 的 Cluster Domain，`cluster1_namespace` 为集群 1 的命名空间。下面的 YAML 文件已经开启了 TLS 功能，并通过配置 `cert-allowed-cn`，使得各个组件开始验证由 `CN` 为 `TiDB` 的 `CA` 所签发的证书

```bash
# 集群 1 的集群名称
cluster1_name="cluster1"
# 集群 1 的Cluster Domain
cluster1_domain="cluster1.com"
# 集群 1 的命名空间
cluster1_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster1_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster1_name}"
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
      storage: "10Gi"
    config: 
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
    config: 
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    tlsClient:
      enabled: true
    config: 
      security:
       cert-allowed-cn:
         - TiDB
EOF
```

### 部署新集群加入初始集群

等待集群 1 完成部署，完成部署后，创建集群 2 ，相关命令如下。在实际使用中，集群 1 并不一定是初始集群，可以指定多集群内的任一集群加入即可。

```bash
# 集群 1 的集群名称
cluster1_name="cluster1"
# 集群 1 的Cluster Domain
cluster1_domain="cluster1.com"
# 集群 1 的命名空间
cluster1_namespace="pingcap"

# 集群 2 的集群名称
cluster2_name="cluster2"
# 集群 2 的Cluster Domain
cluster2_domain="cluster2.com"
# 集群 2 的命名空间
cluster2_namespace="pingcap"

cat << EOF | kubectl apply -f -n ${cluster2_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster2_name}"
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
      storage: "10Gi"
    config: 
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
    config: 
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    tlsClient:
      enabled: true
    config: 
      security:
       cert-allowed-cn:
         - TiDB
EOF
```

## 已加入集群的退出和回收

当我们需要让一个集群从所加入跨 Kubernetes 部署的 TiDB 集群退出并回收资源时，我们可以通过缩容流程来实现上述需求。在此场景下，我们需要满足缩容的一些限制，限制如下：

- 缩容后，集群中 TiKV 副本数应大于 PD 中设置的 `max-replicas` 数量，默认情况下 TiKV 副本数量需要大于 3

我们以上面文档创建的集群 2 为例，先将 PD，TiKV，TiDB 的副本数设置为 0 ，如果开启了 TiFlash，TiCDC，Pump 等其他组件，也请一并将其副本数设为 0

```bash
kubectl patch tc cluster2 --type merge -p '{"spec":{"pd":{"replicas":0},"tikv":{"replicas":0},"tidb":{"replicas":0}}}'
```

等待集群 2 状态变为 `Ready`，相关组件此时应被缩容到 0 副本：

```bash
kubectl get pods -l app.kubernetes.io/instance=cluster2 -n pingcap
```

Pod 列表显示为 `No resources found.`，此时 Pod 已经被全部缩容，集群 2 已经退出集群，查看集群 2 的集群状态：

```bash
kubectl get tc cluster2
```

结果显示集群 2 为 `Ready` 状态，此时我们可以删除该对象，对相关资源进行回收。

```bash
kubectl delete tc cluster2
```

通过上述步骤，我们完成了已加入集群的退出和资源回收。

## 已有数据集群开启跨多个 Kubernetes 集群功能并作为 TiDB 集群的初始集群

> **警告：**
>
> 目前此场景属于实验性支持，可能会造成数据丢失，请谨慎使用

编辑已有集群的 `tidbcluster` 对象：

```bash
kubectl edit tidbcluster cluster1
```

在 spec 字段里添加 Cluster Domain 字段，比如 `.spec.clusterDomain: "cluster1.com"`，可以参考上面初始集群的 YAML 文件修改此处。修改完成后，TiDB 集群进入滚动更新状态。

滚动更新结束后，需要使用 `port-forward` 访问 PD 的 API 接口，更新 PD 的 `advertise-peer-urls`，具体操作如下：

使用端口转发一个 PD 实例的端口：

```bash
kubectl port-forward pods/cluster1-pd-0 2380:2380 2379:2379 -n pingcap
```

获取集群信息：

> **注意：**
>
> 如果开启了 TLS，则需要配置安全证书。例如：
> 
> `curl --cacert /var/lib/pd-tls/ca.crt --cert /var/lib/pd-tls/tls.crt --key /var/lib/pd-tls/tls.key https://127.0.0.1:2379/v2/members`
>
> 后面使用 curl 时都需要带上证书相关信息

```bash
curl http://127.0.0.1:2379/v2/members
```

执行后输出如下结果：

```output
{"members":[{"id":"6ed0312dc663b885","name":"cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster.local","peerURLs":["http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster.local:2379"]},{"id":"bd9acd3d57e24a32","name":"cluster1-pd-1.cluster1-pd-peer.pingcap.svc.cluster.local","peerURLs":["http://cluster1-pd-1.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-1.cluster1-pd-peer.pingcap.svc.cluster.local:2379"]},{"id":"e04e42cccef60246","name":"cluster1-pd-2.cluster1-pd-peer.pingcap.svc.cluster.local","peerURLs":["http://cluster1-pd-2.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-2.cluster1-pd-peer.pingcap.svc.cluster.local:2379"]}]}
```

记录各个 PD 实例的 `member ID`，使用 `member ID` 依次更新每个成员的 `Peer URL`，更新方法如下所示：

```bash
member_ID="6ed0312dc663b885"
member_peer_url="http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster.local:2380"

curl http://127.0.0.1:2379/v2/members/${member_ID} -XPUT \
-H "Content-Type: application/json" -d '{"peerURLs":["${member_peer_url}"]}'
```

更多示例信息以及开发信息，请参阅 [`multi-cluster`](https://github.com/pingcap/tidb-operator/tree/master/examples/multi-cluster)
