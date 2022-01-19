---
title: 升级 Kubernetes 上的 TiDB 集群
summary: 介绍如何升级 Kubernetes 上的 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/upgrade-a-tidb-cluster/']
---

# 升级 Kubernetes 上的 TiDB 集群

如果你使用 TiDB Operator 部署管理 Kubernetes 上的 TiDB 集群，可以通过滚动更新来升级 TiDB 集群的版本，减少对业务的影响。本文介绍如何使用滚动更新来升级 Kubernetes 上的 TiDB 集群。

## 滚动更新功能介绍

Kubernetes 提供了[滚动更新功能](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)，在不影响应用可用性的前提下执行更新。

使用滚动更新时，TiDB Operator 会按 PD、TiKV、TiDB 的顺序，串行地删除旧版本的 Pod，并创建新版本的 Pod。当新版本的 Pod 正常运行后，再处理下一个 Pod。

滚动更新中，TiDB Operator 会自动处理 PD 和 TiKV 的 Leader 迁移。因此，在多节点的部署拓扑下（最小环境：PD \* 3、TiKV \* 3、TiDB \* 2），滚动更新 TiKV、PD 不会影响业务正常运行。对于有连接重试功能的客户端，滚动更新 TiDB 同样不会影响业务。

> **警告：**
>
> 对于无法进行连接重试的客户端，**滚动更新 TiDB 会导致连接到被关闭节点的数据库的连接失效**，造成部分业务请求失败。对于这类业务，推荐在客户端添加重试功能，或者在低峰期进行 TiDB 的滚动更新操作。

## 升级步骤

> **注意：**
>
> TiDB（v4.0.2 起）默认会定期收集使用情况信息，并将这些信息分享给 PingCAP 用于改善产品。若要了解所收集的信息详情及如何禁用该行为，请参见[遥测](https://docs.pingcap.com/zh/tidb/stable/telemetry)。

1. 在 TidbCluster CR 中，修改待升级集群的各组件的镜像配置：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

    正常情况下，集群内的各组件应该使用相同版本，所以一般修改 `spec.version` 即可。如果要为集群内不同组件设置不同的版本，可以修改 `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`。

    `version` 字段格式如下：

    - `spec.version`，格式为 `imageTag`，例如 `v5.3`。
    - `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`，格式为 `imageTag`，例如 `v3.1.0`。

2. 查看升级进度：

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    当所有 Pod 都重建完毕进入 `Running` 状态后，升级完成。

> **注意：**
>
> 如果需要升级到企业版，需要将 `spec.<tidb/pd/tikv/tiflash/ticdc/pump>.baseImage` 配置为企业版镜像，格式为 `pingcap/<tidb/pd/tikv/tiflash/ticdc/tidb-binlog>-enterprise`。
>
> 例如将 `spec.pd.baseImage` 从 `pingcap/pd` 修改为 `pingcap/pd-enterprise`。

## 升级故障排除

如果因为 PD 配置错误、PD 镜像 tag 错误、NodeAffinity 等原因，导致 PD 集群不可用，此时无法成功升级 TiDB 集群版本。这种情况下，可使用 `force-upgrade` 强制升级集群以恢复集群功能。

强制升级的步骤如下：

1. 为集群设置 annotation：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl annotate --overwrite tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade=true
    ```

2. 修改 PD 相关配置，确保 PD 进入正常状态。

3. 修复 PD 配置后，**必须**执行以下命令，禁用强制升级功能，否则下次升级过程可能会出现异常：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade-
    ```

完成上述步骤后，TiDB 集群功能将恢复正常，可以正常进行升级。
