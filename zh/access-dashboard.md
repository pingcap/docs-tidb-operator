---
title: 访问 TiDB Dashboard
summary: 介绍如何在 Kubernetes 环境下访问 TiDB Dashboard
aliases: ['/docs-cn/tidb-in-kubernetes/dev/access-dashboard/']
---

# 访问 TiDB Dashboard

TiDB Dashboard 是从 TiDB 4.0 版本起引入的可视化面板，用于帮助观察与诊断整个 TiDB 集群，详情参见 [TiDB 文档 - TiDB Dashboard](https://docs.pingcap.com/zh/tidb/stable/dashboard-intro)。本篇文章将介绍如何在 Kubernetes 环境下访问 TiDB Dashboard。

- 在测试环境中，你可以[通过端口转发访问 TiDB Dashboard](#方法-1-通过端口转发访问-tidb-dashboard)。
- 在生产环境中，推荐[通过 Ingress 访问 TiDB Dashboard](#方法-2-通过-ingress-访问-tidb-dashboard)，并选择开启 TLS 加密传输，见[使用 Ingress 并开启 TLS](#使用-ingress-并开启-tls)。
- 如果需要使用非域名的方式访问 TiDB Dashboard，可以选择[使用 NodePort Service](#方法-3-使用-nodeport-service)。

> **注意：**
>
> TiDB Dashboard 中的部分功能会因为 Kubernetes 的特殊环境而无法使用，详见 [TiDB Operator 中不支持的 Dashboard 功能](#tidb-operator-中不支持的-dashboard-功能)。

本文档介绍的方法通过 Discovery 服务访问 TiDB Dashboard。TiDB Operator 会为每一个 TiDB 集群启动一个 Discovery 服务。Discovery 服务会为每个 PD Pod 返回相应的启动参数，来辅助 PD 集群启动。此外，Discovery 服务也会发送代理请求到 TiDB Dashboard。

> **警告：**
>
> TiDB Dashboard 位于 PD 的 `/dashboard` 路径中。其他路径可能无法访问控制。

## 前置条件

你需要使用 v1.1.1 版本及以上的 TiDB Operator 以及 v4.0.1 版本及以上的 TiDB 集群，才能在 Kubernetes 环境中流畅使用 `Dashboard`。你需要在 `TidbCluster` 对象文件中通过以下方式开启 `Dashboard` 快捷访问:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  pd:
    enableDashboardInternalProxy: true
```

## 方法 1. 通过端口转发访问 TiDB Dashboard

> **警告：**
>
> 以下教程仅为演示如何快速访问 TiDB Dashboard，请勿在生产环境中直接使用以下方法。

在 4.0.0 及以上版本的 TiDB 中，TiDB Dashboard 目前已经内嵌在了 PD 组件中，你可以通过以下的例子在 Kubernetes 环境下快速部署一个 TiDB 集群。

1. 运行 `kubectl apply -f` 命令，本文档以如下 YAML 文件为例，将该 YAML 文件部署到 Kubernetes 集群中：

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: basic
    spec:
      version: v5.3.0
      timezone: UTC
      pvReclaimPolicy: Delete
      pd:
        enableDashboardInternalProxy: true
        baseImage: pingcap/pd
        maxFailoverCount: 0
        replicas: 1
        requests:
          storage: "10Gi"
        config: {}
      tikv:
        baseImage: pingcap/tikv
        maxFailoverCount: 0
        replicas: 1
        requests:
          storage: "100Gi"
        config: {}
    tidb:
        baseImage: pingcap/tidb
        maxFailoverCount: 0
        replicas: 1
        service:
          type: ClusterIP
        config: {}
    ```

2. 当集群创建完毕时，可以通过以下命令将 TiDB Dashboard 暴露在本地机器:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl port-forward svc/basic-discovery -n ${namespace} 10262:10262
    ```

    `port-forward` 默认绑定 IP 地址 127.0.0.1。如果你需要使用其它 IP 地址访问运行 `port-forward` 命令的机器，可以通过 `--address` 选项指定需要绑定的 IP 地址。

3. 在浏览器中访问 <http://localhost:10262/dashboard>，即可访问到 TiDB Dashboard。

## 方法 2. 通过 Ingress 访问 TiDB Dashboard

> **注意：**
>
> 推荐在生产环境、关键环境内使用 Ingress 来暴露 TiDB Dashboard 服务。

### 环境准备

使用 Ingress 前需要 Kubernetes 集群安装有 Ingress 控制器，仅创建 Ingress 资源无效。你可能需要部署 Ingress 控制器，例如 [ingress-nginx](https://kubernetes.github.io/ingress-nginx/deploy/)。你可以从许多 [Ingress 控制器](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) 中进行选择。

### 使用 Ingress

你可以通过 Ingress 来将 TiDB Dashboard 服务暴露到 Kubernetes 集群外，从而在 Kubernetes 集群外通过 http/https 的方式访问服务。你可以通过 [Ingress](https://kubernetes.io/zh/docs/concepts/services-networking/ingress/) 了解更多关于 Ingress 的信息。以下是一个使用 Ingress 访问 TiDB Dashboard 的 yaml 文件例子。运行 `kubectl apply -f` 命令，将以下 yaml 文件部署到 Kubernetes 集群中。

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

当部署了 Ingress 后，你可以在 Kubernetes 集群外通过 <http://${host}/dashboard> 访问 TiDB Dashboard。

### 使用 Ingress 并开启 TLS

Ingress 提供了 TLS 支持，你可以通过 [Ingress TLS](https://kubernetes.io/zh/docs/concepts/services-networking/ingress/#tls) 了解更多。以下是一个使用 Ingress TLS 的例子，其中 `testsecret-tls` 包含了 `exmaple.com` 所需要的 `tls.crt` 与 `tls.key`：

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

以下是 `testsecret-tls` 的一个例子:

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

当 Ingress 部署完成以后，你就可以通过 <https://{host}/dashboard> 访问 TiDB Dashboard。

## 方法 3. 使用 NodePort Service

由于 Ingress 必需使用域名访问，在某些场景下可能难以使用，此时可以通过添加一个 `NodePort` 类型的 `Service` 来访问和使用 TiDB Dashboard。

以下是一个使用 `NodePort` 类型的 `Service` 访问 TiDB Dashboard 的 yaml 文件例子。运行 `kubectl apply -f` 命令，将以下 yaml 文件部署到 Kubernetes 集群中。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: access-dashboard
  namespace: ${namespace}
spec:
  ports:
  - name: dashboard
    port: 10262
    protocol: TCP
    targetPort: 10262
  type: NodePort
  selector:
    app.kubernetes.io/component: discovery
    app.kubernetes.io/instance: ${cluster_name}
    app.kubernetes.io/name: tidb-cluster
```

当 `Service` 部署完成后，可以通过 <https://{nodeIP}:{nodePort}/dashboard> 访问 TiDB Dashboard, 其中 `nodePort` 默认由 Kubernetes 随机分配，也可以在 yaml 文件中指定一个可用的端口。

需要注意如果 PD Pod 数量超过 1 ，需要在 TidbCluster CR 中设置 `spec.pd.enableDashboardInternalProxy: true` 以保证正常访问 TiDB Dashboard。

## 启用持续分析功能

持续性能分析允许用户在不重启的情况下持续收集 TiDB、TiKV、PD、TiFlash 各个实例的性能数据，并且持久监控节点。收集到的性能数据可显示为火焰图、有向无环图等，直观展现实例在性能收集的时间段内执行的各种内部操作及其比例，方便用户快速了解该实例 CPU 资源消耗细节。

你需要使用 v1.3.0 版本及以上的 TiDB Operator 部署 TidbNGMonitoring CR 才可以开启持续分析功能。

1. 参照[部署 TiDB 集群监控与告警](monitor-a-tidb-cluster.md)部署 TidbMonitor CR。

2. 部署 TidbNGMonitoring CR。
    
    执行以下命令部署 TidbNGMonitoring CR，其中， `${cluster_name}` 为 TidbCluster CR 的名称，`${cluster_ns}` 为 TidbCluster CR 所在的命名空间。

    {{< copyable "shell-regular" >}}

    ```bash
    cat << EOF | kubectl apply -n ${ns} -f -
    apiVersion: pingcap.com/v1alpha1
    kind: TidbNGMonitoring
    metadata:
      name: ${name}
    spec:
      clusters:
      - name: ${cluster_name}
        ns: ${cluster_ns}
      
      ngMonitoring:
        requests:
          storage: 10Gi
        version: v5.4.0
        baseImage: pingcap/ng-monitoring
    ```

    关于 TidbNGMonitoring CR 的更多配置项，可参考 [tidb-operator 中的示例](https://github.com/pingcap/tidb-operator/blob/master/examples/advanced/tidb-ng-monitoring.yaml)。

3. 启用持续性能分析。
   
    1. 进入 TiDB Dashboard，选择**高级调试** (Advanced Debugging) > **实例性能分析** (Profile Instances) > **持续分析** (Continuous Profile)。
    2. 点击**打开设置** (Open Settings)。在右侧**设置** (Settings) 页面，将**启用特性** (Enable Feature) 下方的开关打开。设置**保留时间** (Retention Period) 或保留默认值。
    3. 点击**保存** (Save)。

    ![启用功能](/media/dashboard-conprof-start.png)

关于持续分析功能的更多操作可以参考文档[TiDB Dashboard 实例性能分析 - 持续分析页面](https://docs.pingcap.com/zh/tidb/stable/continuous-profiling#tidb-dashboard-%E5%AE%9E%E4%BE%8B%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90---%E6%8C%81%E7%BB%AD%E5%88%86%E6%9E%90%E9%A1%B5%E9%9D%A2)。

## TiDB Operator 中不支持的 Dashboard 功能

TiDB Dashboard 中的部分功能会因为 kubernetes 的特殊环境而无法使用，包括以下功能：

+ **概况** -> **监控和告警** -> **查看监控项**的链接无法正确跳转到 Grafana 监控页。如果需要访问 Grafana 监控，可以参考[访问 Grafana 监控面板](monitor-a-tidb-cluster.md#访问-grafana-监控面板)。

+ 日志搜索功能无法使用。如果需要查看对应组件的日志，可以使用 `kubectl logs ${pod_name} -n {namespace}` 查看对应组件的日志，或者通过 Kubernetes 集群的日志服务查看。

+ **集群信息** -> **主机** 的磁盘容量，磁盘使用率无法正确显示。可以通过 [TidbMonitor 监控面板](monitor-a-tidb-cluster.md#访问-grafana-监控面板) 的各组件 dashboards 查看各个组件的磁盘使用，或者部署 [Kubernetes 宿主机 Grafana 监控](monitor-kubernetes.md#kubernetes-组件监控) 查看 Kubernetes 节点的磁盘使用情况。
