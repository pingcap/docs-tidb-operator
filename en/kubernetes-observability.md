---
title: "Kubernetes Observability: Monitoring, Alerts, and Log Collection"
summary: Learn how to monitor, configure alerts, and collect logs on Kubernetes.
---

# Kubernetes Observability: Monitoring, Alerts, and Log Collection

This document describes how to monitor, configure alerts, and collect logs in a Kubernetes cluster. These practices help you assess the health and status of your cluster and its components.

## Monitoring

### Monitor TiDB components

The TiDB monitoring system deployed with the cluster only focuses on the operation of the TiDB components themselves, and does not include the monitoring of container resources, hosts, Kubernetes components, or TiDB Operator. To monitor these components or resources, you need to deploy a monitoring system across the entire Kubernetes cluster.

### Monitor the host

Monitoring the host and its resources works in the same way as monitoring physical resources of a traditional server.

If you already have a monitoring system for your physical server in your existing infrastructure, you only need to add the host that holds Kubernetes to the existing monitoring system by conventional means. If there is no monitoring system available, or if you want to deploy a separate monitoring system to monitor the host that holds Kubernetes, then you can use any monitoring system that you are familiar with.

The newly deployed monitoring system can run on a separate server, directly on the host that holds Kubernetes, or in a Kubernetes cluster. Different deployment methods might have differences in the deployment configuration and resource utilization, but there are no major differences in usage.

The following lists some common open source monitoring systems that can be used to monitor server resources:

- [Prometheus](https://prometheus.io/) and [node_exporter](https://github.com/prometheus/node_exporter)
- [VictoriaMetrics](https://victoriametrics.com/)
- [CollectD](https://collectd.org/)
- [Nagios](https://www.nagios.org/)
- [Zabbix](https://www.zabbix.com/)

Some cloud service providers or specialized performance monitoring service providers also have their own free or paid monitoring solutions that you can choose from.

It is recommended to deploy a host monitoring system in the Kubernetes cluster using [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) based on [Node Exporter](https://github.com/prometheus/node_exporter) and Prometheus. This solution can also be compatible with and used for monitoring the Kubernetes' own components.

### Monitor Kubernetes components

For monitoring Kubernetes components, you can refer to the solutions provided in the [Kubernetes official documentation](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-usage-monitoring/) or use other Kubernetes-compatible monitoring systems.

Some cloud service providers might provide their own solutions for monitoring Kubernetes components. Some specialized performance monitoring service providers have their own Kubernetes integration solutions that you can choose from.

TiDB Operator is actually a container running in Kubernetes. For this reason, you can monitor TiDB Operator by choosing any monitoring system that can monitor the status and resources of a Kubernetes container without deploying additional monitoring components.

It is recommended to deploy a host monitoring system using [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) based on [Node Exporter](https://github.com/prometheus/node_exporter) and Prometheus. This solution can also be compatible with and used for monitoring host resources.

## Alerts

If you deploy a monitoring system for Kubernetes hosts and services using Prometheus Operator, some alert rules are configured by default, and an AlertManager service is deployed. For details, see [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus).

If you monitor Kubernetes hosts and services by using other tools or services, you can consult the corresponding information provided by the tool or service provider.

## Log collection

### Collect TiDB and Kubernetes component runtime logs

When you deploy TiDB using TiDB Operator, all components write runtime logs the container's `stdout` and `stderr` by default. On Kubernetes, these logs are stored in the `/var/log/containers` directory on host machines, and filenames include the Pod and container names. You can collect application logs in the container directly from the host.

If you already have a log collection system in your existing infrastructure, you only need to add the `/var/log/containers/*.log` files from the Kubernetes hosts to your collection scope. If there is no log collection system available, or if you want to deploy a separate log collection system, then you can use any log collection system that you are familiar with.

The following lists some common open source tools for Kubernetes log collection:

- [Vector](https://vector.dev/)
- [Fluentd](https://www.fluentd.org/)
- [Fluent Bit](https://fluentbit.io/)
- [Filebeat](https://www.elastic.co/products/beats/filebeat)
- [Logstash](https://www.elastic.co/logstash/)

You can typically aggregate collected logs and store them on a central server or in a dedicated storage and analysis system such as [Elasticsearch](https://www.elastic.co/elasticsearch/).

Some cloud service providers or performance monitoring service providers also offer free or paid log collection solutions.

### Collect system logs

You can collect system logs from Kubernetes hosts using standard methods. If you already have a log collection system in your existing infrastructure, you only need to add the relevant servers and log files to the collection scope. If there is no log collection system available, or if you want to deploy a separate log collection system, then you can use any log collection system that you are familiar with.

All tools listed in the [Collect TiDB and Kubernetes component runtime logs](#collect-tidb-and-kubernetes-component-runtime-logs) section support system log collection. Additionally, some cloud service providers or performance monitoring service providers also offer free or paid log collection solutions.
