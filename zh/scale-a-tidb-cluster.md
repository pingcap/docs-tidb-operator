---
title: 手动扩缩容 Kubernetes 上的 TiDB 集群
summary: 了解如何在 Kubernetes 上对 TiDB 集群手动扩缩容。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/scale-a-tidb-cluster/']
---

# 手动扩缩容 Kubernetes 上的 TiDB 集群

本文介绍如何对部署在 Kubernetes 上的 TiDB 集群进行手动水平扩缩容和垂直扩缩容。

## 水平扩缩容

TiDB 水平扩缩容操作指的是通过增加或减少 Pod 的数量，来达到集群扩缩容的目的。扩缩容 TiDB 集群时，会按照填入的 replicas 值，对 PD、TiKV、TiDB 按顺序进行扩缩容操作。

* 如果要进行扩容操作，可将某个组件的 replicas 值**调大**。扩容操作会按照 Pod 编号由小到大增加组件 Pod，直到 Pod 数量与 replicas 值相等。
* 如果要进行缩容操作，可将某个组件的 replicas 值**调小**。缩容操作会按照 Pod 编号由大到小删除组件 Pod，直到 Pod 数量与 replicas 值相等。

### 扩缩容 PD、TiDB、TiKV

如果要对 PD、TiDB、TiKV 进行水平扩缩容，可以使用 kubectl 修改集群所对应的 `TidbCluster` 对象中的 `spec.pd.replicas`、`spec.tidb.replicas`、`spec.tikv.replicas` 至期望值。

例如，执行以下命令可将 PD 的 replicas 值设置为 3：

{{< copyable "shell-regular" >}}

```shell
kubectl patch -n ${namespace} tc ${cluster_name} --type merge --patch '{"spec":{"pd":{"replicas":3}}}'
```

你可以通过以下命令查看 Kubernetes 集群中对应的 TiDB 集群是否更新到了你的期望定义。

{{< copyable "shell-regular" >}}

```shell
kubectl get tidbcluster ${cluster_name} -n ${namespace} -oyaml
```

如果上述命令输出的 `TidbCluster` 中，`spec.pd.replicas`、`spec.tidb.replicas`、`spec.tikv.replicas` 的值和你之前更新的值一致，那么可以通过以下命令来观察 `TidbCluster` Pod 是否新增或者减少。PD 和 TiDB 通常需要 10 到 30 秒左右的时间进行扩容或者缩容。TiKV 组件由于涉及到数据搬迁，通常需要 3 到 5 分钟来进行扩容或者缩容。

{{< copyable "shell-regular" >}}

```shell
watch kubectl -n ${namespace} get pod -o wide
```

### 扩缩容 TiFlash

如果要对 TiFlash 进行水平扩容，可以通过修改 `spec.tiflash.replicas` 来实现。例如，执行以下命令可将 TiFlash 的 replicas 值设置为 3：

{{< copyable "shell-regular" >}}

```shell
kubectl patch -n ${namespace} tc ${cluster_name} --type merge --patch '{"spec":{"tiflash":{"replicas":3}}'
```

如果要对 TiFlash 进行水平缩容，执行以下步骤：

1. 通过 `port-forward` 暴露 PD 服务：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl port-forward -n ${namespace} svc/${cluster_name}-pd 2379:2379
    ```

2. 打开一个**新**终端标签或窗口，通过如下命令确认开启 TiFlash 的所有数据表的最大副本数 N：

    {{< copyable "shell-regular" >}}

    ```shell
    curl 127.0.0.1:2379/pd/api/v1/config/rules/group/tiflash | grep count
    ```

    输出结果中 `count` 的最大值就是所有数据表的最大副本数 N。

3. 回到 `port-forward` 命令所在窗口，按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停止 `port-forward`。

4. 如果缩容 TiFlash 后，TiFlash 集群剩余 Pod 数大于等于所有数据表的最大副本数 N，直接进行下面第 6 步。如果缩容 TiFlash 后，TiFlash 集群剩余 Pod 数小于所有数据表的最大副本数 N，参考[访问 TiDB 集群](access-tidb.md)的步骤连接到 TiDB 服务，并针对所有副本数大于集群剩余 TiFlash Pod 数的表执行如下命令：

    {{< copyable "sql" >}}

    ```sql
    alter table <db_name>.<table_name> set tiflash replica 0;
    ```

5. 等待并确认相关表的 TiFlash 副本被删除。

    连接到 TiDB 服务，执行如下命令，查不到相关表的同步信息时即为副本被删除：

    {{< copyable "sql" >}}

    ```sql
    SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>';
    ```

6. 修改 `spec.tiflash.replicas` 对 TiFlash 进行缩容。

    你可以通过以下命令查看 Kubernetes 集群中对应的 TiDB 集群中的 TiFlash 是否更新到了你的期望定义。检查以下命令输出内容中，`spec.tiflash.replicas` 的值是否符合预期值。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get tidbcluster ${cluster-name} -n ${namespace} -oyaml
    ```

### 扩缩容 TiCDC

如果集群中部署了 TiCDC，可以通过修改 `spec.ticdc.replicas` 对 TiCDC 进行扩缩容。例如，执行以下命令可将 TiCDC 的 replicas 值设置为 3：

{{< copyable "shell-regular" >}}

```shell
kubectl patch -n ${namespace} tc ${cluster_name} --type merge --patch '{"spec":{"ticdc":{"replicas":3}}'
```

### 查看集群水平扩缩容状态

{{< copyable "shell-regular" >}}

```shell
watch kubectl -n ${namespace} get pod -o wide
```

当所有组件的 Pod 数量都达到了预设值，并且都进入 `Running` 状态后，水平扩缩容完成。

> **注意：**
>
> - PD、TiKV、TiFlash 组件在扩缩容的过程中不会触发滚动升级操作。
> - TiKV 组件在缩容过程中，TiDB Operator 会调用 PD 接口将对应 TiKV 标记为下线，然后将其上数据迁移到其它 TiKV 节点，在数据迁移期间 TiKV Pod 依然是 `Running` 状态，数据迁移完成后对应 Pod 才会被删除，缩容时间与待缩容的 TiKV 上的数据量有关，可以通过 `kubectl get -n ${namespace} tidbcluster ${cluster_name} -o json | jq '.status.tikv.stores'` 查看 TiKV 是否处于下线 `Offline` 状态。
> - 当 TiKV UP 状态的 store 数量 <= PD 配置中 `MaxReplicas` 的参数值时，无法缩容 TiKV 组件。
> - TiKV 组件不支持在缩容过程中进行扩容操作，强制执行此操作可能导致集群状态异常。假如异常已经发生，可以参考 [TiKV Store 异常进入 Tombstone 状态](exceptions.md#tikv-store-异常进入-tombstone-状态) 进行解决。
> - TiFlash 组件缩容处理逻辑和 TiKV 组件相同。
> - PD、TiKV、TiFlash 组件在缩容过程中被删除的节点的 PVC 会保留，并且由于 PV 的 `Reclaim Policy` 设置为 `Retain`，即使 PVC 被删除，数据依然可以找回。

## 垂直扩缩容

垂直扩缩容操作指的是通过增加或减少节点的资源限制，来达到集群扩缩容的目的。垂直扩缩容本质上是节点滚动升级的过程。目前 TiDB 集群使用 TidbCluster Custom Resource (CR) 管理方式。

### 垂直扩缩容操作

如果要对 PD、TiDB、TiKV 进行垂直扩缩容，通过 kubectl 修改集群所对应的 `TidbCluster` 对象的 `spec.pd.resources`、`spec.tikv.resources`、`spec.tidb.resources` 至期望值。

如果集群中部署了 TiFlash，可以通过修改 `spec.tiflash.resources` 对 TiFlash 进行垂直扩缩容。

如果集群中部署了 TiCDC，可以通过修改 `spec.ticdc.resources` 对 TiCDC 进行垂直扩缩容。

### 查看垂直扩缩容进度

{{< copyable "shell-regular" >}}

```shell
watch kubectl -n ${namespace} get pod -o wide
```

当所有 Pod 都重建完毕进入 `Running` 状态后，垂直扩缩容完成。

> **注意：**
>
> - 如果在垂直扩容时修改了资源的 `requests` 字段，并且 PD、TiKV、TiFlash 使用了 `Local PV`，那升级后 Pod 还会调度回原节点，如果原节点资源不够，则会导致 Pod 一直处于 `Pending` 状态而影响服务。
> - TiDB 是一个可水平扩展的数据库，推荐通过增加节点个数发挥 TiDB 集群可水平扩展的优势，而不是类似传统数据库升级节点硬件配置来实现垂直扩容。

## 扩缩容故障诊断

无论是水平扩缩容、或者是垂直扩缩容，都可能遇到资源不够时造成 Pod 出现 Pending 的情况。可以参考 [Pod 处于 Pending 状态](deploy-failures.md#pod-处于-pending-状态)。
