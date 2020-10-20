---
title: 滚动升级 Kubernetes 上的 TiDB 集群
summary: 介绍如何滚动升级 Kubernetes 上的 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/upgrade-a-tidb-cluster/']
---

# 滚动升级 Kubernetes 上的 TiDB 集群

滚动更新 TiDB 集群时，会按 PD、TiKV、TiDB 的顺序，串行删除 Pod，并创建新版本的 Pod，当新版本的 Pod 正常运行后，再处理下一个 Pod。

滚动升级过程会自动处理 PD、TiKV 的 Leader 迁移与 TiDB 的 DDL Owner 迁移。因此，在多节点的部署拓扑下（最小环境：PD \* 3、TiKV \* 3、TiDB \* 2），滚动更新 TiKV、PD 不会影响业务正常运行。

对于有连接重试功能的客户端，滚动更新 TiDB 同样不会影响业务。对于无法进行重试的客户端，滚动更新 TiDB 则会导致连接到被关闭节点的数据库连接失效，造成部分业务请求失败。对于这类业务，推荐在客户端添加重试功能或在低峰期进行 TiDB 的滚动升级操作。

滚动更新可以用于升级 TiDB 版本，也可以用于更新集群配置。

## 通过 TidbCluster CR 升级

如果 TiDB 集群是直接通过 TidbCluster CR 部署的或者通过 Helm 方式部署的然后又切换到了 TidbCluster CR 管理，可以通过下面步骤升级 TiDB 集群。

### 升级 TiDB 版本

1. 修改集群的 TidbCluster CR 中各组件的镜像配置。

    正常情况下，集群内的各组件应该使用相同版本，所以一般修改 `spec.version` 即可，如果要为集群内不同组件设置不同的版本，可以修改 `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`。

    `version` 字段格式如下：

    - `spec.version`，格式为 `imageTag`，例如 `v4.0.7`
    - `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`，格式为 `imageTag`，例如 `v3.1.0`

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. 查看升级进度：

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    当所有 Pod 都重建完毕进入 `Running` 状态后，升级完成。

> **注意：**
>
> 如果需要升级到企业版，需要将 db.yaml 中 `spec.<tidb/pd/tikv/tiflash/ticdc/pump>.baseImage` 配置为企业版镜像，格式为 `pingcap/<tidb/pd/tikv/tiflash/ticdc/tidb-binlog>-enterprise`。
>
> 例如将 `spec.pd.baseImage` 从 `pingcap/pd` 修改为 `pingcap/pd-enterprise`。

### 强制升级 TiDB 集群

如果 PD 集群因为 PD 配置错误、PD 镜像 tag 错误、NodeAffinity 等原因不可用，[TiDB 集群扩缩容](scale-a-tidb-cluster.md)、[升级 TiDB 版本](#升级-tidb-版本)和更新 TiDB 集群配置这三种操作都无法成功执行。

这种情况下，可使用 `force-upgrade` 强制升级集群以恢复集群功能。
首先为集群设置 `annotation`：

{{< copyable "shell-regular" >}}

```shell
kubectl annotate --overwrite tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade=true
```

然后修改 PD 相关配置，确保 PD 进入正常状态。

> **警告：**
>
> PD 集群恢复后，**必须**执行下面命令禁用强制升级功能，否则下次升级过程可能会出现异常：
>
> {{< copyable "shell-regular" >}}
>
> ```shell
> kubectl annotate tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade-
> ```

## 通过 Helm 升级

如果选择继续用 Helm 管理集群，可以参考下面步骤升级 TiDB 集群。

### 升级 TiDB 版本

1. 修改集群的 `values.yaml` 文件中的 `tidb.image`、`tikv.image`、`pd.image` 的值为新版本镜像；
2. 执行 `helm upgrade` 命令进行升级：

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade ${release_name} pingcap/tidb-cluster -f values.yaml --version=${chart_version}
    ```

3. 查看升级进度：

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    当所有 Pod 都重建完毕进入 `Running` 状态后，升级完成。

> **注意：**
>
> 如果需要升级到企业版，需要把 `<tidb/tikv/pd>.image` 的值改为企业版镜像。
>
> 例如将 `pd.image` 从 `pingcap/pd:v4.0.7` 修改为 `pingcap/pd-enterprise:v4.0.7`。

### 强制升级 TiDB 集群

如果 PD 集群因为 PD 配置错误、PD 镜像 tag 错误、NodeAffinity 等原因不可用，[TiDB 集群扩缩容](scale-a-tidb-cluster.md)、[升级 TiDB 版本](#升级-tidb-版本)和更新 TiDB 集群配置这三种操作都无法成功执行。

这种情况下，可使用 `force-upgrade`（TiDB Operator 版本 > v1.0.0-beta.3 ）强制升级集群以恢复集群功能。
首先为集群设置 `annotation`：

{{< copyable "shell-regular" >}}

```shell
kubectl annotate --overwrite tc ${release_name} -n ${namespace} tidb.pingcap.com/force-upgrade=true
```

然后执行对应操作中的 `helm upgrade` 命令：

{{< copyable "shell-regular" >}}

```shell
helm upgrade ${release_name} pingcap/tidb-cluster -f values.yaml --version=${chart_version}
```

> **警告：**
>
> PD 集群恢复后，**必须**执行下面命令禁用强制升级功能，否则下次升级过程可能会出现异常：
>
> {{< copyable "shell-regular" >}}
>
> ```shell
> kubectl annotate tc ${release_name} -n ${namespace} tidb.pingcap.com/force-upgrade-
> ```

> **注意：**
>
> TiDB（v4.0.2 起）默认会定期收集使用情况信息，并将这些信息分享给 PingCAP 用于改善产品。若要了解所收集的信息详情及如何禁用该行为，请参见[遥测](https://docs.pingcap.com/zh/tidb/stable/telemetry)。
