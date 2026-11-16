---
title: Access the TiDB Cluster on Kubernetes
summary: Learn how to access the TiDB cluster on Kubernetes.
---

# Access the TiDB Cluster on Kubernetes

This document describes how to access a TiDB cluster through a Kubernetes [Service](https://kubernetes.io/docs/concepts/services-networking/service/). You can configure the Service as one of the following types, depending on your access requirements:

* [`ClusterIP`](#clusterip): for access from within the Kubernetes cluster only.
* [`NodePort`](#nodeport): for access from outside the cluster (recommended for test environments).
* [`LoadBalancer`](#loadbalancer): for access through your cloud provider's LoadBalancer feature (recommended for production environments).

## Security prerequisites

Complete the following steps before you make port `4000` reachable from outside the Kubernetes cluster:

1. Using a trusted internal connection method such as `kubectl port-forward`, set a strong password for the TiDB `root` account. Create separate least-privileged SQL accounts for applications instead of using `root`. For account-management guidance, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management/).
2. [Enable TLS for the MySQL client](enable-tls-for-mysql-client.md), configure clients to verify the TiDB server certificate, and enforce encrypted connections on the server. Depending on your access policy, set the TiDB [`require_secure_transport`](https://docs.pingcap.com/tidb/stable/system-variables/#require_secure_transport-new-in-v610) system variable to `ON`, or configure each externally accessible account with `REQUIRE SSL`.
3. Restrict the source networks that can reach the Service. An internal load balancer alone does not limit access to trusted clients, so apply source filtering to both internal and external `LoadBalancer` Services. For `NodePort`, apply cloud firewall rules, security groups, or network ACLs to trusted networks only to prevent bypassing the LoadBalancer source filtering.

> **Warning:**
>
> A newly bootstrapped TiDB cluster can accept `root` connections without a password. Never expose the MySQL port to the public internet before authentication, TLS, and source-network restrictions are in place. The Service examples in this document configure routing only; they do not establish an authentication boundary.

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
> It is not recommended to use `NodePort` in production environments. For production environments on cloud platforms, use the `LoadBalancer` type instead. In either case, allow access only from trusted source networks after completing the [security prerequisites](#security-prerequisites).

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

Cloud providers can create an internet-facing load balancer by default. Prefer a provider-specific internal load balancer, but an internal load balancer is not itself a source-network restriction. For both internal and external load balancers, restrict the Service to the required client CIDR ranges, for example:

```yaml
spec:
  type: LoadBalancer
  loadBalancerSourceRanges:
    - 203.0.113.0/24 # Replace with an actual trusted client CIDR.
```

Do not use `0.0.0.0/0`. Verify that your cloud provider enforces `loadBalancerSourceRanges`; if it does not, apply equivalent provider firewall or security-group rules. A `LoadBalancer` Service normally also allocates a NodePort, which might remain directly reachable even when load balancer traffic is restricted. Restrict that NodePort at the node firewall, or set `allocateLoadBalancerNodePorts: false` if your provider supports load balancing without NodePorts. When you disable NodePort allocation on an existing Service, also remove every allocated `spec.ports[].nodePort`, because Kubernetes does not remove these values automatically. Internal-load-balancer annotations and these capabilities differ by provider; review the provider documentation before applying the Service.

For more information, see the following documents:

- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/)
- [Google Cloud LoadBalancer Service](https://cloud.google.com/kubernetes-engine/docs/concepts/service-load-balancer)
- [Azure Load Balancer Service](https://learn.microsoft.com/en-us/azure/aks/load-balancer-standard)

To learn more about Kubernetes Service types and cloud provider support for LoadBalancer, see the [Kubernetes Service documentation](https://kubernetes.io/docs/concepts/services-networking/service/).
