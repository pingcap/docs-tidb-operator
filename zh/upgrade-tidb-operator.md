---
title: 升级 TiDB Operator
summary: 介绍如何将 TiDB Operator 升级到指定版本。
---

# 升级 TiDB Operator

本文介绍如何升级 TiDB Operator 到指定版本。

## 升级注意事项

暂不支持从 v1.x 升级到 v2.x 版本。

## 升级 CRD

执行以下命令以升级 TiDB Operator 的 Custom Resource Definition (CRD)。请将 `${version}` 替换为目标 TiDB Operator 版本，例如 `v2.0.0-alpha.3`。

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/${version}/tidb-operator.crds.yaml --server-side
```

## 升级 TiDB Operator 组件

你可以使用以下两种方式升级 TiDB Operator 组件：

* [使用 `kubectl apply`](#方式一使用-kubectl-apply-升级)
* [使用 Helm](#方式二使用-helm-升级)

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

如果你的 TiDB Operator 是使用 Helm 部署，可以使用 `helm upgrade` 命令进行升级。

执行以下命令升级 TiDB Operator：

```shell
helm upgrade tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator --version=${version} --namespace=tidb-admin
```

> **注意：**
>
> * `tidb-operator` 是 TiDB Operator 的 Helm release 名称。如果你的 release 名称不同，请替换为实际的名称。
> * `${version}` 是目标升级的 TiDB Operator 版本号。
> * `--namespace=tidb-admin` 指定 TiDB Operator 所在的命名空间。如果你的命名空间不同，请替换为实际的命名空间。

升级完成后，你可以通过以下命令检查 Pod 状态，确认升级是否成功：

```shell
kubectl get pods -n tidb-admin
```

#### 自定义升级

如果部署或升级过程中使用了自定义配置（即修改了 `values.yaml` 文件），你需要确保在本次升级中也使用这些自定义配置。

1. 获取当前部署所使用的 `values.yaml` 文件：

    ```shell
    helm get values tidb-operator -n tidb-admin > values.yaml
    ```

2. 获取目标版本的默认配置文件 `values-new.yaml`：

    ```shell
    helm show values oci://ghcr.io/pingcap/charts/tidb-operator --version=${version} > values-new.yaml
    ```

3. 对比 `values.yaml` 和 `values-new.yaml` 两个文件，将你的自定义配置项合并到 `values-new.yaml` 中。

4. 使用合并后的 `values-new.yaml` 文件进行升级：

    ```shell
    helm upgrade tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator --version=${version} -f values-new.yaml --namespace=tidb-admin
    ```
