---
title: 在 Kubernetes 上部署 TiDB Operator
summary: 了解如何在 Kubernetes 上部署 TiDB Operator。
---

# 在 Kubernetes 上部署 TiDB Operator

本文介绍如何在 Kubernetes 上部署 TiDB Operator。

## 准备环境

TiDB Operator 部署前，请确认以下软件需求：

- [Kubernetes >= v1.30](https://kubernetes.io/releases/)
- [Kubectl >= v1.22](https://kubernetes.io/docs/tasks/tools/)
- [Helm >= v3.8](https://helm.sh/)

TiDB Operator 运行在 Kubernetes 集群，你可以使用 [Getting started 页面](https://kubernetes.io/docs/setup/) 列出的任何一种方法搭建一套自管理的 Kubernetes 集群, 也可以选择 [Kubernetes 认证的云服务提供商](https://kubernetes.io/docs/setup/production-environment/turnkey-solutions/) 提供的 Kubernetes 集群服务。只要保证 Kubernetes 版本大于等于 v1.30。若想创建一个简单集群测试，可以参考[快速上手教程](get-started.md)。

## 部署 TiDB Operator CRDs

通过如下命令安装 CRDs (CustomResourceDefinitions)

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.3/tidb-operator.crds.yaml --server-side
```

## 部署 TiDB Operator

### 使用 kubectl apply 快速部署

所有 TiDB Operator 安装所需的除 CRD 外的资源 (RBAC, Deployment 等) 都已经包含在 tidb-operator.yaml 文件中，用户可以通过如下命令一键部署，无需指定参数

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.3/tidb-operator.yaml --server-side
```

TiDB Operator 会被安装到 `tidb-admin` namespace 下，可以通过如下命令确认是否完成了安装

```shell
kubectl get pods -n tidb-admin
```

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

### 使用 Helm 部署

支持使用 helm 安装部署除 CRD 外的资源

```shell
helm install tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator:v2.0.0-alpha.3 --namespace tidb-admin --create-namespace
```

TiDB Operator 会被安装到 `tidb-admin` namespace 下，可以通过如下命令确认是否完成了安装

```shell
kubectl get pods -n tidb-admin
```

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```


#### 自定义安装

可以通过如下命令获取默认的 `values.yaml`

```shell
helm show values oci://ghcr.io/pingcap/charts/tidb-operator:v2.0.0-alpha.3 > values.yaml
```

完成修改后通过指定 `values.yaml` 来自定义安装

```shell
helm install tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator:v2.0.0-alpha.3 -f values.yaml
```
