---
title: 访问 Kubernetes 上的 TiDB 集群
summary: 介绍如何访问 Kubernetes 上的 TiDB 集群。
---

# 访问 TiDB 集群

[Service](https://kubernetes.io/docs/concepts/services-networking/service/) 可以根据不同访问场景配置为 `ClusterIP`、`NodePort` 或 `LoadBalancer` 类型，每种类型对应不同的访问方式。

## ClusterIP

`ClusterIP` 通过集群的内部 IP 暴露服务，选择该类型的服务时，只能在集群内部访问。

可以选择在同一个 Namespace 下访问（如 basic-tidb），或者跨 Namespace 访问（如 basic-tidb.default 或 basic-tidb.default.svc）。

- basic-tidb (仅限同 Namespace)
- basic-tidb.default
- basic-tidb.default.svc

其中，`basic-tidb` 是 `Service` 的名称，`default` 是 `Namespace` 的名称, 详见 [Kubernetes Service 的 DNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#namespaces-of-services)

每个 `TiDBGroup` 会创建一个能够访问该 TiDBGroup 所有 TiDB 的 Service。例如，TiDBGroup `tidb-0` 会创建一个内部 Service `tidb-0-tidb`。

可以直接使用该默认 Service 访问 TiDB，也可以根据需要自行创建 Service。

以下 YAML 示例用于创建一个能够访问 Cluster `db` 下所有 TiDB 节点的 Service。

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

以下 YAML 示例用于创建一个能够访问 Cluster `db` 下特定 TiDBGroup `tidb-0` 所有 TiDB 节点的 Service。

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

在没有 LoadBalancer 的环境下，可以通过 NodePort 将服务暴露到集群外部，允许通过节点 IP 和端口访问服务。

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

详见 [NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport)

> **注意：**
>
> NodePort 模式并不适合在生产环境下使用，生产环境下建议使用 LoadBalancer 模式暴露服务

## LoadBalancer

若运行在支持 LoadBalancer 的云平台（如 Google Cloud 或 AWS），建议使用云平台提供的 LoadBalancer 特性来暴露服务，以获得更好的可用性和负载均衡能力。

参考 [AWS LoadBalancer](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/) 和 [GCP LoadBalancer](https://cloud.google.com/kubernetes-engine/docs/concepts/service-load-balancer) 文档，通过创建 LoadBalancer Service 访问 TiDB 服务。

访问 [Kubernetes Service 文档](https://kubernetes.io/docs/concepts/services-networking/service/)，了解更多 Service 特性以及云平台 Load Balancer 支持。
