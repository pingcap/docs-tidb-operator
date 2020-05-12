---
title: Kubernetes 上的 TiDB 集群扩缩容
summary: 介绍如何在 Kubernetes 中对 TiDB 集群扩缩容。
category: how-to
---

# Kubernetes 上的 TiDB 集群扩缩容

本文介绍 TiDB 在 Kubernetes 中如何进行水平扩缩容和垂直扩缩容。

## 水平扩缩容

TiDB 水平扩缩容操作指的是通过增加或减少节点的数量，来达到集群扩缩容的目的。扩缩容 TiDB 集群时，会按照填入的 replicas 值，对 PD、TiKV、TiDB 进行顺序扩缩容操作。扩容操作按照节点编号由小到大增加节点，缩容操作按照节点编号由大到小删除节点。目前 TiDB 集群有通过 Helm 与使用 TidbCluster Custom Resource (CR) 两种管理方式，你可以根据 TiDB 集群的管理方式选择对应的方式进行伸缩。

### 水平扩缩容操作 (CR)

#### 扩缩容 PD、TiDB、TiKV

使用 kubectl 修改集群所对应的 `TidbCluster` 对象中的 `spec.pd.replicas`、`spec.tidb.replicas`、`spec.tikv.replicas` 至期望值。

#### 扩容 TiFlash

如果集群中部署了 TiFlash，可以通过修改 `spec.tiflash.replicas` 对 TiFlash 进行扩容。

#### 缩容 TiFlash

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
    alter table <db-name>.<table-name> set tiflash replica 0;
    ```

5. 等待相关表的 TiFlash 副本被删除。

    连接到 TiDB 服务，执行如下命令，查不到相关表的同步信息时即为副本被删除：

    {{< copyable "sql" >}}

    ```sql
    SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>';
    ```
    
6. 修改 `spec.tiflash.replicas` 对 TiFlash 进行缩容。

### 水平扩缩容操作 (Helm)

1. 修改集群的 `value.yaml` 文件中的 `pd.replicas`、`tidb.replicas`、`tikv.replicas` 至期望值。

2. 执行 `helm upgrade` 命令进行扩缩容：

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade ${release_name} pingcap/tidb-cluster -f values.yaml --version=${chart_version}
    ```

### 查看集群水平扩缩容状态

{{< copyable "shell-regular" >}}

```shell
watch kubectl -n ${namespace} get pod -o wide
```

当所有组件的 Pod 数量都达到了预设值，并且都进入 `Running` 状态后，水平扩缩容完成。

> **注意：**
>
> - PD、TiKV、TiFlash 组件在滚动升级的过程中不会触发扩缩容操作。
> - TiKV 组件在缩容过程中，TiDB Operator 会调用 PD 接口将对应 TiKV 标记为下线，然后将其上数据迁移到其它 TiKV 节点，在数据迁移期间 TiKV Pod 依然是 `Running` 状态，数据迁移完成后对应 Pod 才会被删除，缩容时间与待缩容的 TiKV 上的数据量有关，可以通过 `kubectl get tidbcluster -n ${namespace} ${release_name} -o json | jq '.status.tikv.stores'` 查看 TiKV 是否处于下线 `Offline` 状态。
> - TiKV 组件不支持在缩容过程中进行扩容操作，强制执行此操作可能导致集群状态异常。假如异常已经发生，可以参考 [TiKV Store 异常进入 Tombstone 状态](troubleshoot.md#tikv-store-异常进入-tombstone-状态) 进行解决。
> - TiFlash 组件缩容处理逻辑和 TiKV 组件相同。
> - PD、TiKV、TiFlash 组件在缩容过程中被删除的节点的 PVC 会保留，并且由于 PV 的 `Reclaim Policy` 设置为 `Retain`，即使 PVC 被删除，数据依然可以找回。

## 垂直扩缩容

垂直扩缩容操作指的是通过增加或减少节点的资源限制，来达到集群扩缩容的目的。垂直扩缩容本质上是节点滚动升级的过程。目前 TiDB 集群有通过 Helm 与使用 TidbCluster Custom Resource (CR) 两种管理方式，你可以根据 TiDB 集群的管理方式选择对应的方式进行伸缩。

### 垂直扩缩容操作 (CR)

通过 kubectl 修改集群所对应的 `TidbCluster` 对象的 `spec.pd.resources`、`spec.tikv.resources`、`spec.tidb.resources` 至期望值。
如果集群中部署了 TiFlash，可以通过修改 `spec.tiflash.resources` 对 TiFlash 进行垂直扩缩容。

### 垂直扩缩容操作 (Helm)

1. 修改 `values.yaml` 文件中的 `tidb.resources`、`tikv.resources`、`pd.resources` 至期望值。

2. 执行 `helm upgrade` 命令进行升级：

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade ${release_name} pingcap/tidb-cluster -f values.yaml --version=${chart_version}
    ```

### 查看升级进度

{{< copyable "shell-regular" >}}

```shell
watch kubectl -n ${namespace} get pod -o wide
```

当所有 Pod 都重建完毕进入 `Running` 状态后，垂直扩缩容完成。

> **注意：**
>
> - 如果在垂直扩容时修改了资源的 `requests` 字段，并且 PD、TiKV、TiFlash 使用了 `Local PV`，那升级后 Pod 还会调度回原节点，如果原节点资源不够，则会导致 Pod 一直处于 `Pending` 状态而影响服务。
> - TiDB 作为一个可水平扩展的数据库，推荐通过增加节点个数发挥 TiDB 集群可水平扩展的优势，而不是类似传统数据库升级节点硬件配置来实现垂直扩容。
