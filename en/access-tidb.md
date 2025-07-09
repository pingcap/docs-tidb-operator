---
title: Access the TiDB Cluster on Kubernetes
summary: Learn how to access the TiDB cluster on Kubernetes.
---

# Access the TiDB Cluster on Kubernetes

This document describes how to access a TiDB cluster through a Kubernetes [Service](https://kubernetes.io/docs/concepts/services-networking/service/). You can configure the Service as one of the following types, depending on your access requirements:

* [`ClusterIP`](#clusterip): for access from within the Kubernetes cluster only.
* [`NodePort`](#nodeport): for access from outside the cluster (recommended for test environments).
* [`LoadBalancer`](#loadbalancer): for access through your cloud provider's LoadBalancer feature (recommended for production environments).

## ClusterIP

The `ClusterIP` Service type exposes the TiDB cluster using an internal IP address. It is only accessible from within the Kubernetes cluster.

You can access the TiDB cluster using one of the following DNS formats:

* `basic-tidb`: access is limited to the same namespace.
* `basic-tidb.default`: support cross-namespace access.
* `basic-tidb.default.svc`: support cross-namespace access.

In these formats, `basic-tidb` is the Service name, and `default` is the namespace. For more information, see [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#namespaces-of-services).

Each TiDBGroup automatically creates a Service that provides access to all TiDB instances in that group. For example, the TiDBGroup `tidb-0` creates an internal Service named `tidb-0-tidb`.

> **Note:**
>
> It is not recommended to directly use the default Service to access TiDB. Instead, create custom Services based on your specific needs.

The following YAML example defines a Service that provides access to all TiDB nodes in the `db` cluster:

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

The following YAML example defines a Service that provides access to all TiDB nodes in the TiDBGroup `tidb-0` of the cluster `db`:

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

In environments without a LoadBalancer, you can use a `NodePort` Service to expose TiDB outside the Kubernetes cluster. This allows access using the node's IP address and a specific port. For more information, see [NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport).

> **Note:**
>
> It is not recommended to use `NodePort` in production environments. For production environments on cloud platforms, use the `LoadBalancer` type instead.

The following is an example:

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

On cloud platforms that support LoadBalancer (such as Google Cloud or AWS), it is recommended to use the platform's LoadBalancer feature to expose TiDB. This approach provides higher availability and better load balancing.

For more information, see the following documents:

- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/)
- [Google Cloud LoadBalancer Service](https://cloud.google.com/kubernetes-engine/docs/concepts/service-load-balancer)
- [Azure Load Balancer Service](https://learn.microsoft.com/en-us/azure/aks/load-balancer-standard)

To learn more about Kubernetes Service types and cloud provider support for LoadBalancer, see the [Kubernetes Service documentation](https://kubernetes.io/docs/concepts/services-networking/service/).
