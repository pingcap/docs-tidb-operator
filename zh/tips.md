---
title: Kubernetes 上的 TiDB 集群管理常用使用技巧
summary: 介绍 Kubernetes 上 TiDB 集群管理常用使用技巧。
---

# Kubernetes 上的 TiDB 集群管理常用使用技巧

本文介绍了 Kubernetes 上 TiDB 集群管理常用使用技巧。

## 诊断模式

当 Pod 处于 `CrashLoopBackoff` 状态时，Pod 内容器不断退出，导致无法正常使用 `kubectl exec`，给诊断带来不便。为了解决这个问题，TiDB in Kubernetes 提供了 PD/TiKV/TiDB Pod 诊断模式。在诊断模式下，Pod 内的容器启动后会直接挂起，不会再进入重复 Crash 的状态，此时，便可以通过 `kubectl exec` 连接 Pod 内的容器进行诊断。

操作方式：

1. 首先，为待诊断的 Pod 添加 Annotation：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate pod ${pod_name} -n ${namespace} runmode=debug
    ```

    在 Pod 内的容器下次重启时，会检测到该 Annotation，进入诊断模式。

    > **注意：**
    >
    > 如果 Pod 处于运行中，可以执行以下命令强制让容器重启。
    >
    > ```shell
    > kubectl exec ${pod_name} -n ${namespace} -c ${container} -- kill -SIGTERM 1
    > ```

2. 等待 Pod 进入 Running 状态即可开始诊断：

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl get pod ${pod_name} -n ${namespace}
    ```

    下面是使用 `kubectl exec` 进入容器进行诊断工作的例子：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- /bin/sh
    ```

3. 诊断完毕，修复问题后，删除 Pod：

    ```shell
    kubectl delete pod ${pod_name} -n ${namespace}
    ```

Pod 重建后会自动回到正常运行模式。

## 单独修改某个 TiKV 的配置

在一些测试场景中，如果你需要单独修改某一个 TiKV 实例配置，而不影响其他的 TiKV 实例，可以参考以下两种方式。

### 在线更新

参考文档[在线修改 TiKV 配置](https://docs.pingcap.com/zh/tidb/stable/dynamic-config#在线修改-tikv-配置)，使用 SQL 在线更新某一个 TiKV 实例的配置。

> **注意：**
>
> 这种方式的配置更新是临时的，不会持久化。这意味着，当该 TiKV 的 Pod 重启后，依旧会使用原来的配置。

### 进入诊断模式后修改配置

让 TiKV Pod 进入[诊断模式](#诊断模式)后，可以手动修改 TiKV 的配置文件，并指定使用修改后的配置文件启动 TiKV 进程。

具体操作步骤如下：

1. 从 TiKV 的日志中获取 TiKV 的启动命令，后续步骤中将会使用。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs pod ${pod_name} -n ${namespace} -c tikv | head -2 | tail -1
    ```

    输出类似如下，该行就是 TiKV 的启动命令。

    ```shell
    /tikv-server --pd=http://${tc_name}-pd:2379 --advertise-addr=${pod_name}.${tc_name}-tikv-peer.default.svc:20160 --addr=0.0.0.0:20160 --status-addr=0.0.0.0:20180 --data-dir=/var/lib/tikv --capacity=0 --config=/etc/tikv/tikv.toml
    ```

    > **注意：**
    >
    > 如果 TiKV Pod 持续处于 `CrashLoopBackoff` 状态，无法从日志中获取启动命令，可以按照上述的命令格式来拼接出启动命令。

2. 对 Pod 开启诊断模式，并重启 Pod。

    执行以下命令为 Pod 添加 Annotation，等待下一次 Pod 重启。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate pod ${pod_name} -n ${namespace} runmode=debug
    ```

    如果 Pod 一直处于运行中，你可以执行以下命令强制让 TiKV 容器重启。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec ${pod_name} -n ${namespace} -c tikv -- kill -SIGTERM 1
    ```

    可以通过检查 TiKV 的日志，确认是否进入了诊断模式。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs ${pod_name} -n ${namespace} -c tikv
    ```

    期望的日志内容如下：

    ```
    entering debug mode.
    ```

3. 执行下面命令进入 TiKV 容器。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -c tikv -- sh
    ```

4. 在 TiKV 容器中，复制 TiKV 的配置文件，然后在新的文件上修改 TiKV 的配置。

    {{< copyable "shell-regular" >}}

    ```shell
    cp /etc/tikv/tikv.toml /tmp/tikv.toml && vi /tmp/tikv.tmol
    ```

5. 在 TiKV 容器中，根据第 1 步中获取的 TiKV 的启动命令，修改启动参数 `--config` 为刚刚新创建的配置文件路径后，启动 TiKV 进程。

    ```shell
    /tikv-server --pd=http://${tc_name}-pd:2379 --advertise-addr=${pod_name}.${tc_name}-tikv-peer.default.svc:20160 --addr=0.0.0.0:20160 --status-addr=0.0.0.0:20180 --data-dir=/var/lib/tikv --capacity=0 --config=/tmp/tikv.toml
    ```

测试完成后，如果要恢复 TiKV Pod，可以直接删除当前的 TiKV Pod，并等待 TiKV Pod 自动被拉起。

{{< copyable "shell-regular" >}}

```shell
kubectl delete ${pod_name} -n ${namespace}
```

## 配置 TiKV 强制升级

正常情况下，在 TiKV 滚动升级或者修改配置滚动更新过程中，TiDB Operator 会为每个 TiKV 驱逐 Region Leader，并在 Leader 驱逐完成后才开始更新当前 Pod，尽量减小滚动升级或者更新过程对用户请求的影响。在一些测试场景中，如果你不需要在 TiKV 滚动升级或者修改配置滚动更新过程中等待 TiKV 上的 Region Leader 迁移，想要加速升级或者更新过程，可以将 TidbCluster 定义中的 `spec.tikv.evictLeaderTimeout` 字段设置为一个很小的值。

```yaml
spec:
  tikv:
    evictLeaderTimeout: 10s
```

关于该字段更多的说明，见[配置 TiKV 平滑升级](configure-a-tidb-cluster.md#配置-tikv-平滑升级)。

> **警告：**
>
> 该操作会导致部分用户请求失败，不建议在生产环境中使用。

## 配置 TiCDC 强制升级

正常情况下，在 TiCDC 滚动升级或者修改配置滚动更新过程中，TiDB Operator 会转移 TiCDC 上的同步负载，并在同步负载转移完成后才开始更新当前 Pod，尽量减小滚动升级或者更新过程对同步延时的影响。在一些测试场景中，如果你不需要在 TiCDC 滚动升级或者修改配置滚动更新过程中等待 TiCDC 上的同步负载迁移，想要加速升级或者更新过程，可以将 TidbCluster 定义中的 `spec.ticdc.gracefulShutdownTimeout` 字段设置为一个很小的值。

```yaml
spec:
  ticdc:
    gracefulShutdownTimeout: 10s
```

关于该字段更多的说明，见[配置 TiCDC 平滑升级](configure-a-tidb-cluster.md#配置-ticdc-平滑升级)。

> **警告：**
>
> 该操作会导致同步延时上升，不建议在生产环境中使用。
