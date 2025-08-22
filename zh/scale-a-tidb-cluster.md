---
title: 手动扩缩容 Kubernetes 上的 TiDB 集群
summary: 了解如何在 Kubernetes 上手动对 TiDB 集群进行水平和垂直扩缩容。
---

# 手动扩缩容 Kubernetes 上的 TiDB 集群

本文介绍如何对部署在 Kubernetes 上的 TiDB 集群进行手动水平扩缩容和垂直扩缩容。

## 水平扩缩容

水平扩缩容操作是指通过增加或减少组件的 Pod 的数量，来达到集群扩缩容的目的。可通过修改组件的 `replicas` 参数来控制 Pod 数量，从而实现扩容或缩容。

* 如果要进行扩容操作，可将某个组件的 `replicas` 值**调大**。扩容操作会增加组件 Pod，直到 Pod 数量与 `replicas` 值相等。
* 如果要进行缩容操作，可将某个组件的 `replicas` 值**调小**。缩容操作会删除组件 Pod，直到 Pod 数量与 `replicas` 值相等。

如果要对 TiDB 集群进行水平扩缩容，你可以使用 `kubectl` 修改对应组件的 Component Group Custom Resource (CR) 对象中的 `spec.replicas` 至期望值。

1. 按需修改 TiDB 集群组件的 `replicas` 值。例如，执行以下命令可将 PD 的 `replicas` 值设置为 `3`：

    ```shell
    kubectl patch -n ${namespace} pdgroup ${name} --type merge --patch '{"spec":{"replicas":3}}'
    ```

2. 查看 Kubernetes 集群中对应组件的 Component Group CR 是否更新为期望的配置。例如，执行以下命令查看 PDGroup CR：

    ```shell
    kubectl get pdgroup ${name} -n ${namespace}
    ```

    上述命令输出的 `DESIRED` 的值预期应与你之前配置的值一致。

3. 观察 Pod 是否新增或者减少：

    ```shell
    kubectl -n ${namespace} get pod -w
    ```

    当所有组件的 Pod 数量都达到了预设值，并且都进入 `Running` 状态后，水平扩缩容完成。

    PD 和 TiDB 通常需要 10 到 30 秒左右的时间进行扩容或者缩容。

    TiKV 组件由于涉及到数据搬迁，通常需要 3 到 5 分钟来进行扩容或者缩容。

> **注意：**
>
> - TiKV 组件在缩容过程中，TiDB Operator 会调用 PD 接口将对应 TiKV 标记为下线，然后将其上数据迁移到其它 TiKV 节点，在数据迁移期间 TiKV Pod 依然是 `Running` 状态，数据迁移完成后对应 Pod 才会被删除，缩容时间与待缩容的 TiKV 上的数据量有关，可以通过 `kubectl get -n ${namespace} tikv` 查看 TiKV 是否处于下线 `Removing` 状态。
> - 当 `Serving` 状态的 TiKV 数量小于或等于 PD 配置中 `MaxReplicas` 的参数值时，无法缩容 TiKV 组件。
> - TiKV 组件不支持在缩容过程中进行扩容操作，强制执行此操作可能导致集群状态异常。
> - TiFlash 组件缩容处理逻辑和 TiKV 组件相同。

## 垂直扩缩容

垂直扩缩容操作指的是通过增加或减少 Pod 的资源限制，来达到集群扩缩容的目的。垂直扩缩容本质上是 Pod 滚动升级的过程。

如果要对 PD、TiKV、TiDB、TiProxy、TiFlash 或 TiCDC 进行垂直扩缩容，通过 `kubectl` 修改对应的 Component Group CR 对象的 `spec.template.spec.resources` 至期望值。

> **注意：**
>
> 暂不支持[原地调整 Pod 的资源](https://kubernetes.io/zh-cn/docs/tasks/configure-pod-container/resize-container-resources/)。

### 查看垂直扩缩容进度

```shell
kubectl -n ${namespace} get pod -w
```

当所有 Pod 都重建完毕进入 `Running` 状态后，垂直扩缩容完成。

> **注意：**
>
> - 如果在垂直扩容时修改了资源的 `requests` 字段，并且 PD、TiKV、TiFlash、TiCDC 使用了 `Local PV`，那升级后 Pod 还会调度回原节点，如果原节点资源不够，则会导致 Pod 一直处于 `Pending` 状态而影响服务。
> - TiDB 是一个可水平扩展的数据库，推荐通过增加节点个数发挥 TiDB 集群可水平扩展的优势，而不是类似传统数据库升级节点硬件配置来实现垂直扩容。

## 扩缩容故障诊断

无论是水平扩缩容、或者是垂直扩缩容，都可能遇到资源不够时造成 Pod 出现 Pending 的情况。可以参考 [Pod 处于 Pending 状态](deploy-failures.md#pod-处于-pending-状态)来进行处理。
