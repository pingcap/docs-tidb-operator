---
title: 升级 TiDB Operator
summary: 介绍如何升级 TiDB Operator。
---

# 升级 TiDB Operator

本文介绍如何升级 TiDB Operator 到指定版本。

## 升级注意事项

暂不支持从 v1 升级到 v2

## 升级 CRDs

通过如下命令升级 CRDs (CustomResourceDefinitions)

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/${version}/tidb-operator.crds.yaml --server-side
```

## 升级 TiDB Operator 组件

### 使用 kubectl apply 升级

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/${version}/tidb-operator.yaml --server-side
```

安装在 `tidb-admin` namespace 下的 TiDB Operator 会被升级, 可以通过如下命令查看 pod 是否升级完成。

```shell
kubectl get pods -n tidb-admin
```

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

### 使用 Helm 升级

<!-- TODO -->
