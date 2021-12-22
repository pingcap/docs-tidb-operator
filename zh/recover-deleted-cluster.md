---
title: 恢复误删的 TiDB 集群
summary: 介绍如何恢复误删的 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/recover-deleted-cluster/']
---

# 恢复误删的 TiDB 集群

本文介绍如何恢复在 Kubernetes 上误删的 TiDB 集群。如果你使用 TidbCluster 或 Helm 意外删除了 TiDB 集群，可参考本文介绍的方法恢复集群。

## 恢复在 TidbCluster 上误删的 TiDB 集群

TiDB Operator 使用 PV (Persistent Volume)、PVC (Persistent Volume Claim) 来存储持久化的数据，如果不小心使用 `kubectl delete tc` 意外删除了 TiDB 集群，PV/PVC 对象以及数据都会保留下来，以最大程度保证数据安全。

此时你可以使用 `kubectl create` 命令来创建一个同名同配置的集群，之前保留下来未被删除的 PV/PVC 以及数据会被复用：

{{< copyable "shell-regular" >}}

```shell
kubectl -n ${namespace} create -f tidb-cluster.yaml
```

## 恢复在 Helm 上误删的 TiDB 集群

TiDB Operator 使用 PV (Persistent Volume)、PVC (Persistent Volume Claim) 来存储持久化的数据，如果不小心使用 `helm uninstall` 意外删除了集群，PV/PVC 对象以及数据都会保留下来，以最大程度保证数据安全。

此时你可以使用 `helm install` 命令来创建一个同名同配置的集群，之前保留下来未被删除的 PV/PVC 以及数据会被复用：

{{< copyable "shell-regular" >}}

```shell
helm install ${release_name} pingcap/tidb-cluster --namespace=${namespace} --version=${chart_version} -f values.yaml
```
