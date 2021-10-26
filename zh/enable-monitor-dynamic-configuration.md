---
title: 开启动态配置功能
summary: 动态更新 TidbMonitor 配置
---

# 开启动态配置功能

本文档介绍如何开启 TidbMonitor 动态配置功能。

## 功能介绍

TidbMonitor 支持多集群，分片等功能，Prometheus的配置，Rule，`Targets 变更，如果不开启动态配置需要重启才能生效，如果监控数据量很大，恢复 Prometheus 快照数据耗时会比较长。

当开启动态配置功能，TidbMonitor 的配置都可以做到热更新。

## 如何开启动态配置功能

开启动态配置功能，需要指定 `prometheusReloader` 配置，示例如下:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: monitor
spec:
  clusterScoped: true
  clusters:
    - name: ns1
      namespace: ns1
    - name: ns2
      namespace: ns2
  prometheusReloader:
    baseImage: quay.io/prometheus-operator/prometheus-config-reloader
    version: v0.49.0
  imagePullPolicy: IfNotPresent
```

变更后会发生 TidbMonitor 重启，后续针对 Prometheus 的配置变更都会动态更新。

可以参考 [Example](https://github.com/pingcap/tidb-operator/tree/master/examples/monitor-dynamic-configmap)。
