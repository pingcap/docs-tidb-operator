---
title: 在 Kubernetes 上部署 TiDB Operator
summary: 了解如何在 Kubernetes 上部署 TiDB Operator。
---

# 在 Kubernetes 上部署 TiDB Operator

本文介绍如何在 Kubernetes 上部署 TiDB Operator。

## 准备环境

部署 TiDB Operator 前，请确保你的环境满足以下软件要求：

- [Kubernetes >= v1.30](https://kubernetes.io/releases/)
- [kubectl >= v1.30](https://kubernetes.io/docs/tasks/tools/)
- [Helm >= v3.8](https://helm.sh/)

## 部署 Kubernetes 集群

TiDB Operator 运行在 Kubernetes 集群中。你可以选择以下任一方式搭建 Kubernetes 集群：

- **自托管集群**：根据 [Kubernetes 官方文档](https://kubernetes.io/zh-cn/docs/setup/)中任意一种方法搭建自托管的 Kubernetes 集群。
- **云服务提供商**：使用 [Kubernetes 认证的云服务提供商](https://kubernetes.io/zh-cn/docs/setup/production-environment/turnkey-solutions/)提供的 Kubernetes 集群服务。

无论选择哪种方式，请务必确保你的 Kubernetes 版本为 v1.30 或更高。如果需要快速搭建一个用于测试的简单集群，可以参考[快速上手教程](get-started.md)。

## 部署 TiDB Operator CRD

执行以下命令，安装 TiDB Operator 所需的 [Custom Resource Definition (CRD)](https://kubernetes.io/zh-cn/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions)：

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.3/tidb-operator.crds.yaml --server-side
```

## 部署 TiDB Operator

你可以通过以下两种方式部署 TiDB Operator：

- [使用 `kubectl apply` 快速部署](#方式一使用-kubectl-apply-快速部署)
- [使用 Helm 部署](#方式二使用-helm-部署)

### 方式一：使用 `kubectl apply` 快速部署

TiDB Operator 安装所需的所有资源（包括 RBAC 和 Deployment 等，CRD 除外）都已打包在 `tidb-operator.yaml` 文件中。你可以使用以下命令一键部署，无需额外指定参数：

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.3/tidb-operator.yaml --server-side
```

TiDB Operator 将被部署到 `tidb-admin` namespace 下。你可以运行以下命令验证安装是否成功：

```shell
kubectl get pods -n tidb-admin
```

预期输出如下：

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

### 方式二：使用 Helm 部署

使用 Helm 部署除 CRD 外的所有资源：

```shell
helm install tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator:v2.0.0-alpha.3 --namespace tidb-admin --create-namespace
```

TiDB Operator 将被部署到 `tidb-admin` namespace 下。你可以运行以下命令验证安装是否成功：

```shell
kubectl get pods -n tidb-admin
```

预期输出如下：

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

#### 自定义安装

如需自定义部署参数，请先导出默认的 `values.yaml` 文件：

```shell
helm show values oci://ghcr.io/pingcap/charts/tidb-operator:v2.0.0-alpha.3 > values.yaml
```

根据需要修改 `values.yaml`，然后执行以下命令安装：

```shell
helm install tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator:v2.0.0-alpha.3 -f values.yaml
```
