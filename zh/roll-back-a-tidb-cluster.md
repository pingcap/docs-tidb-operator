---
title: 回退 Kubernetes 上的 TiDB 集群
summary: 介绍如何回退 Kubernetes 上的 TiDB 集群。
---

# 回退 Kubernetes 上的 TiDB 集群

如果你使用 TiDB Operator 部署管理 Kubernetes 上的 TiDB 集群，可以通过回退 TiDB 集群到指定补丁版本，减少新版本对业务的影响。本文介绍如何回退 Kubernetes 上的 TiDB 集群。

在回退 Kubernetes 上的 TiDB 集群的时候，TiDB Operator 会串行地删除各个组件当前版本的 Pod，并创建指定版本的 Pod。当指定版本的 Pod 正常运行后，再处理下一个 Pod。

滚动回退时，TiDB Operator 会自动处理 PD 和 TiKV 的 Leader 迁移。因此，在多节点的部署拓扑下（最小环境要求：3 个 PD、3 个 TiKV、3 个 TiDB），滚动回退 TiKV、PD 不会影响业务正常运行。对于有连接重试功能的客户端，滚动回退 TiDB 同样不会影响业务。

## 支持回退的版本

本文档适用于以下回退路径：

- 使用 TiDB 从 v7.5.Y 版本回退至 v7.5.X，其中 Y 和 X 是大于 0 的整数，且 Y>X。

其他补丁版本的回退未经验证，如直接回退，可能会产生非预期的问题。

## 注意事项

回退版本时，请注意以下事项：

- 对于无法进行连接重试的客户端，版本回退会导致连接到被关闭的 TiDB 节点的数据库的连接失效，造成部分业务请求失败。对于这类业务，推荐在客户端添加重试功能，或者在低峰期进行 TiDB 的滚动更新操作。
- 在回退 TiDB 集群的过程中，请勿执行 DDL 语句，否则可能会出现行为未定义的问题。
- 回退的集群内的各组件应该使用相同版本。 
- Changefeed 默认配置值在回退过程中不会被更改，已经修改的值，在回退过程中也不会被修改。

## 回退前的准备工作

### 查阅兼容性变更

- TiDB 目前仅支持有限的补丁版本回退。请参见[支持回退的版本](#支持回退的版本)。

- 查看对应版本的 [Release Notes](https://docs.pingcap.com/zh/tidb/stable/release-notes) 中的兼容性变更。如果有任何变更影响到回退，请采取相应的措施。例如，从 TiDB v7.5.2 回退至 v7.5.1 时，需查阅以下各版本的兼容性变更：

    - [TiDB v7.5.1 Release Notes](https://docs.pingcap.com/zh/tidb/stable/release-7.5.1#兼容性变更) 中的兼容性变更
    - [TiDB v7.5.2 Release Notes](https://docs.pingcap.com/zh/tidb/stable/release-7.5.2#兼容性变更) 中的兼容性变更

### 检查当前集群的 DDL

集群中有 DDL 语句正在被执行时，请勿进行版本回退操作。被执行的 DDL 语句通常为 [`ADD INDEX`](https://docs.pingcap.com/zh/tidb/stable/sql-statement-add-index) 和列类型变更等耗时较久的 DDL 语句。

在回退前，为避免回退过程中出现未定义行为或其他故障，建议执行下列操作：

1. 使用 [`ADMIN SHOW DDL`](https://docs.pingcap.com/zh/tidb/stable/sql-statement-admin-show-ddl) 命令查看集群中是否有正在进行的 DDL Job。

2. 如需回退，请等待 DDL 执行完成，或使用 [`ADMIN CANCEL DDL`](https://docs.pingcap.com/zh/tidb/stable/sql-statement-admin-cancel-ddl) 命令取消该 DDL Job。

### 检查当前集群的健康状况

为避免回退过程中出现未定义行为或其他故障，建议在回退前对使用 `check` 子命令检查集群的 Region 健康状态。

```shell
tiup cluster check <cluster-name> --cluster
```

执行结束后，会输出 `region status` 检查结果。

- 如果结果为 `All regions are healthy`，则说明当前集群中所有 Region 均为健康状态，可以继续执行回退。
- 如果结果为 `Regions are not fully healthy: m miss-peer, n pending-peer`，并提示 `Please fix unhealthy regions before other operations.`，则说明当前集群中有 Region 处在异常状态。此时应先排除相应异常状态，并再次检查结果为 `All regions are healthy` 后再继续回退。

## 执行回退操作

1. 通过 TiDB Operator，严格按如下顺序执行回退操作：

    ```shell
    pd-ctl pd config set cluster-version "v7.5.0" -u \"pd-1-peer:2379\"
    use kubectl edit tc/tc ticdc version to v7.5.0
    use kubectl edit tc/tc tidb version to v7.5.0
    use kubectl edit tc/tc tikv version to v7.5.0
    use kubectl edit tc/tc tiflash version to v7.5.0
    use kubectl edit tc/tc pd version to v7.5.0
    ```

2. 查看回退进度：

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

3. 当所有 Pod 都重建完毕进入 `Running` 状态后，回退完成。
