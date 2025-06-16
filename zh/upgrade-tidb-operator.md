---
title: 升级 TiDB Operator
summary: 介绍如何将 TiDB Operator 升级到指定版本。
---

# 升级 TiDB Operator

本文介绍如何升级 TiDB Operator 到指定版本。

## 升级注意事项

暂不支持从 v1.x 升级到 v2.x 版本。

## 升级 CRD

执行以下命令以升级 TiDB Operator 的 Custom Resource Definition (CRD)：

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/${version}/tidb-operator.crds.yaml --server-side
```

## 升级 TiDB Operator 组件

你可以使用以下两种方式升级 TiDB Operator 组件：

* [使用 `kubectl apply`](#使用-kubectl-apply-升级)
* [使用 Helm](#使用-helm-升级)

### 方式一：使用 `kubectl apply` 升级

执行以下命令以升级 TiDB Operator 组件：

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/${version}/tidb-operator.yaml --server-side
```

此命令会升级部署在 `tidb-admin` namespace 下的 TiDB Operator。你可以运行以下命令确认 Pod 是否升级成功：

```shell
kubectl get pods -n tidb-admin
```

预期输出示例：

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

### 方式二：使用 Helm 升级

<!-- TODO -->
