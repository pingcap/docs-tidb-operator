---
title: 升级 Kubernetes 上的 TiDB 集群
summary: 介绍如何升级 Kubernetes 上的 TiDB 集群。
---

# 升级 Kubernetes 上的 TiDB 集群

如果你使用 TiDB Operator 部署管理 Kubernetes 上的 TiDB 集群，可以通过滚动更新来升级 TiDB 集群的版本，减少对业务的影响。本文介绍如何使用滚动更新来升级 Kubernetes 上的 TiDB 集群。

## 滚动更新功能介绍

Kubernetes 提供了[滚动更新功能](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)，在不影响应用可用性的前提下执行更新。

使用滚动更新时，TiDB Operator 会当新版本的 Pod 正常运行后，再处理下一个 Pod。

滚动更新中，TiDB Operator 会自动处理 PD 和 TiKV 的 Leader 迁移。因此，在多节点的部署拓扑下（最小环境：PD \* 3、TiKV \* 3、TiDB \* 2），滚动更新 TiKV、PD 不会影响业务正常运行。对于有连接重试功能的客户端，滚动更新 TiDB 同样不会影响业务。

> **警告：**
>
> - 对于无法进行连接重试的客户端，**滚动更新 TiDB 会导致连接到被关闭节点的数据库的连接失效**，造成部分业务请求失败。对于这类业务，推荐在客户端添加重试功能，或者在低峰期进行 TiDB 的滚动更新操作。
> - 升级前，请参考[文档](https://docs.pingcap.com/zh/tidb/stable/sql-statement-admin-show-ddl)确认没有正在进行的 DDL 操作。

## 升级前准备

1. 查阅[升级兼容性说明](https://docs.pingcap.com/zh/tidb/dev/upgrade-tidb-using-tiup#1-升级兼容性说明)，了解升级的注意事项。注意包括补丁版本在内的所有 TiDB 版本目前暂不支持降级或升级后回退。
2. 查阅 [TiDB release notes](https://docs.pingcap.com/zh/tidb/dev/release-notes) 中各中间版本的兼容性变更。如果有任何变更影响到了你的升级，请采取相应的措施。

    例如，从 TiDB v6.4.0 升级至 v6.5.2 时，需查阅以下各版本的兼容性变更：

    - TiDB v6.5.0 release notes 中的[兼容性变更](https://docs.pingcap.com/zh/tidb/dev/release-6.5.0#兼容性变更)和[废弃功能](https://docs.pingcap.com/zh/tidb/dev/release-6.5.0#废弃功能)
    - TiDB v6.5.1 release notes 中的[兼容性变更](https://docs.pingcap.com/zh/tidb/dev/release-6.5.1#兼容性变更)
    - TiDB v6.5.2 release notes 中的[兼容性变更](https://docs.pingcap.com/zh/tidb/dev/release-6.5.2#兼容性变更)

    如果从 v6.3.0 或之前版本升级到 v6.5.2，也需要查看中间版本 release notes 中提到的兼容性变更信息。

## 升级步骤

1. 修改待升级集群的各组件 group 的版本配置, 通过 `version` 字段指定组件版本：

    ```yaml
    spec:
      template:
        spec:
          version: v8.1.0
    ```

    可以通过 `kubectl apply` 一次性完成所有组件的变更，也可以通过 `kubectl edit` 一个个组件完成变更。TiDB Operator 会自动编排组件升级的顺序, 在组件不符合升级前置条件的情况下阻塞升级。

    > **注意：**
    >
    > - TiDB Operator 会限制集群内的各组件都使用相同的版本，所以需要将所有组件的 `spec.template.spec.version` 都设置成相同的值。

2. 查看升级进度：

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    当所有 Pod 都重建完毕进入 `Running` 状态后，升级完成。

