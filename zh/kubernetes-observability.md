---
title: Kubernetes 可观测性：监控、告警与日志收集
summary: 介绍如何在 Kubernetes 集群中进行监控、告警与日志收集。
---

# Kubernetes 可观测性：监控、告警与日志收集

本文介绍如何在 Kubernetes 集群中进行监控、告警与日志收集，帮助你全面掌握集群及其组件的运行状态。

## 监控

### TiDB 组件监控

随集群部署的 TiDB 监控只关注 TiDB 本身各组件的运行情况，并不包括对容器资源、宿主机、Kubernetes 组件和 TiDB Operator 等的监控。对于这些组件或资源的监控，需要在整个 Kubernetes 集群维度部署监控系统来实现。

### 宿主机监控

对宿主机及其资源的监控与传统的服务器物理资源监控相同。

如果在你的现有基础设施中已经有针对物理服务器的监控系统，只需要通过常规方法将 Kubernetes 所在的宿主机添加到现有监控系统中即可；如果没有可用的监控系统，或者希望部署一套独立的监控系统用于监控 Kubernetes 所在的宿主机，可以使用你熟悉的任意监控系统。

新部署的监控系统可以运行于独立的服务器、直接运行于 Kubernetes 所在的宿主机，也可以运行于 Kubernetes 集群内。虽然不同部署方式在安装配置与资源利用上存在少许差异，但是在使用上并没有重大区别。

常见的可用于监控服务器资源的开源监控系统有：

- [Prometheus](https://prometheus.io/) 和 [node_exporter](https://github.com/prometheus/node_exporter)
- [VictoriaMetrics](https://victoriametrics.com/)
- [CollectD](https://collectd.org/)
- [Nagios](https://www.nagios.org/)
- [Zabbix](https://www.zabbix.com/)

一些云服务商或专门的性能监控服务提供商也有各自的免费或收费的监控解决方案可以选择。

推荐通过 [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) 在 Kubernetes 集群内部署基于 [Node Exporter](https://github.com/prometheus/node_exporter) 和 Prometheus 的宿主机监控系统，这一方案同时可以兼容并用于 Kubernetes 自身组件的监控。

### Kubernetes 组件监控

对 Kubernetes 组件的监控可以参考[官方文档](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-usage-monitoring/)提供的方案，也可以使用其他兼容 Kubernetes 的监控系统来进行。

一些云服务商可能提供了自己的 Kubernetes 组件监控方案，一些专门的性能监控服务商也有各自的 Kubernetes 集成方案可以选择。

由于 TiDB Operator 实际上是运行于 Kubernetes 中的容器，选择任一可以覆盖对 Kubernetes 容器状态及资源进行监控的监控系统即可覆盖对 TiDB Operator 的监控，无需再额外部署监控组件。

推荐通过 [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) 部署基于 [Node Exporter](https://github.com/prometheus/node_exporter) 和 Prometheus 的宿主机监控系统，这一方案同时可以兼容并用于对宿主机资源的监控。

## 告警

如果使用 Prometheus Operator 部署针对 Kubernetes 宿主机和服务的监控，会默认配置一些告警规则，并且会部署一个 AlertManager 服务，具体的设置方法请参阅 [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus) 的说明。

如果使用其他的工具或服务对 Kubernetes 宿主机和服务进行监控，请查阅该工具或服务提供商的对应资料。

## 日志收集

### TiDB 与 Kubernetes 组件运行日志

通过 TiDB Operator 部署的 TiDB 各组件默认将运行日志输出到容器的 `stdout` 和 `stderr`。在 Kubernetes 环境中，这些日志存储在宿主机的 `/var/log/containers` 目录下，文件名包含 Pod 和容器名称等信息。因此，你可以直接在宿主机上收集容器中应用的日志。

如果你现有的基础设施已具备日志收集系统，只需要通过常规方法将 Kubernetes 所在的宿主机上的 `/var/log/containers/*.log` 文件加入采集范围即可。如果没有可用的日志收集系统，或者希望部署一套独立的系统用于收集相关日志，可以使用你熟悉的任何日志收集系统或方案。

常见的可用于收集 Kubernetes 日志的开源工具有：

- [Vector](https://vector.dev/)
- [Fluentd](https://www.fluentd.org/)
- [Fluent Bit](https://fluentbit.io/)
- [Filebeat](https://www.elastic.co/products/beats/filebeat)
- [Logstash](https://www.elastic.co/logstash/)

收集到的日志通常可以汇总存储在某一特定的服务器上，或存放到 [Elasticsearch](https://www.elastic.co/elasticsearch/) 等专用的存储和分析系统中。

此外，一些云服务商或性能监控服务提供商也提供了免费或付费的日志收集方案。

### 系统日志

系统日志可以通过常规方法在 Kubernetes 宿主机上收集。如果你现有的基础设施已具备日志收集系统，只需要通过常规方法将相关服务器和日志文件添加到收集范围即可。如果没有可用的日志收集系统，或者希望部署一套独立的系统用于收集相关日志，可以使用你熟悉的任何日志收集系统或方案。

[TiDB 与 Kubernetes 组件运行日志](#tidb-与-kubernetes-组件运行日志)章节提到的几种常见日志收集工具均支持对系统日志的收集。此外，一些云服务商或性能监控服务提供商也提供了免费或付费的日志收集方案。