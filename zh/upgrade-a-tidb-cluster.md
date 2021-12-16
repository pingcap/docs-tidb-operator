---
title: 滚动升级 Kubernetes 上的 TiDB 集群
summary: 介绍如何滚动升级 Kubernetes 上的 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/upgrade-a-tidb-cluster/']
---

# 滚动升级 Kubernetes 上的 TiDB 集群

如果你使用 TiDB Operator 部署管理 Kubernetes 上的 TiDB 集群，你可以使用滚动升级功能来更新 TiDB 集群的版本。本文介绍如何滚动升级 Kubernetes 上的 TiDB 集群。

滚动升级功能适用于以下场景：

- [升级 TiDB 版本](#升级-tidb-版本)。
- 由于 PD 集群不可用，导致 TiDB 集群无法扩缩容、升级、更新配置时，可通过[强制升级 TiDB 集群](#强制升级-tidb-集群)以恢复功能。
- [修改 TiDB 集群配置](#修改-tidb-集群配置)。//TODO：需要补充场景信息

## 功能介绍

滚动升级 TiDB 集群时，TiDB Operator 会按 PD、TiKV、TiDB 的顺序，串行删除旧版本的 Pod，并创建新版本的 Pod。当新版本的 Pod 正常运行后，再处理下一个 Pod。

滚动升级中，TiDB Operator 会自动处理 PD 和 TiKV 的 Leader 迁移与 TiDB 的 DDL Owner 迁移。因此，在多节点的部署拓扑下（最小环境：PD \* 3、TiKV \* 3、TiDB \* 2），滚动更新 TiKV、PD 不会影响业务正常运行。

对于有连接重试功能的客户端，滚动更新 TiDB 同样不会影响业务。

> **Warning:**
>
> 对于无法进行连接重试的客户端，滚动更新 TiDB 则会导致连接到被关闭节点的数据库的连接失效，造成部分业务请求失败。对于这类业务，推荐在客户端添加重试功能，或者在低峰期进行 TiDB 的滚动升级操作。

## 升级 TiDB 版本

1. 在 TidbCluster CR 中，修改待升级集群的各组件的镜像配置：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

    正常情况下，集群内的各组件应该使用相同版本，所以一般修改 `spec.version` 即可。如果要为集群内不同组件设置不同的版本，可以修改 `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`。

    `version` 字段格式如下：

    - `spec.version`，格式为 `imageTag`，例如 `v5.2.1`。
    - `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`，格式为 `imageTag`，例如 `v3.1.0`。

2. 查看升级进度：

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    当所有 Pod 都重建完毕进入 `Running` 状态后，升级完成。

> **注意：**
>
> 如果需要升级到企业版，需要将 `db.yaml` 中 `spec.<tidb/pd/tikv/tiflash/ticdc/pump>.baseImage` 配置为企业版镜像，格式为 `pingcap/<tidb/pd/tikv/tiflash/ticdc/tidb-binlog>-enterprise`。
>
> 例如将 `spec.pd.baseImage` 从 `pingcap/pd` 修改为 `pingcap/pd-enterprise`。

## 强制升级 TiDB 集群

如果因为 PD 配置错误、PD 镜像 tag 错误、NodeAffinity 等原因，导致 PD 集群不可用，此时 [TiDB 集群扩缩容](scale-a-tidb-cluster.md)、[升级 TiDB 版本](#升级-tidb-版本)和更新 TiDB 集群配置这三种操作都无法成功执行。

这种情况下，可使用 `force-upgrade` 强制升级集群以恢复集群功能。强制升级的步骤如下：

1. 为集群设置 `annotation`：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl annotate --overwrite tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade=true
    ```

2. 修改 PD 相关配置，确保 PD 进入正常状态。

> **警告：**
>
> PD 集群恢复后，**必须**执行下面命令禁用强制升级功能，否则下次升级过程可能会出现异常：
>
> {{< copyable "shell-regular" >}}
>
> ```shell
> kubectl annotate tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade-
> ```

## 修改 TiDB 集群配置

TiDB 集群支持通过 SQL 对各组件进行[在线配置变更](https://docs.pingcap.com/zh/tidb/stable/dynamic-config)，无需重启集群组件。但是，在滚动升级后，通过在线修改配置进行修改的配置项会被 CR 中的配置项覆盖。因此，你需要使用下面的方式修改配置：

1. 参考[配置 TiDB 组件](configure-a-tidb-cluster.md#配置-tidb-组件)，修改集群的 TidbCluster CR 中各组件配置：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

    > **注意：**
    >
    > 在首次启动成功后，PD 部分配置项会持久化到 etcd 中，且后续将以 etcd 中的配置为准。因此，在 PD 首次启动后，这些配置项将无法再通过配置参数来进行修改，而需要使用 SQL、pd-ctl 或 PD server API 来动态进行修改。目前，[在线修改 PD 配置](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-pd-配置)文档中所列的配置项中，除 `log.level` 外，其他配置项在 PD 首次启动之后均不再支持通过配置参数进行修改。

2. 查看配置修改后的更新进度：

    {{< copyable "shell-regular" >}}

    ```bash
    watch kubectl -n ${namespace} get pod -o wide
    ```

    当所有 Pod 都重建完毕进入 `Running` 状态后，配置修改完成。

> **注意：**
>
> TiDB（v4.0.2 起）默认会定期收集使用情况信息，并将这些信息分享给 PingCAP 用于改善产品。若要了解所收集的信息详情及如何禁用该行为，请参见[遥测](https://docs.pingcap.com/zh/tidb/stable/telemetry)。
