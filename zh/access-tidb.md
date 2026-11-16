---
title: 访问 Kubernetes 上的 TiDB 集群
summary: 介绍如何访问 Kubernetes 上的 TiDB 集群。
---

# 访问 Kubernetes 上的 TiDB 集群

本文介绍如何通过 Kubernetes [Service](https://kubernetes.io/zh-cn/docs/concepts/services-networking/service/) 访问 TiDB 集群。根据不同的访问场景需求，你可以将 Service 配置为以下类型：

- [`ClusterIP`](#clusterip)：仅限 Kubernetes 集群内部访问
- [`NodePort`](#nodeport)：允许从集群外部访问（适用于测试环境）
- [`LoadBalancer`](#loadbalancer)：通过云平台的 LoadBalancer 特性访问（推荐用于生产环境）

## 安全前置条件

在允许从 Kubernetes 集群外部访问 `4000` 端口之前，请完成以下操作：

1. 先通过 `kubectl port-forward` 等可信的内部连接方式，为 TiDB `root` 用户设置高强度密码。为应用创建单独的最小权限 SQL 用户，不要使用 `root` 用户连接应用。账号管理方法参见 [TiDB 用户账户管理](https://docs.pingcap.com/zh/tidb/stable/user-account-management/)。
2. [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)，配置客户端验证 TiDB Server 证书，并在服务端强制使用加密连接。根据访问策略，将 TiDB [`require_secure_transport`](https://docs.pingcap.com/zh/tidb/stable/system-variables/#require_secure_transport-从-v610-版本开始引入) 系统变量设置为 `ON`，或者为每个允许从外部访问的账号配置 `REQUIRE SSL`。
3. 限制可以访问 Service 的来源网络。内部负载均衡器本身并不能保证只有可信客户端可以访问，因此内部和外部 `LoadBalancer` Service 都需要配置来源过滤。对于 `NodePort`，使用云防火墙、安全组或网络 ACL，仅允许可信网络访问，防止绕过 LoadBalancer 的来源过滤。

> **警告：**
>
> 新初始化的 TiDB 集群可能允许 `root` 用户无密码连接。在完成身份认证、TLS 和来源网络限制之前，绝不能向公网暴露 MySQL 端口。本文的 Service 示例仅配置网络路由，并不构成身份认证边界。

## ClusterIP

`ClusterIP` 类型的 Service 通过集群的内部 IP 暴露服务，仅支持在 Kubernetes 集群内部访问 TiDB 集群。

你可以使用以下格式之一访问 TiDB 集群：

- `basic-tidb`：仅限在同一 Namespace 内访问
- `basic-tidb.default`：支持跨 Namespace 访问
- `basic-tidb.default.svc`：支持跨 Namespace 访问

其中，`basic-tidb` 是 Service 的名称，`default` 是 Namespace 的名称，详见 [Service 与 Pod 的 DNS](https://kubernetes.io/zh-cn/docs/concepts/services-networking/dns-pod-service/#namespaces-of-services)。

每个 TiDBGroup 会自动创建一个能够访问该 TiDBGroup 所有 TiDB 的 Service。例如，TiDBGroup `tidb-0` 会创建一个内部 Service `tidb-0-tidb`。

> **注意：**
>
> 不建议直接使用默认创建的 Service 访问 TiDB。建议根据实际访问需求自行创建 Service。

以下 YAML 示例用于创建一个能够访问 Cluster `db` 下所有 TiDB 节点的 Service：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tidb
spec:
  selector:
    pingcap.com/managed-by: tidb-operator
    pingcap.com/cluster: db
    pingcap.com/component: tidb
  ports:
    - name: mysql
      protocol: TCP
      port: 4000
      targetPort: mysql-client
```

以下 YAML 示例用于创建一个能够访问 Cluster `db` 下特定 TiDBGroup `tidb-0` 所有 TiDB 节点的 Service：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tidb-0
spec:
  selector:
    pingcap.com/managed-by: tidb-operator
    pingcap.com/cluster: db
    pingcap.com/component: tidb
    pingcap.com/group: tidb-0
  ports:
    - name: mysql
      protocol: TCP
      port: 4000
      targetPort: mysql-client
```

## NodePort

在没有 LoadBalancer 的环境中，可以使用 `NodePort` 类型的 Service 将 TiDB 集群暴露到集群外部，允许通过节点 IP 和指定端口访问 TiDB 集群。有关详细说明，请参阅 [NodePort](https://kubernetes.io/zh-cn/docs/concepts/services-networking/service/#type-nodeport)。

> **注意：**
>
> 不建议在生产环境中使用 NodePort 类型。对于云平台上的生产环境，推荐使用 LoadBalancer 类型。无论使用哪种类型，都必须先完成[安全前置条件](#安全前置条件)，并仅允许可信来源网络访问。

配置示例如下：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tidb-0
spec:
  type: NodePort
  selector:
    pingcap.com/managed-by: tidb-operator
    pingcap.com/cluster: db
    pingcap.com/component: tidb
    pingcap.com/group: tidb-0
  ports:
    - name: mysql
      protocol: TCP
      port: 4000
      targetPort: mysql-client
```

## LoadBalancer

在支持 LoadBalancer 的云平台（如 Google Cloud 或 AWS）上，建议使用云平台提供的 LoadBalancer 特性暴露 TiDB 服务，以获得更好的可用性和负载均衡能力。

云平台可能默认创建面向公网的负载均衡器。建议优先使用云平台提供的内部负载均衡器，但内部负载均衡器本身并不等同于来源网络限制。对于内部和外部负载均衡器，都需要将 Service 限制为所需的客户端 CIDR 范围，例如：

```yaml
spec:
  type: LoadBalancer
  loadBalancerSourceRanges:
    - 203.0.113.0/24 # 替换为实际的可信客户端 CIDR。
```

请勿使用 `0.0.0.0/0`。请确认云平台会强制实施 `loadBalancerSourceRanges`；如果不支持，请配置等效的云防火墙或安全组规则。`LoadBalancer` Service 通常还会分配 NodePort，即使负载均衡器流量已受限制，该 NodePort 也可能仍可被直接访问。请在节点防火墙中限制该 NodePort；如果云平台支持不依赖 NodePort 的负载均衡，也可以设置 `allocateLoadBalancerNodePorts: false`。如果在已有 Service 上关闭 NodePort 分配，还需要删除所有已分配的 `spec.ports[].nodePort`，因为 Kubernetes 不会自动删除这些值。不同云平台配置内部负载均衡器所需的 annotation 及上述能力不同，应用 Service 前请查阅对应云平台的文档。

你可以参考以下官方文档，通过创建 LoadBalancer Service 访问 TiDB 服务：

- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/)
- [Google Cloud LoadBalancer Service](https://cloud.google.com/kubernetes-engine/docs/concepts/service-load-balancer)
- [Azure Load Balancer Service](https://learn.microsoft.com/zh-cn/azure/aks/load-balancer-standard)

访问 [Kubernetes Service 文档](https://kubernetes.io/zh-cn/docs/concepts/services-networking/service/)，了解更多 Service 特性以及云平台 Load Balancer 支持。
