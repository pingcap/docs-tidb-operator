---
title: TiDB 集群的监控与告警
summary: 介绍如何监控 TiDB 集群。
---

# TiDB 集群的监控与告警

本文介绍如何对通过 TiDB Operator 部署的 TiDB 集群进行监控及配置告警。

## TiDB 集群的监控

TiDB 集群的监控包括两部分：[监控数据采集](#监控数据采集)和[监控面板](#监控面板)。你可以使用 [Prometheus](https://prometheus.io/) 或 [VictoriaMetrics](https://victoriametrics.com/) 等开源组件采集监控数据，然后通过 [Grafana](https://grafana.com/) 实现监控面板的展示。

![TiDB 集群的监控架构](/media/overview-of-monitoring-tidb-clusters.png)

### 监控数据采集

#### 使用 Prometheus 采集监控数据

使用 Prometheus 采集监控数据的步骤如下：

1. 参考 [Prometheus Operator 官方文档](https://prometheus-operator.dev/docs/getting-started/installation/)，在 Kubernetes 集群中部署 Prometheus Operator，本文档以 `v0.82.0` 版本为例。

2. 在每个 TiDB 集群所在的命名空间中创建一个 `PodMonitor` Custom Resource (CR)：

    ```yaml
    apiVersion: monitoring.coreos.com/v1
    kind: PodMonitor
    metadata:
      name: tidb-cluster-pod-monitor
      namespace: ${tidb_cluster_namespace}
      labels:
        monitor: tidb-cluster
    spec:
      jobLabel: "pingcap.com/component"
      namespaceSelector:
        matchNames:
          - ${tidb_cluster_namespace}
      selector:
        matchLabels:
          app.kubernetes.io/managed-by: tidb-operator
      podMetricsEndpoints:
        - interval: 15s
          # 若 TiDB 集群启用了 TLS，则设置为 https，否则设置为 http
          scheme: https
          honorLabels: true
          # 若 TiDB 集群启用了 TLS，则需配置 tlsConfig，否则无需配置
          tlsConfig:
            ca:
              secret:
                name: db-cluster-client-secret
                key: ca.crt
            cert:
              secret:
                name: db-cluster-client-secret
                key: tls.crt
            keySecret:
              name: db-cluster-client-secret
              key: tls.key
          metricRelabelings:
            - action: labeldrop
              regex: container
          relabelings:
            - sourceLabels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
              action: keep
              regex: "true"
            - sourceLabels:
                - __meta_kubernetes_pod_name
                - __meta_kubernetes_pod_label_app_kubernetes_io_instance
                - __meta_kubernetes_pod_label_app_kubernetes_io_component
                - __meta_kubernetes_namespace
                - __meta_kubernetes_pod_annotation_prometheus_io_port
              action: replace
              regex: (.+);(.+);(.+);(.+);(.+)
              replacement: $1.$2-$3-peer.$4:$5
              targetLabel: __address__
            - sourceLabels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
              targetLabel: __metrics_path__
            - sourceLabels: [__meta_kubernetes_namespace]
              targetLabel: kubernetes_namespace
            - sourceLabels: [__meta_kubernetes_pod_label_app_kubernetes_io_instance]
              targetLabel: cluster
            - sourceLabels: [__meta_kubernetes_pod_name]
              targetLabel: instance
            - sourceLabels: [__meta_kubernetes_pod_label_app_kubernetes_io_component]
              targetLabel: component
            - sourceLabels:
                - __meta_kubernetes_namespace
                - __meta_kubernetes_pod_label_app_kubernetes_io_instance
              separator: '-'
              targetLabel: tidb_cluster
    ```

3. 参考 [Prometheus Operator 官方文档](https://prometheus-operator.dev/docs/platform/platform-guide/#deploying-prometheus)，创建一个 `Prometheus` CR 用来采集监控指标，确保为 ServiceAccount 分配必要权限：

    ```yaml
    apiVersion: monitoring.coreos.com/v1
    kind: Prometheus
    metadata:
      name: prometheus
      namespace: monitoring
    spec:
      serviceAccountName: prometheus
      externalLabels:
        k8s_cluster: ${your_k8s_cluster_name}
      podMonitorSelector:
        matchLabels:
          monitor: tidb-cluster
      # podMonitorNamespaceSelector 设置为空，表示采集所有命名空间中的 PodMonitor
      podMonitorNamespaceSelector: {}
    ```

4. 运行以下 `kubectl port-forward` 命令，通过端口转发访问 Prometheus：

    ```shell
    kubectl port-forward -n monitoring prometheus-prometheus-0 9090:9090 &>/tmp/portforward-prometheus.log &
    ```

    然后在浏览器中访问 <http://localhost:9090/targets> 查看监控数据采集状态。

#### 使用 VictoriaMetrics 采集监控数据

使用 VictoriaMetrics 部署监控数据采集的步骤如下：

1. 参考 [VictoriaMetrics 官方文档](https://docs.victoriametrics.com/operator/quick-start/)，在 Kubernetes 集群中部署 VictoriaMetrics Operator，本文档以 `v0.58.1` 版本为例。

2. 创建一个 `VMSingle` Custom Resource (CR) 用来存储监控指标：

    ```yaml
    apiVersion: victoriametrics.com/v1beta1
    kind: VMSingle
    metadata:
      name: demo
      namespace: monitoring
    ```

3. 创建一个 `VMAgent` CR 用来采集监控指标：

    ```yaml
    apiVersion: victoriametrics.com/v1beta1
    kind: VMAgent
    metadata:
      name: demo
      namespace: monitoring
    spec:
      # 配置远程写入，将采集到的监控指标写入 VMSingle
      remoteWrite:
        - url: "http://vmsingle-demo.monitoring.svc:8429/api/v1/write"
      externalLabels:
        k8s_cluster: ${your_k8s_cluster_name}
      selectAllByDefault: true
    ```

4. 在每个 TiDB 集群所在的命名空间中创建一个 `VMPodScrape` CR，用来发现 TiDB 集群的 Pod，并为 `VMAgent` 生成相应的 scrape 配置：

    ```yaml
    apiVersion: victoriametrics.com/v1beta1
    kind: VMPodScrape
    metadata:
      name: tidb-cluster-pod-scrape
      namespace: ${tidb_cluster_namespace}
    spec:
      jobLabel: "pingcap.com/component"
      namespaceSelector:
        matchNames:
          - ${tidb_cluster_namespace}
      selector:
        matchLabels:
          app.kubernetes.io/managed-by: tidb-operator
      podMetricsEndpoints:
        - interval: 15s
          # 若 TiDB 集群启用了 TLS，则设置为 https，否则设置为 http
          scheme: https
          honorLabels: true
          # 若 TiDB 集群启用了 TLS，则需配置 TLS 认证，否则无需配置
          tlsConfig:
            ca:
              secret:
                name: db-cluster-client-secret
                key: ca.crt
            cert:
              secret:
                name: db-cluster-client-secret
                key: tls.crt
            keySecret:
              name: db-cluster-client-secret
              key: tls.key
          metricRelabelConfigs:
            - action: labeldrop
              regex: container
          relabelConfigs:
            - sourceLabels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
              action: keep
              regex: "true"
            - sourceLabels:
                - __meta_kubernetes_pod_name
                - __meta_kubernetes_pod_label_app_kubernetes_io_instance
                - __meta_kubernetes_pod_label_app_kubernetes_io_component
                - __meta_kubernetes_namespace
                - __meta_kubernetes_pod_annotation_prometheus_io_port
              action: replace
              regex: (.+);(.+);(.+);(.+);(.+)
              replacement: $1.$2-$3-peer.$4:$5
              targetLabel: __address__
            - sourceLabels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
              targetLabel: __metrics_path__
            - sourceLabels: [__meta_kubernetes_namespace]
              targetLabel: kubernetes_namespace
            - sourceLabels: [__meta_kubernetes_pod_label_app_kubernetes_io_instance]
              targetLabel: cluster
            - sourceLabels: [__meta_kubernetes_pod_name]
              targetLabel: instance
            - sourceLabels: [__meta_kubernetes_pod_label_app_kubernetes_io_component]
              targetLabel: component
            - sourceLabels:
                - __meta_kubernetes_namespace
                - __meta_kubernetes_pod_label_app_kubernetes_io_instance
              separator: '-'
              targetLabel: tidb_cluster
    ```

5. 运行以下 `kubectl port-forward` 命令，通过端口转发访问 VMAgent：

    ```shell
    kubectl port-forward -n monitoring svc/vmagent-demo 8429:8429 &>/tmp/portforward-vmagent.log &
    ```

    然后在浏览器中访问 <http://localhost:8429/targets> 查看监控数据采集状态。

### 监控面板

配置监控面板的步骤如下：

1. 参考 [Grafana 官方文档](https://grafana.com/docs/grafana/latest/setup-grafana/installation/kubernetes/#deploy-grafana-on-kubernetes)，在 Kubernetes 集群中部署 Grafana，本文档以 `12.0.0-security-01` 版本为例。

2. 运行以下 `kubectl port-forward` 命令，通过端口转发访问 Grafana 监控面板：

    ```shell
    kubectl port-forward -n ${namespace} ${grafana_pod_name} 3000:3000 &>/tmp/portforward-grafana.log &
    ```

3. 在浏览器中访问 <http://localhost:3000>，默认用户名和密码都为 `admin`。如果是通过 Helm 安装，可以使用以下命令查看 `admin` 密码：

    ```shell
    kubectl get secret --namespace ${namespace} ${grafana_secret_name} -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
    ```

4. 在 Grafana 中添加 Prometheus 类型的数据源，并配置 Prometheus Server URL：

    - 如果使用 Prometheus 采集监控指标，设置 URL 为 `http://prometheus-operated.monitoring.svc:9090`。
    - 如果使用 VictoriaMetrics 采集监控指标，设置 URL 为 `http://vmsingle-demo.monitoring.svc:8429`。

5. 可以使用 [`get-grafana-dashboards.sh`](<https://raw.githubusercontent.com/pingcap/tidb-operator/refs/tags/{{{ .tidb_operator_version }}}/hack/get-grafana-dashboards.sh>) 脚本下载各组件的监控面板，然后手动导入到 Grafana 中。

## 告警配置

你可以通过 [AlertManager](https://github.com/prometheus/alertmanager) 管理与发送告警信息，具体的部署和配置步骤请参考 [Alertmanager 官方文档](https://prometheus.io/docs/alerting/alertmanager/)。

## 使用 Grafana 查看多集群监控

要使用 Grafana 查看多个集群的监控，请在每个 Grafana Dashboard 中进行以下操作：

1. 在 Grafana Dashboard 中，点击 **Dashboard settings** 选项，打开 **Settings** 页面。
2. 在 **Settings** 页面中，选择 **Variables** 中的 **tidb_cluster** 变量，将 **tidb_cluster** 变量的 **Hide** 属性设置为空选项。
3. 返回当前 Grafana Dashboard，即可看到集群选择下拉框。下拉框中的集群名称格式为 `${namespace}-${tidb_cluster_name}`。
4. 点击 **Save dashboard** 保存对该 Dashboard 的修改。
