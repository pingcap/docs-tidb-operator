---
title: Access TiDB Dashboard
summary: Learn how to access TiDB Dashboard in Kubernetes.
aliases: ['/docs/tidb-in-kubernetes/dev/access-dashboard/']
---

# Access TiDB Dashboard

TiDB Dashboard is a visualized tool in TiDB 4.0 used to monitor and diagnose the TiDB cluster. For details, see [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard-intro).

This document describes how to access TiDB Dashboard in Kubernetes.

## Prerequisites

To access TiDB Dashboard smoothly in Kubernetes, you need to use TiDB Operator v1.1.1 (or later versions) and the TiDB cluster (v4.0.1 or later versions).

You need to configure the `TidbCluster` object file as follows to enable quick access to TiDB Dashboard:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  pd:
    enableDashboardInternalProxy: true
```

## Quick start

> **Warning:**
>
> This guide shows how to quickly access TiDB Dashboard. Do **NOT** use this method in the production environment. For production environments, refer to [Access TiDB Dashboard by Ingress](#access-tidb-dashboard-by-ingress).

TiDB Dashboard is built in the PD component in TiDB 4.0 and later versions. You can refer to the following example to quickly deploy a v4.0.4 TiDB cluster in Kubernetes.

1. Deploy the following `.yaml` file into the Kubernetes cluster by running the `kubectl apply -f` command:

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: basic
    spec:
      version: v4.0.7
      timezone: UTC
      pvReclaimPolicy: Delete
      pd:
        enableDashboardInternalProxy: true
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
    ```

2. After the cluster is created, expose TiDB Dashboard to the local machine by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl port-forward svc/basic-discovery -n ${namespace} 10262:10262
    ```

3. Visit <http://localhost:10262/dashboard> in your browser to access TiDB Dashboard.

## Access TiDB Dashboard by Ingress

In important production environments, it is recommended to expose the TiDB Dashboard service using Ingress.

### Prerequisites

Before using Ingress, install the Ingress controller in your Kubernetes cluster. Otherwise, simply creating Ingress resources does not take effect.

To deploy the Ingress controller, refer to [ingress-nginx](https://kubernetes.github.io/ingress-nginx/deploy/). You can also choose from [various Ingress controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/).

### Use Ingress

You can expose the TiDB Dashboard service outside the Kubernetes cluster by using Ingress. In this way, the service can be accessed outside Kubernetes via `http`/`https`. For more details, see [Ingress](https://kubernetes.io/zh/docs/concepts/services-networking/ingress/).

The following is an `.yaml` example of accessing TiDB Dashboard using Ingress:

1. Deploy the following `.yaml` file to the Kubernetes cluster by running the `kubectl apply -f` command:

    ```yaml
    apiVersion: extensions/v1beta1
    kind: Ingress
    metadata:
      name: access-dashboard
      namespace: ${namespace}
    spec:
      rules:
        - host: ${host}
          http:
            paths:
              - backend:
                  serviceName: ${cluster_name}-discovery
                  servicePort: 10262
                path: /dashboard
    ```

2. After Ingress is deployed, you can access TiDB Dashboard via <http://${host}/dashboard> outside the Kubernetes cluster.

## Enable Ingress TLS

Ingress supports TLS. See [Ingress TLS](https://kubernetes.io/docs/concepts/services-networking/ingress/#tls). The following example shows how to use Ingress TLS:

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: access-dashboard
  namespace: ${namespace}
spec:
  tls:
  - hosts:
    - ${host}
    secretName: testsecret-tls
  rules:
    - host: ${host}
      http:
        paths:
          - backend:
              serviceName: ${cluster_name}-discovery
              servicePort: 10262
            path: /dashboard
```

In the above file, `testsecret-tls` contains `tls.crt` and `tls.key` needed for `example.com`.

This is an example of `testsecret-tls`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: testsecret-tls
  namespace: default
data:
  tls.crt: base64 encoded cert
  tls.key: base64 encoded key
type: kubernetes.io/tls
```

After Ingress is deployed, visit <https://{host}/dashboard> to access TiDB Dashboard.

## Update the TiDB cluster

To enable quick access to TiDB Dashboard by updating an existing TiDB cluster, update the following two configurations:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  configUpdateStrategy: RollingUpdate
  pd:
    enableDashboardInternalProxy: true
```
