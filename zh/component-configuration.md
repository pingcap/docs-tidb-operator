---
title: 组件配置
summary: 介绍如何配置 Kubernetes 集群上 TiDB、TiKV、PD、TiProxy、TiFlash、TiCDC 等组件的配置参数。
---

# 组件配置

本文档介绍如何配置 TiDB、TiKV、PD、TiProxy、TiFlash、TiCDC 等组件的配置参数。

TiDB Operator 支持两种配置更新策略：

- `Restart`（默认值）：更新配置时，自动滚动重启相关组件，使配置生效。
- `HotReload`：更新配置后组件不重启，由组件自动应用新配置，或由用户手动触发滚动更新。

你可以通过 CR 资源（如 TiDBGroup、TiKVGroup、PDGroup、TiProxyGroup、TiFlashGroup、TiCDCGroup）中的 `spec.template.spec.updateStrategy.config` 字段设置配置更新策略。

## 配置 TiDB 配置参数

你可以通过 TiDBGroup CR 的 `spec.template.spec.config` 来配置 TiDB 配置参数。

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

获取所有可以配置的 TiDB 配置参数，请参考 [TiDB 配置文档](https://docs.pingcap.com/zh/tidb/stable/tidb-configuration-file)。

## 配置 TiKV 配置参数

你可以通过 TiKVGroup CR 的 `spec.template.spec.config` 来配置 TiKV 配置参数。

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

获取所有可以配置的 TiKV 配置参数，请参考 [TiKV 配置文档](https://docs.pingcap.com/zh/tidb/stable/tikv-configuration-file)。

> **注意：**
>
> TiKV 的 RocksDB 日志默认存储在 `/var/lib/tikv` 数据目录，建议配置 `max-days` 和 `max-backups` 来自动清理日志文件。

## 配置 PD 配置参数

你可以通过 PDGroup CR 的 `spec.template.spec.config` 来配置 PD 配置参数。

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

获取所有可以配置的 PD 配置参数，请参考 [PD 配置文档](https://docs.pingcap.com/zh/tidb/stable/pd-configuration-file)。

> **注意：**
>
> PD 部分配置项在首次启动成功后会持久化到 etcd 中且后续将以 etcd 中的配置为准。因此 PD 在首次启动后，这些配置项将无法再通过配置参数来进行修改，而需要使用 [SQL](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-pd-配置)、[pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules) 或 PD server API 来动态进行修改。目前，[在线修改 PD 配置](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-pd-配置)文档中所列的配置项中，除 `log.level` 外，其他配置项在 PD 首次启动之后均不再支持通过配置参数进行修改。

### 配置 PD 微服务

> **注意：**
>
> - PD 从 v8.0.0 版本开始支持[微服务模式](https://docs.pingcap.com/zh/tidb/dev/pd-microservices)。
> - 目前只支持在创建时开启 PD 微服务模式，后续无法再修改该字段。

你可以通过设置 PDGroup CR 的 `spec.template.spec.mode` 为 `"ms"` 来开启 PD 微服务模式：

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

目前 PD 支持 `tso` 和 `scheduling` 这两个微服务，你可以通过 TSOGroup 和 SchedulingGroup CR 的 `spec.template.spec.config` 来配置 PD 微服务参数。

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

要获取 PD 微服务可配置的所有参数，请参考 [PD 配置文件描述](https://docs.pingcap.com/zh/tidb/stable/pd-configuration-file)。

> **注意：**
>
> - 如果在部署 TiDB 集群时就启用了 PD 微服务模式，PD 微服务的部分配置项会持久化到 etcd 中且后续将以 etcd 中的配置为准。
> - 因此，PD 微服务在首次启动后，这些配置项将无法再通过配置参数来进行修改，而需要使用 [SQL](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-pd-配置)、[pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules) 或 PD server API 来动态进行修改。目前，[在线修改 PD 配置](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-pd-配置)文档中所列的配置项中，除 `log.level` 外，其他配置项在 PD 微服务首次启动之后均不再支持通过配置参数进行修改。

## 配置 TiProxy 配置参数

你可以通过 TiProxyGroup CR 的 `spec.template.spec.config` 来配置 TiProxy 配置参数。

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

获取所有可以配置的 TiProxy 配置参数，请参考 [TiProxy 配置文档](https://docs.pingcap.com/zh/tidb/stable/tiproxy-configuration)。

## 配置 TiFlash 配置参数

你可以通过 TiFlashGroup CR 的 `spec.template.spec.config` 来配置 TiFlash 配置参数。

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

获取所有可以配置的 TiFlash 配置参数，请参考 [TiFlash 配置文档](https://docs.pingcap.com/zh/tidb/stable/tiflash-configuration)。

## 配置 TiCDC 启动参数

你可以通过 TiCDCGroup CR 的 `spec.template.spec.config` 来配置 TiCDC 启动参数。

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

获取所有可以配置的 TiCDC 启动参数，请参考 [TiCDC 启动参数文档](https://github.com/pingcap/tiflow/blob/bf29e42c75ae08ce74fbba102fe78a0018c9d2ea/pkg/cmd/util/ticdc.toml)。
