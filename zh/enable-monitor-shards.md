---
title: TidbMonitor 分片功能
summary: 如何使用 TidbMonitor 分片功能
---

# 开启 TidbMonitor 分片功能

本文档介绍如何使用 TidbMonitor 分片功能。

## 功能介绍

TidbMonitor 负责单个或者多个 TiDB 集群的监控数据采集。当监控数据量很大的时候，单点计算能力会达到瓶颈。可以采用 Prometheus [Modulus](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) 分片功能，对 `__address__` 做 `hashmod`，打散 `Targets` 到多个 TidbMonitor 节点上。

这种方式需要支持数据聚合方案，我们推荐采用 [Thanos](https://thanos.io/tip/thanos/design.md/) 方案。

## 如何开启分片功能

开启分片功能，需要指定 `shard` 字段，示例如下:

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

> **注意：**
>
> Pod 数量取决于 replica 和 shard 的乘积。当 replica 为 2 个副本，shard 为 2 个分片，就会产生四个 TidbMonitor Pod实例。
> shard 变更后，Targets 会重新分配，但是原本在节点上的监控数据不会重新分配。

可以参考 [Example](https://github.com/pingcap/tidb-operator/tree/master/examples/monitor-shards)。
