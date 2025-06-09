---
title: Tools on Kubernetes
summary: Learn how to use operation tools for TiDB on Kubernetes, including PD Control, TiKV Control, and TiDB Control.
---

# Tools on Kubernetes

This document describes how to use operational tools for TiDB on Kubernetes, including PD Control, TiKV Control, and TiDB Control.

## Use PD Control on Kubernetes

[PD Control](https://docs.pingcap.com/tidb/stable/pd-control) is the command-line tool for PD (Placement Driver). To use PD Control to operate TiDB clusters on Kubernetes, first establish a local connection to the PD service using [`kubectl port-forward`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/):

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd 2379:2379 &>/tmp/portforward-pd.log &
```

After running this command, you can access the PD service at `127.0.0.1:2379` and use the default parameters of the `pd-ctl` command directly. For example, to view the PD configuration:

```shell
pd-ctl -d config show
```

If port 2379 is already in use, you can specify another local port:

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd ${local_port}:2379 &>/tmp/portforward-pd.log &
```

In this case, you need to explicitly specify the PD port in the `pd-ctl` command:

```shell
pd-ctl -u 127.0.0.1:${local_port} -d config show
```

## Use TiKV Control on Kubernetes

[TiKV Control](https://docs.pingcap.com/tidb/stable/tikv-control) is the command-line tool for TiKV. To use TiKV Control to operate TiDB clusters on Kubernetes, first establish local connections to the PD service and the target TiKV Pod using [`kubectl port-forward`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/):

The following example forwards the local port 2379 to the PD service:

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd 2379:2379 &>/tmp/portforward-pd.log &
```

The following example forwards the local port 20160 to the TiKV Pod:

```shell
kubectl port-forward -n ${namespace} ${pod_name} 20160:20160 &>/tmp/portforward-tikv.log &
```

After the connections are established, you can access the PD service and TiKV node through the corresponding local ports:

```shell
tikv-ctl --host 127.0.0.1:20160 --pd 127.0.0.1:2379 ${subcommands}
```

## Use TiDB Control on Kubernetes

[TiDB Control](https://docs.pingcap.com/tidb/stable/tidb-control) is the command-line tool for TiDB. To use TiDB Control, you need local access to both the TiDB node and the PD service. It is recommended to use [`kubectl port-forward`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/) to establish these connections.

The following example forwards the local port 2379 to the PD service:

```shell
kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd 2379:2379 &>/tmp/portforward-pd.log &
```

The following example forwards the local port 10080 to the TiDB Pod:

```shell
kubectl port-forward -n ${namespace} ${pod_name} 10080:10080 &>/tmp/portforward-tidb.log &
```

After the connections are established, you can run `tidb-ctl` to perform various operations. For example, to view the schema of the `mysql` database:

```shell
tidb-ctl schema in mysql
```
