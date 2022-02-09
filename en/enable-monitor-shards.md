---
title: Enable Shards for TidbMonitor
summary: Learn how to use shards for TidbMonitor.
---

# Enable Shards for TidbMonitor

This document describes how to use shards for TidbMonitor.

## Shards

TidbMonitor collects monitoring data for a single TiDB cluster or multiple TiDB clusters. When the amount of monitoring data is large, the computing capacity of one TidbMonitor might hit a bottleneck. In this case, it is recommended to use shards of Prometheus [Modulus](https://prometheus.io/docs/prometheus/latest/configuration/configuration/). This feature performs `hashmod` on `__address__` to divide the monitoring data of multiple targets (`Targets`) into multiple TidbMonitor Pods.

To use shards for TidbMonitor, you need a data aggregation plan. The [Thanos](https://thanos.io/tip/thanos/design.md/) method is recommended.

## Enable shards

To enable shards for TidbMonitor, you need to specify the `shards` field. For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: monitor
spec:
  replicas: 1
  shards: 2
  clusters:
    - name: basic
  prometheus:
    baseImage: prom/prometheus
    version: v2.27.1
  initializer:
    baseImage: pingcap/tidb-monitor-initializer
    version: v5.2.1
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  imagePullPolicy: IfNotPresent
```

> **Note:**
>
> - The number of Pods corresponding to TidbMonitor is the product of `replicas` and `shards`. For example, when `replicas` is `1` and `shards` is `2`, TiDB Operator creates 2 TidbMonitor Pods.
> - After `shards` is changed, `Targets` are reallocated. However, the monitoring data already stored on the Pods is not reallocated.

For details on the configuration, refer to [shards example](https://github.com/pingcap/tidb-operator/tree/master/examples/monitor-shards).
