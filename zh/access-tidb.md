---
title: 访问 Kubernetes 上的 TiDB 集群
summary: 介绍如何访问 Kubernetes 上的 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/access-tidb/']
---

# 访问 TiDB 集群

Service 可以根据场景配置不同的类型，比如 `ClusterIP`、`NodePort`、`LoadBalancer` 等，对于不同的类型可以有不同的访问方式。

## ClusterIP

`ClusterIP` 是通过集群的内部 IP 暴露服务，选择该类型的服务时，只能在集群内部访问

可以选择跨 Namespace 访问或者在同一个 Namespace 下访问

- basic-tidb (仅限同 Namespace)
- basic-tidb.default
- basic-tidb.default.svc

详见 [Kubernetes Service 的 DNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#namespaces-of-services)

每个 `TiDBGroup` 会默认创建一个能够访问该 TiDBGroup 所有 TiDB 的内部 Service，比如 TiDBGroup `tidb-0` 会创建一个内部 Service `tidb-0-tidb`

可以直接选择使用该 Service 访问 TiDB，也可以自行创建。

以下命令用于创建一个能够访问 Cluster `db` 下所有 TiDB 的 Service

{{< copyable "" >}}

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

也可以创建一个访问 Cluster `db` 下某个 TiDBGroup `tidb-0` 下所有 TiDB 的 Service

{{< copyable "" >}}

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

在没有 LoadBalancer 时，可选择通过 NodePort 将服务暴露到集群外部。

{{< copyable "" >}}

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
>

## LoadBalancer

若运行在有 LoadBalancer 的环境，比如 Google Cloud、AWS 平台，建议使用云平台的 LoadBalancer 特性。

参考 [AWS LoadBalancer](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/) 和 [GCP LoadBalancer](https://cloud.google.com/kubernetes-engine/docs/concepts/service-load-balancer) 文档，通过创建 LoadBalancer Service 访问 TiDB 服务。

访问 [Kubernetes Service 文档](https://kubernetes.io/docs/concepts/services-networking/service/)，了解更多 Service 特性以及云平台 Load Balancer 支持。
