---
title: Kubernetes 上的 TiDB 工具指南
summary: 详细介绍 Kubernetes 上的 TiDB 相关的工具及其使用方法。
---

# Kubernetes 上的 TiDB 工具指南

本文档详细介绍了 Kubernetes 上的 TiDB 相关的工具及其使用方法。

## 在 Kubernetes 上使用 PD Control

[PD Control](https://docs.pingcap.com/zh/tidb/stable/pd-control) 是 PD 的命令行工具，在使用 PD Control 操作 Kubernetes 上的 TiDB 集群时，需要先使用 `kubectl port-forward` 打开本地到 PD 服务的连接：

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd 2379:2379 &>/tmp/portforward-pd.log &
```

执行上述命令后，就可以通过 `127.0.0.1:2379` 访问到 PD 服务，从而直接使用 `pd-ctl` 命令的默认参数执行操作，如：

```shell
# 查看 PD 配置（通过本地 2379 端口访问）
pd-ctl -d config show
```

假如你本地的 2379 被占据，则需要选择其它端口：

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd ${local_port}:2379 &>/tmp/portforward-pd.log &
```

此时，需要为 `pd-ctl` 命令显式指定 PD 端口：

```shell
pd-ctl -u 127.0.0.1:${local_port} -d config show
```

## 在 Kubernetes 上使用 TiKV Control

[TiKV Control](https://docs.pingcap.com/zh/tidb/stable/tikv-control) 是 TiKV 的命令行工具。在使用 TiKV Control 操作 Kubernetes 上的 TiDB 集群时，需要先使用 `kubectl port-forward` 打开本地到 PD 服务以及目标 TiKV 节点的连接：

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd 2379:2379 &>/tmp/portforward-pd.log &
```

```shell
# 打开本地到目标 TiKV Pod 的端口转发
kubectl port-forward -n ${namespace} ${pod_name} 20160:20160 &>/tmp/portforward-tikv.log &
```

打开连接后，即可通过本地的对应端口访问 PD 服务和 TiKV 节点：

```shell
tikv-ctl --host 127.0.0.1:20160 --pd 127.0.0.1:2379 ${subcommands}
```

## 在 Kubernetes 上使用 TiDB Control

[TiDB Control](https://docs.pingcap.com/zh/tidb/stable/tidb-control) 是 TiDB 的命令行工具，使用 TiDB Control 时，需要从本地访问 TiDB 节点和 PD 服务，因此建议使用 `kubectl port-forward` 打开到集群中 TiDB 节点和 PD 服务的连接：

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd 2379:2379 &>/tmp/portforward-pd.log &
```

```shell
# 打开本地到 TiDB Pod 的端口转发
kubectl port-forward -n ${namespace} ${pod_name} 10080:10080 &>/tmp/portforward-tidb.log &
```

接下来便可开始使用 `tidb-ctl` 命令：

```shell
# 查看 mysql 库的 schema
tidb-ctl schema in mysql
```
