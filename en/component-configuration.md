---
title: Component Configuration
summary: Learn how to configure parameters for components such as TiDB, TiKV, PD, TiProxy, TiFlash, and TiCDC in a Kubernetes cluster.
---

# Component Configuration

This document describes how to configure parameters for TiDB, TiKV, PD, TiProxy, TiFlash, and TiCDC in a Kubernetes cluster.

By default, TiDB Operator applies configuration changes by performing a rolling restart of the related components.

## Configure TiDB parameters

You can configure TiDB parameters using the `spec.template.spec.config` field in the `TiDBGroup` CR.

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: tidb
spec:
  template:
    spec:
      config: |
        split-table = true
        oom-action = "log"
```

For a full list of configurable TiDB parameters, see [TiDB Configuration File](https://docs.pingcap.com/tidb/stable/tidb-configuration-file).

## Configure TiKV parameters

You can configure TiKV parameters using the `spec.template.spec.config` field in the `TiKVGroup` CR.

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiKVGroup
metadata:
  name: tikv
spec:
  template:
    spec:
      config: |
        [storage]
          [storage.block-cache]
            capacity = "16GB"
        [log.file]
          max-days = 30
          max-backups = 30
```

For a full list of configurable TiKV parameters, see [TiKV Configuration File](https://docs.pingcap.com/tidb/stable/tikv-configuration-file).

> **Note:**
>
> The RocksDB logs of TiKV are stored in the `/var/lib/tikv` data directory by default. It is recommended to configure `max-days` and `max-backups` to automatically clean up log files.

## Configure PD parameters

You can configure PD parameters using the `spec.template.spec.config` field in the `PDGroup` CR.

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
spec:
  template:
    spec:
      config: |
        lease = 3
        enable-prevote = true
```

For a full list of configurable PD parameters, see [PD Configuration File](https://docs.pingcap.com/tidb/stable/pd-configuration-file).

> **Note:**
>
> After the cluster is started for the first time, some PD configuration items are persisted in etcd. The persisted configuration in etcd takes precedence over that in PD. Therefore, after the first start, you cannot modify some PD configuration using parameters. You need to dynamically modify the configuration using [SQL statements](https://docs.pingcap.com/tidb/stable/dynamic-config/#modify-pd-configuration-dynamically), [pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules), or PD server API. Currently, among all the configuration items listed in [Modify PD configuration online](https://docs.pingcap.com/tidb/stable/dynamic-config/#modify-configuration-dynamically), except `log.level`, all the other configuration items cannot be modified using parameters after the first start.

### Configure PD microservices

> **Note:**
>
> - Starting from v8.0.0, PD supports the [microservice mode](https://docs.pingcap.com/tidb/dev/pd-microservices).
> - PD microservice mode can only be enabled during initial deployment and cannot be changed afterward.

To enable PD microservice mode, set `spec.template.spec.mode` to `"ms"` in the `PDGroup` CR:

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
spec:
  template:
    spec:
      mode: "ms"
```

Currently, PD supports the `tso` and `scheduling` microservices. You can configure them using the `TSOGroup` and `SchedulingGroup` CRs.

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TSOGroup
metadata:
  name: tso
spec:
  template:
    spec:
      config: |
        [log.file]
          filename = "/pdms/log/tso.log"
---
apiVersion: core.pingcap.com/v1alpha1
kind: SchedulingGroup
metadata:
  name: scheduling
spec:
  template:
    spec:
      config: |
        [log.file]
          filename = "/pdms/log/scheduling.log"
```

To get complete configuration parameters for the PD microservice, `tso` microservice, and `scheduling` microservice, see the following documents:

- [PD Configuration File](https://docs.pingcap.com/tidb/stable/pd-configuration-file)
- [TSO Configuration File](https://docs.pingcap.com/tidb/stable/tso-configuration-file/)
- [Scheduling Configuration File](https://docs.pingcap.com/tidb/stable/scheduling-configuration-file/)

> **Note:**
>
> - If you enable the PD microservice mode when you deploy a TiDB cluster, some configuration items of PD microservices are persisted in etcd. The persisted configuration in etcd takes precedence over that in PD.
> - Hence, after the first startup of PD microservices, you cannot modify these configuration items using parameters. Instead, you can modify them dynamically using [SQL statements](https://docs.pingcap.com/tidb/stable/dynamic-config/#modify-pd-configuration-dynamically), [pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control/#config-show--set-option-value--placement-rules), or PD server API. Currently, among all the configuration items listed in [Modify PD configuration dynamically](https://docs.pingcap.com/tidb/stable/dynamic-config/#modify-pd-configuration-dynamically), except `log.level`, all the other configuration items cannot be modified using parameters after the first startup of PD microservices.

## Configure TiProxy parameters

You can configure TiProxy parameters using the `spec.template.spec.config` field in the `TiProxyGroup` CR.

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiProxyGroup
metadata:
  name: tiproxy
spec:
  template:
    spec:
      config: |
        [log]
          level = "info"
```

For a full list of configurable TiProxy parameters, see [TiProxy Configuration File](https://docs.pingcap.com/tidb/stable/tiproxy-configuration).

## Configure TiFlash parameters

You can configure TiFlash parameters using the `spec.template.spec.config` field in the `TiFlashGroup` CR.

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiFlashGroup
metadata:
  name: tiflash
spec:
  template:
    spec:
      config: |
        [flash]
          [flash.flash_cluster]
            log = "/data0/logs/flash_cluster_manager.log"
        [logger]
          count = 10
          level = "information"
          errorlog = "/data0/logs/error.log"
          log = "/data0/logs/server.log"
```

For a full list of configurable TiFlash parameters, see [TiFlash Configuration File](https://docs.pingcap.com/tidb/stable/tiflash-configuration).

## Configure TiCDC startup parameters

You can configure TiCDC startup parameters using the `spec.template.spec.config` field in the `TiCDCGroup` CR.

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiCDCGroup
metadata:
  name: ticdc
spec:
  template:
    spec:
      config: |
        gc-ttl = 86400
        log-level = "info"
```

For a full list of configurable TiCDC startup parameters, see [TiCDC Configuration File](https://github.com/pingcap/tiflow/blob/bf29e42c75ae08ce74fbba102fe78a0018c9d2ea/pkg/cmd/util/ticdc.toml).
