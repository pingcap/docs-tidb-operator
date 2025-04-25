---
title: 销毁 Kubernetes 上的 TiDB 集群
summary: 介绍如何销毁 Kubernetes 集群上的 TiDB 集群。
---

# 销毁 Kubernetes 上的 TiDB 集群

本文描述了如何销毁 Kubernetes 集群上的 TiDB 集群。

## 销毁使用 `Cluster` 管理的 TiDB 集群

要销毁使用 `Cluster` 管理的 TiDB 集群，执行以下命令：

```shell
kubectl delete cluster ${cluster_name} -n ${namespace}
```
