---
title: 在 Kubernetes 上部署 TiCDC
summary: 了解如何在 Kubernetes 上部署 TiCDC。
category: how-to
---

# 在 Kubernetes 上部署 TiCDC

本文介绍如何在 Kubernetes 上部署 TiCDC。

## 前置条件

* TiDB Operator [部署](deploy-tidb-operator.md)完成。

## 全新部署 TiDB 集群同时部署 TiCDC

参考 [在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)进行部署。

## 在现有 TiDB 集群上新增 TiCDC 组件

编辑 TidbCluster Custom Resource：

{{< copyable "shell-regular" >}}

``` shell
kubectl edit tc ${cluster_name} -n ${namespace}
```

按照如下示例增加 TiCDC 配置：

```yaml
spec:
  ticdc:
    baseImage: pingcap/ticdc
    replicas: 3
```

部署完成后，通过 `kubectl exec` 进入任意一个 TiCDC Pod 进行操作。

{{< copyable "shell-regular" >}}

```shell
kubectl exec -it ${pod_name} -n ${namespace} sh
```

然后通过 `cdc cli` 进行[管理集群和同步任务](https://pingcap.com/docs-cn/stable/ticdc/manage-ticdc/)。

{{< copyable "shell-regular" >}}

```shell
/cdc cli capture list --pd=${pd_address}:2379
```
