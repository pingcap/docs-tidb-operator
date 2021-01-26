---
title: Aggregate Monitoring Data of Multiple TiDB Clusters
summary: Learn how to aggregate monitoring data of multiple TiDB clusters by Thanos query.
---

# Aggregate Monitoring Data of Multiple TiDB Clusters

This document describes how to aggregate the monitoring data of multiple TiDB clusters by Thanos to solve the centralization problem of monitoring data of multiple clusters.

## Thanos

[Thanos](https://thanos.io/design.md/) is a high availability solution for Prometheus to simplify the availability guarantee of Prometheus.

Thanos provides [Thanos Query](https://thanos.io/components/query.md/) component as a unified query solution across Prometheus. You can use this feature to solve the problem of aggregating multiple clusters monitoring data.

## Configure Thanos Query

First, you need to configure a Thanos Sidecar container for each TidbMonitor. To update TidbMonitor, configure Thanos Sidecar and deploy Thanos Query component, refer to [Example](https://github.com/pingcap/tidb-operator/tree/master/examples/monitor-with-thanos/README.md).In Thanos Query, a Prometheus corresponds to a Store, which corresponds to a TidbMonitor. After deploying Thanos Query, you can provide a unified query interface for monitoring data through Thanos Query's API.

## Configure Grafana

After deploying Thanos Query, Grafana only needs to change the DataSource into the Thanos source to query the monitoring data of multiple TidbMonitors.

## Add or reduce TidbMonitor

If you need to update or offline TidbMonitor, update the starting configuration `--store` of Thanos Query Store, and perform a rolling update to Thanos Query component.

## Configure archives and storage of Thanos Sidecar

Thanos Sidecar supports replicating monitoring data to S3 remote storage, the configuration is as follows:

TidbMonitor CR configuration is as follows:

```yaml
spec:
  thanos:
    baseImage: thanosio/thanos
    version: v0.17.2
    objectStorageConfig:
      key: objectstorage.yaml
      name: thanos-objectstorage
```

Meanwhile, you need to create a Secret. The example is as follows:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: thanos-objectstorage
type: Opaque
stringData:
  objectstorage.yaml: |
    type: S3
    config:
      bucket: "xxxxxx"
      endpoint: "xxxx"
      region: ""
      access_key: "xxxx"
      insecure: true
      signature_version2: true
      secret_key: "xxxx"
      put_user_metadata: {}
      http_config:
        idle_conn_timeout: 90s
        response_header_timeout: 2m
      trace:
        enable: true
      part_size: 41943040
```
