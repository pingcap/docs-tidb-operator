---
title: Kubernetes 与 TiDB 集群的监控与告警
summary: 介绍如何在 Kubernetes 上部署 TiDB 集群监控。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/monitor-a-tidb-cluster/', '/docs-cn/tidb-in-kubernetes/dev/monitor-using-tidbmonitor/', '/zh/tidb-in-kubernetes/stable/monitor-using-tidbmonitor/']
---

# Kubernetes 与 TiDB 集群的监控与告警

基于 Kubernetes 环境部署的 TiDB 集群监控可以大体分为两个部分：对 **TiDB 集群本身**的监控、对 **Kubernetes 集群**及 **TiDB Operator** 的监控。

## TiDB 集群的监控

TiDB 通过 Prometheus 和 Grafana 监控 TiDB 集群。在通过 TiDB Operator 创建新的 TiDB 集群时，可以对于每个 TiDB 集群，创建、配置一套独立的监控系统，与 TiDB 集群运行在同一 Namespace，包括 Prometheus 和 Grafana 两个组件。

可以在 `TidbMonitor` 中设置 `spec.persistent` 为 `true` 来持久化监控数据。开启此选项时应将 `spec.storageClassName` 设置为一个当前集群中已有的存储，并且此存储应当支持将数据持久化，否则会存在数据丢失的风险。

在 [TiDB 集群监控](https://pingcap.com/docs-cn/stable/deploy-monitoring-services/)中有一些监控系统配置的细节可供参考。

### 访问 Grafana 监控面板

可以通过 `kubectl port-forward` 访问 Grafana 监控面板：

{{< copyable "shell-regular" >}}

```shell
kubectl port-forward -n ${namespace} svc/${cluster_name}-grafana 3000:3000 &>/tmp/portforward-grafana.log &
```

然后在浏览器中打开 [http://localhost:3000](http://localhost:3000)，默认用户名和密码都为 `admin`。

也可以设置 `spec.grafana.service.type` 为 `NodePort` 或者 `LoadBalancer`，通过 `NodePort` 或者 `LoadBalancer` 查看监控面板。

如果不需要使用 Grafana，可以在部署时将 `TidbMonitor` 中的 `spec.grafana` 部分删除。这一情况下需要使用其他已有或新部署的数据可视化工具直接访问监控数据来完成可视化。

### 访问 Prometheus 监控数据

对于需要直接访问监控数据的情况，可以通过 `kubectl port-forward` 来访问 Prometheus：

{{< copyable "shell-regular" >}}

```shell
kubectl port-forward -n ${namespace} svc/${cluster_name}-prometheus 9090:9090 &>/tmp/portforward-prometheus.log &
```

然后在浏览器中打开 [http://localhost:9090](http://localhost:9090)，或通过客户端工具访问此地址即可。

也可以设置 `spec.prometheus.service.type` 为 `NodePort` 或者 `LoadBalancer`，通过 `NodePort` 或者 `LoadBalancer` 访问监控数据。

## Kubernetes 的监控

随集群部署的 TiDB 监控只关注 TiDB 本身各组件的运行情况，并不包括对容器资源、宿主机、Kubernetes 组件和 TiDB Operator 等的监控。对于这些组件或资源的监控，需要在整个 Kubernetes 集群维度部署监控系统来实现。

### 宿主机监控

对宿主机及其资源的监控与传统的服务器物理资源监控相同。

如果在你的现有基础设施中已经有针对物理服务器的监控系统，只需要通过常规方法将 Kubernetes 所在的宿主机添加到现有监控系统中即可；如果没有可用的监控系统，或者希望部署一套独立的监控系统用于监控 Kubernetes 所在的宿主机，也可以使用你熟悉的任意监控系统。

新部署的监控系统可以运行于独立的服务器、直接运行于 Kubernetes 所在的宿主机，或运行于 Kubernetes 集群内，不同部署方式除在安装配置与资源利用上存在少许差异，在使用上并没有重大区别。

常见的可用于监控服务器资源的开源监控系统有：

- [CollectD](https://collectd.org/)
- [Nagios](https://www.nagios.org/)
- [Prometheus](http://prometheus.io/) & [node_exporter](https://github.com/prometheus/node_exporter)
- [Zabbix](https://www.zabbix.com/)

一些云服务商或专门的性能监控服务提供商也有各自的免费或收费的监控解决方案可以选择。

我们推荐通过 [Prometheus Operator](https://github.com/coreos/prometheus-operator) 在 Kubernetes 集群内部署基于 [Node Exporter](https://github.com/prometheus/node_exporter) 和 Prometheus 的宿主机监控系统，这一方案同时可以兼容并用于 Kubernetes 自身组件的监控。

### Kubernetes 组件监控

对 Kubernetes 组件的监控可以参考[官方文档](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/)提供的方案，也可以使用其他兼容 Kubernetes 的监控系统来进行。

一些云服务商可能提供了自己的 Kubernetes 组件监控方案，一些专门的性能监控服务商也有各自的 Kubernetes 集成方案可以选择。

由于 TiDB Operator 实际上是运行于 Kubernetes 中的容器，选择任一可以覆盖对 Kubernetes 容器状态及资源进行监控的监控系统即可覆盖对 TiDB Operator 的监控，无需再额外部署监控组件。

我们推荐通过 [Prometheus Operator](https://github.com/coreos/prometheus-operator) 部署基于 [Node Exporter](https://github.com/prometheus/node_exporter) 和 Prometheus 的宿主机监控系统，这一方案同时可以兼容并用于对宿主机资源的监控。

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

## Prometheus 配置

如需要自定义 Prometheus 的配置或行为，可为 Prometheus 指定用户自定义配置及额外的命令行参数：

1. 为用户自定义配置创建 ConfigMap 并将 `data` 部分的键名设置为 `prometheus-config`。
2. 设置 `spec.prometheus.config.configMapRef.name` 与 `spec.prometheus.config.configMapRef.namespace` 为自定义 ConfigMap 的名称与所属的 namespace。
3. 设置 `spec.prometheus.config.commandOptions` 为用于启动 Prometheus 的额外的命令行参数。

## 告警配置

### TiDB 集群告警

在随 TiDB 集群部署 Prometheus 时，会自动导入一些默认的告警规则，可以通过浏览器访问 Prometheus 的 Alerts 页面查看当前系统中的所有告警规则和状态。

目前支持自定义配置告警规则，可以参考下面步骤修改告警规则：

1. 在为 TiDB 集群部署监控的过程中，设置 `spec.reloader.service.type` 为 `NodePort` 或者 `LoadBalancer`。
2. 通过 `NodePort` 或者 `LoadBalancer` 访问 reloader 服务，点击上方 `Files` 选择要修改的告警规则文件进行修改，修改完成后 `Save`。

默认的 Prometheus 和告警配置不能发送告警消息，如需发送告警消息，可以使用任意支持 Prometheus 告警的工具与其集成。推荐通过 [AlertManager](https://prometheus.io/docs/alerting/alertmanager/) 管理与发送告警消息。

如果在你的现有基础设施中已经有可用的 AlertManager 服务，可以参考[设置 kube-prometheus 与 AlertManager](#设置-kube-prometheus-与-alertmanager) 设置 `spec.alertmanagerURL` 配置其地址供 Prometheus 使用；如果没有可用的 AlertManager 服务，或者希望部署一套独立的服务，可以参考官方的[说明](https://github.com/prometheus/alertmanager)部署。

### Kubernetes 告警

如果使用 Prometheus Operator 部署针对 Kubernetes 宿主机和服务的监控，会默认配置一些告警规则，并且会部署一个 AlertManager 服务，具体的设置方法请参阅 [kube-prometheus](https://github.com/coreos/kube-prometheus) 的说明。

如果使用其他的工具或服务对 Kubernetes 宿主机和服务进行监控，请查阅该工具或服务提供商的对应资料。
