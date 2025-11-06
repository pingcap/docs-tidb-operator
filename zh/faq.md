---
title: Kubernetes 上的 TiDB 集群常见问题
summary: 介绍 Kubernetes 上的 TiDB 集群常见问题以及解决方案。
---

# Kubernetes 上的 TiDB 集群常见问题

本文介绍 Kubernetes 上的 TiDB 集群常见问题以及解决方案。

## 如何修改时区设置？

默认情况下，在 Kubernetes 集群上部署的 TiDB 集群各组件容器中的时区为 UTC。如果要修改时区配置，可以使用 [Overlay](overlay.md) 功能进行如下配置：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: tidb
spec:
  template:
    spec:
      overlay:
        pod:
          spec:
            containers:
              - name: tidb
                env:
                  - name: "TZ"
                    value: "Asia/Shanghai"
```

## TiDB 相关组件可以配置 HPA 或 VPA 吗？

TiDB 集群目前还不支持 HPA（Horizontal Pod Autoscaling，自动水平扩缩容）和 VPA（Vertical Pod Autoscaling，自动垂直扩缩容），因为对于数据库这种有状态应用而言，实现自动扩缩容难度较大，无法仅通过 CPU 和 memory 监控数据来简单地实现。

## 使用 TiDB Operator 编排 TiDB 集群时，有什么场景需要人工介入操作吗？

如果不考虑 Kubernetes 集群本身的运维，TiDB Operator 存在以下可能需要人工介入的场景：

* 维护或下线指定的 Kubernetes 节点，参考[维护节点](maintain-a-kubernetes-node.md)。

## 在公有云上使用 TiDB Operator 编排 TiDB 集群时，推荐的部署拓扑是怎样的？

首先，为了实现高可用和数据安全，我们在推荐生产环境下的 TiDB 集群中至少部署在三个可用区 (Available Zone)。

当考虑 TiDB 集群与业务服务的部署拓扑关系时，TiDB Operator 支持下面几种部署形态。它们有各自的优势与劣势，具体选型需要根据实际业务需求进行权衡：

* 将 TiDB 集群与业务服务部署在同一个 VPC 中的同一个 Kubernetes 集群上。
* 将 TiDB 集群与业务服务部署在同一个 VPC 中的不同 Kubernetes 集群上。
* 将 TiDB 集群与业务服务部署在不同 VPC 中的不同 Kubernetes 集群上。

## TiDB Operator 支持 TiSpark 吗？

TiDB Operator 尚不支持自动编排 TiSpark。

假如要为 TiDB on Kubernetes 添加 TiSpark 组件，你需要在**同一个** Kubernetes 集群中自行维护 Spark，确保 Spark 能够访问到 PD 和 TiKV 实例的 IP 与端口，并为 Spark 安装 TiSpark 插件，TiSpark 插件的安装方式可以参考 [TiSpark](https://docs.pingcap.com/zh/tidb/stable/tispark-overview#在已有-spark-集群上部署-tispark)。

在 Kubernetes 上维护 Spark 可以参考 Spark 的官方文档：[Spark on Kubernetes](http://spark.apache.org/docs/latest/running-on-kubernetes.html)。

## 如何查看 TiDB 集群配置？

如果需要查看当前集群的 PD、TiKV、TiDB 组件的配置信息，可以执行下列命令：

* 查看 PD 配置文件：

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- cat /etc/pd/config.toml
    ```

* 查看 TiKV 配置文件：

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- cat /etc/tikv/config.toml
    ```

* 查看 TiDB 配置文件：

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- cat /etc/tidb/config.toml
    ```

## 部署 TiDB 集群时调度失败是什么原因？

TiDB Operator 调度 Pod 失败的原因可能有两种情况：

* 资源不足，导致 Pod 一直阻塞在 `Pending` 状态。详细说明参见[集群故障诊断](deploy-failures.md)。

* 部分 Node 被打了 `taint`，导致 Pod 无法调度到对应的 Node 上。详请参考 [taint & toleration](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/taint-and-toleration/)。

## TiDB 如何保证数据安全可靠？

TiDB Operator 部署的 TiDB 集群使用 Kubernetes 集群提供的[持久卷](https://kubernetes.io/zh-cn/docs/concepts/storage/persistent-volumes/)作为存储，保证数据的持久化存储。

PD 和 TiKV 使用 [Raft 一致性算法](https://raft.github.io/)将存储的数据在各节点间复制为多副本，以确保某个节点宕机时数据的安全性。

在底层，TiKV 使用复制日志 + 状态机 (State Machine) 的模型来复制数据。对于写入请求，数据被写入 Leader，然后 Leader 以日志的形式将命令复制到它的 Follower 中。当集群中的大多数节点收到此日志时，日志会被提交，状态机会相应作出变更。
