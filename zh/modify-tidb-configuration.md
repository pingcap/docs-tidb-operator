---
title: 修改 TiDB 集群配置
summary: 了解如何修改部署在 Kubernetes 上的 TiDB 的集群配置。
---

# 修改 TiDB 集群配置

TiDB 集群自身支持通过 SQL 对 TiDB、TiKV、PD 等组件进行[在线配置变更](https://docs.pingcap.com/zh/tidb/stable/dynamic-config)，无需重启集群组件。但是，对于部署在 Kubernetes 中的 TiDB 集群，部分组件在升级或者重启后，配置项会被 TidbCluster CR 中的配置项覆盖，导致在线变更的配置失效。

本文介绍如何修改部署在 Kubernetes 上的 TiDB 的集群配置，避免重启或升级导致配置失效。由于 PD 的特殊性，需要分别对 PD 和其他组件进行配置。

## 修改 TiDB/TiKV 等组件配置

对于 TiDB 和 TiKV，如果通过 SQL 进行[在线配置变更](https://docs.pingcap.com/zh/tidb/stable/dynamic-config)，在升级或者重启后，配置项会被 TidbCluster CR 中的配置项覆盖，导致在线变更的配置失效。因此，如果需要持久化修改配置，你需要在 TidbCluster CR 中直接修改配置项。

对于 TiFlash、TiCDC 和 Pump，目前只能通过在 TidbCluster CR 中修改配置项。

在 TidbCluster CR 中修改配置项的步骤如下：

1. 参考[配置 TiDB 组件](configure-a-tidb-cluster.md#配置-tidb-组件)中的参数，修改集群的 TidbCluster CR 中各组件配置：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. 查看配置修改后的更新进度：

    {{< copyable "shell-regular" >}}

    ```bash
    watch kubectl -n ${namespace} get pod -o wide
    ```

    当所有 Pod 都重建完毕进入 `Running` 状态后，配置修改完成。

## 修改 PD 组件配置

在 PD 首次启动成功后，PD 的部分配置项会持久化到 etcd 中，且后续将以 etcd 中的配置为准。因此，在 PD 首次启动后，这些配置项将无法再通过 TidbCluster CR 来进行修改。

PD 中[支持在线修改的配置项](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-pd-配置)里，除 `log.level` 外，其他配置项在 PD 首次启动之后均不再支持通过 TidbCluster CR 进行修改。

对于部署在 Kubernetes 中的 TiDB 集群，如需修改 PD 配置参数，需要使用 [SQL](https://docs.pingcap.com/zh/tidb/stable/dynamic-config/#在线修改-pd-配置)、[pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules) 或 PD server API 来动态进行修改。
