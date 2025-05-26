---
title: 访问 Kubernetes 上的 TiDB 集群
summary: 介绍如何访问 Kubernetes 上的 TiDB 集群。
---

# 访问 Kubernetes 上的 TiDB 集群

本文介绍如何通过 Kubernetes [Service](https://kubernetes.io/zh-cn/docs/concepts/services-networking/service/) 访问 TiDB 集群。根据不同的访问场景需求，你可以将 Service 配置为以下类型：

- [`ClusterIP`](#clusterip)：仅限 Kubernetes 集群内部访问
- [`NodePort`](#nodeport)：允许从集群外部访问（适用于测试环境）
- [`LoadBalancer`](#loadbalancer)：通过云平台的 LoadBalancer 特性访问（推荐用于生产环境）

## ClusterIP

`ClusterIP` 类型的 Service 通过集群的内部 IP 暴露服务，仅支持在 Kubernetes 集群内部访问 TiDB 集群。

你可以使用以下格式之一访问 TiDB 集群：

- `basic-tidb`：仅限在同一 Namespace 内访问
- `basic-tidb.default`：支持跨 Namespace 访问
- `basic-tidb.default.svc`：支持跨 Namespace 访问

其中，`basic-tidb` 是 Service 的名称，`default` 是 Namespace 的名称，详见 [Service 与 Pod 的 DNS](https://kubernetes.io/zh-cn/docs/concepts/services-networking/dns-pod-service/#namespaces-of-services)。

每个 TiDBGroup 会自动创建一个能够访问该 TiDBGroup 所有 TiDB 的 Service。例如，TiDBGroup `tidb-0` 会创建一个内部 Service `tidb-0-tidb`。

你可以直接使用默认创建的 Service 访问 TiDB，也可以根据需要自行创建 Service。

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
> 不建议在生产环境中使用 NodePort 类型。对于云平台上的生产环境，推荐使用 LoadBalancer 类型。

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

你可以参考以下官方文档，通过创建 LoadBalancer Service 访问 TiDB 服务：

- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/)
- [Google Cloud LoadBalancer Service](https://cloud.google.com/kubernetes-engine/docs/concepts/service-load-balancer)

访问 [Kubernetes Service 文档](https://kubernetes.io/zh-cn/docs/concepts/services-networking/service/)，了解更多 Service 特性以及云平台 Load Balancer 支持。
