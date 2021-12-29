---
title: 对 Kubernetes 上的 TiDB 集群启用自动弹性伸缩
summary: 介绍如何对 Kubernetes 上的 TiDB 集群启用自动弹性伸缩。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/enable-tidb-cluster-auto-scaling/']
---

# 对 Kubernetes 上的 TiDB 集群启用自动弹性伸缩

Kubernetes 平台上有原生的弹性伸缩 API：[Horizontal Pod Autoscaler](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale/)。基于 Kubernetes，TiDB 自 v5.0 起支持了全新的弹性调度算法。相应地，在 TiDB Operator 1.2 及以上版本中，TiDB 集群可以凭借 Kubernetes 平台本身的特性支持开启弹性调度。本文介绍如何对 Kubernetes 上的 TiDB 集群开启和使用自动弹性伸缩。

> **警告：**
>
> * Kubernetes 上的 TiDB 集群弹性伸缩目前仍处于 Alpha 阶段，极其不推荐在关键、生产环境开启该特性。
> * 推荐在测试环境中体验该特性，并反馈相关的建议与问题，帮助我们更好地提高这一特性。
> * 目前仅支持基于 CPU 利用率的弹性伸缩。

## 开启弹性伸缩特性

TiDB Operator 的弹性伸缩特性默认关闭，要启用弹性伸缩特性，请执行以下步骤：

1. 修改 TiDB Operator 的 `values.yaml` 文件，在 `features` 选项中开启 `AutoScaling`。

    ```yaml
    features:
    - AutoScaling=true
    ```

2. 更新 TiDB Operator 使更改生效。

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade tidb-operator pingcap/tidb-operator --version=${chart_version} --namespace=tidb-admin -f ${HOME}/tidb-operator/values-tidb-operator.yaml
    ```

3. 确认目标 TiDB 集群资源设置。

    目标 TiDB 集群在使用弹性伸缩前，需要提前设置好对应组件的 CPU。以 TiKV 为例，你需要配置 `spec.tikv.requests.cpu`：

    ```yaml
    spec:
      tikv:
        requests:
          cpu: "1"
      tidb:
        requests:
          cpu: "1"
    ```

## 定义 TiDB 集群的弹性伸缩行为

你可以通过 `TidbClusterAutoScaler` CR 对象来控制 TiDB 集群的弹性伸缩行为。

示例如下：

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbClusterAutoScaler
metadata:
  name: auto-scaling-demo
spec:
  cluster:
    name: auto-scaling-demo
  tikv:
    resources:
      storage_small:
        cpu: 1000m
        memory: 2Gi
        storage: 10Gi
        count: 3
    rules:
      cpu:
        max_threshold: 0.8
        min_threshold: 0.2
        resource_types:
        - storage_small
    scaleInIntervalSeconds: 500
    scaleOutIntervalSeconds: 300
  tidb:
    resources:
      compute_small:
        cpu: 1000m
        memory: 2Gi
        count: 3
    rules:
      cpu:
        max_threshold: 0.8
        min_threshold: 0.2
        resource_types:
        - compute_small
```

### 原理介绍

TiDB Operator 会根据 `TidbClusterAutoScaler` CR 的配置，向 PD 发起请求，查询扩缩容结果，并根据 PD 返回的结果，利用[异构集群](deploy-heterogeneous-tidb-cluster.md)特性，创建、更新或者删除异构 TiDB 集群（只配置 TiDB 组件或者只配置 TiKV 组件），实现 TiDB 集群的弹性伸缩。

### 字段介绍

* `spec.cluster`：需要被弹性调度的 TiDB 集群。

    * `name`：TiDB 集群名称。
    * `namespace`：TiDB 集群所在的 namespace。如果没有配置 namespace，会默认设置为和 TidbClusterAutoScaler CR 相同的 namespace。

* `spec.tikv`：TiKV 弹性调度相关配置。
* `spec.tikv.resources`：TiKV 弹性调度可以选择的资源配置类型。如果没有配置，会默认设置为 `spec.cluster` 对应的 TidbCluster CR 中的 `spec.tikv.requests` 资源配置。

    * `cpu`：CPU 配置。
    * `memory`：内存配置。
    * `storage`：存储配置。
    * `count`：当前资源配置可以使用的数量，如果不配置，则认为没有限制。

* `spec.tikv.rules`：TiKV 弹性调度规则，目前只支持 CPU 规则。

    * `max_threshold`：所有 Pod CPU 平均利用率超过 `max_threshold` 会触发扩容操作。
    * `min_threshold`：所有 Pod CPU 平均利用率低于 `min_threshold` 会触发缩容操作。
    * `resource_types`：配置根据 CPU 规则弹性伸缩时可以使用的资源类型，对应 `spec.tikv.resources[]` 中的 `key`。如果没有配置，默认会设置为 `spec.tikv.resources[]` 中所有的 `key`。

* `spec.tikv.scaleInIntervalSeconds`：缩容距离上一次伸缩（扩容或者缩容）的冷却时间，如果没有配置，默认设置为 `500`，即 `500s`。
* `spec.tikv.scaleOutIntervalSeconds`：扩容距离上一次伸缩（扩容或者缩容）的冷却时间，如果没有配置，默认设置为 `300`，即 `300s`。
* `spec.tidb`：TiDB 弹性调度相关配置，下面的各个字段和 `spec.tikv` 一样。

更多配置字段可以参考 [API 文档](https://github.com/pingcap/tidb-operator/blob/master/docs/api-references/docs.md#basicautoscalerspec)。

## 演示示例

1. 执行以下命令在 Kubernetes 集群上快速安装一个 1 PD、3 TiKV、2 TiDB，并带有监控与弹性伸缩能力的 TiDB 集群。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/auto-scale/tidb-cluster.yaml -n ${namespace}
    ```

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/auto-scale/tidb-monitor.yaml -n ${namespace}
    ```

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/auto-scale/tidb-cluster-auto-scaler.yaml  -n ${namespace}
    ```

2. 使用 [sysbench](https://github.com/akopytov/sysbench) 工具准备数据。

    将以下内容复制到 `sysbench.config` 文件中：

    ```config
    mysql-host=${tidb_service_ip}
    mysql-port=4000
    mysql-user=root
    mysql-password=
    mysql-db=test
    time=120
    threads=20
    report-interval=5
    db-driver=mysql
    ```

    通过以下命令准备数据：

    {{< copyable "shell-regular" >}}

    ```shell
    sysbench --config-file=${path}/sysbench.config oltp_point_select --tables=1 --table-size=20000 prepare
    ```

3. 通过以下命令开始进行压测：

    {{< copyable "shell-regular" >}}

    ```shell
    sysbench --config-file=${path}/sysbench.config oltp_point_select --tables=1 --table-size=20000 run
    ```

    上述命令执行完毕后，出现如下输出：

    ```sh
    Initializing worker threads...

    Threads started!

    [ 5s ] thds: 20 tps: 37686.35 qps: 37686.35 (r/w/o: 37686.35/0.00/0.00) lat (ms,95%): 0.99 err/s: 0.00 reconn/s: 0.00
    [ 10s ] thds: 20 tps: 38487.20 qps: 38487.20 (r/w/o: 38487.20/0.00/0.00) lat (ms,95%): 0.95 err/s: 0.00 reconn/s: 0.00
    ```

4. 新建一个会话终端，通过以下命令观察 TiDB 集群的 Pod 变化情况。

    {{< copyable "shell-regular" >}}

    ```shell
    watch -n1 "kubectl -n ${namespace} get pod"
    ```

    出现如下输出:

    ```sh
    auto-scaling-demo-discovery-fbd95b679-f4cb9   1/1     Running   0          17m
    auto-scaling-demo-monitor-6857c58564-ftkp4    3/3     Running   0          17m
    auto-scaling-demo-pd-0                        1/1     Running   0          17m
    auto-scaling-demo-tidb-0                      2/2     Running   0          15m
    auto-scaling-demo-tidb-1                      2/2     Running   0          15m
    auto-scaling-demo-tikv-0                      1/1     Running   0          15m
    auto-scaling-demo-tikv-1                      1/1     Running   0          15m
    auto-scaling-demo-tikv-2                      1/1     Running   0          15m
    ```

    观察 Pod 的变化情况和 sysbench 的 TPS 与 QPS，当 TiKV 与 TiDB Pod 新增时，sysbench 的 TPS 与 QPS 值有显著提升。当 sysbench 结束后，观察 Pod 变化情况，发现新增的 TiKV 与 TiDB Pod 自动消失。

5. 使用如下命令销毁环境：

    ```shell
    kubectl delete tidbcluster auto-scaling-demo -n ${namespace}
    kubectl delete tidbmonitor auto-scaling-demo -n ${namespace}
    kubectl delete tidbclusterautoscaler auto-scaling-demo -n ${namespace}
    ```
