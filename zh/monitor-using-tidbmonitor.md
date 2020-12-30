---
title: 通过 TidbMonitor 监控 TiDB 集群
aliases: ['/docs-cn/tidb-in-kubernetes/dev/monitor-using-tidbmonitor/']
---

# 通过 TidbMonitor 监控 TiDB 集群

## 持久化监控数据

如果要将 TidbMonitor 的监控数据持久化存储，需要在 TidbMonitor 中开启持久化选项:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: basic
spec:
  clusters:
    - name: basic
  persistent: true
  storageClassName: ${storageClassName}
  storage: 5G
  prometheus:
    baseImage: prom/prometheus
    version: v2.18.1
    service:
      type: NodePort
  grafana:
    baseImage: grafana/grafana
    version: 6.1.6
    service:
      type: NodePort
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v4.0.9
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

你可以通过以下命令来确认 PVC 情况:

{{< copyable "shell-regular" >}}

```shell
kubectl get pvc -l app.kubernetes.io/instance=basic,app.kubernetes.io/component=monitor -n ${namespace}
```

```
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
basic-monitor   Bound    pvc-6db79253-cc9e-4730-bbba-ba987c29db6f   5G         RWO            standard       51s
```

### 设置 kube-prometheus 与 AlertManager

在部分情况下，你可能需要 TidbMonitor 同时获取 Kubernetes 上的监控指标。你可以通过设置 `TidbMonitor.Spec.kubePrometheusURL` 来使其获取 [kube-prometheus](https://github.com/coreos/kube-prometheus) metrics。

同样的，你可以通过设置 TidbMonitor 来将监控推送警报至指定的 [AlertManager](https://prometheus.io/docs/alerting/alertmanager/)。

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: basic
spec:
  clusters:
    - name: basic
  kubePrometheusURL: "your-kube-prometheus-url"
  alertmanagerURL: "your-alert-manager-url"
  prometheus:
    baseImage: prom/prometheus
    version: v2.18.1
    service:
      type: NodePort
  grafana:
    baseImage: grafana/grafana
    version: 6.1.6
    service:
      type: NodePort
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v4.0.9
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

## 开启 Ingress

### 环境准备

使用 `Ingress` 前需要 Kubernetes 集群安装有 `Ingress` 控制器，仅创建 `Ingress` 资源无效。您可能需要部署 `Ingress` 控制器，例如 [ingress-nginx](https://kubernetes.github.io/ingress-nginx/deploy/)。您可以从许多 [Ingress 控制器](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) 中进行选择。

更多关于 `Ingress` 环境准备，可以参考 [Ingress 环境准备](https://kubernetes.io/zh/docs/concepts/services-networking/ingress/#%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87)

### 使用 Ingress 访问 TidbMonitor

目前, `TidbMonitor` 提供了通过 Ingress 将 Prometheus/Grafana 服务暴露出去的方式，你可以通过 [Ingress 文档](https://kubernetes.io/zh/docs/concepts/services-networking/ingress/)了解更多关于 Ingress 的详情。

以下是一个开启了 Prometheus 与 Grafana Ingress 的 `TidbMonitor` 例子：

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: ingress-demo
spec:
  clusters:
    - name: demo
  persistent: false
  prometheus:
    baseImage: prom/prometheus
    version: v2.18.1
    ingress:
      hosts:
      - example.com
      annotations:
        foo: "bar"
  grafana:
    baseImage: grafana/grafana
    version: 6.1.6
    service:
      type: ClusterIP
    ingress:
      hosts:
        - example.com
      annotations:
        foo: "bar"
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v4.0.9
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

你可以通过 `spec.prometheus.ingress.annotations` 与 `spec.grafana.ingress.annotations` 来设置对应的 Ingress Annotations 的设置。如果你使用的是默认的 Nginx Ingress 方案，你可以在 [Nginx Ingress Controller Annotation](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/) 了解更多关于 Annotations 的详情。

`TidbMonitor` 的 Ingress 设置同样支持设置 TLS，以下是一个为 Ingress 设置 TLS 的例子。你可以通过 [Ingress TLS](https://kubernetes.io/zh/docs/concepts/services-networking/ingress/#tls) 来了解更多关于 Ingress TLS 的资料。

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: ingress-demo
spec:
  clusters:
    - name: demo
  persistent: false
  prometheus:
    baseImage: prom/prometheus
    version: v2.18.1
    ingress:
      hosts:
      - example.com
      tls:
      - hosts:
        - example.com
        secretName: testsecret-tls
  grafana:
    baseImage: grafana/grafana
    version: 6.1.6
    service:
      type: ClusterIP
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v4.0.9
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

TLS Secret 必须包含名为 tls.crt 和 tls.key 的密钥，这些密钥包含用于 TLS 的证书和私钥，例如：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: testsecret-tls
  namespace: ${namespace}
data:
  tls.crt: base64 encoded cert
  tls.key: base64 encoded key
type: kubernetes.io/tls
```

在公有云 Kubernetes 集群中，通常可以[配置 Loadbalancer](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/) 通过域名访问 Ingress。如果无法配置 Loadbalancer 服务，比如使用了 NodePort 作为 Ingress 的服务类型，可通过与如下命令等价的方式访问服务：

```shell
curl -H "Host: example.com" ${node_ip}:${NodePort}
```

## 参考

了解 TidbMonitor 更为详细的 API 设置，可以参考 [API 文档](https://github.com/pingcap/tidb-operator/blob/master/docs/api-references/docs.md)。
