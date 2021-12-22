---
title: 灰度升级 TiDB Operator
summary: 介绍如何灰度升级 TiDB Operator，避免 TiDB Operator 升级对整个 Kubernetes 集群中的所有 TiDB 集群产生不可预知的影响。
---

# 灰度升级 TiDB Operator

灰度升级可以控制 TiDB Operator 升级的影响范围，避免 TiDB Operator 升级对整个 Kubernetes 集群中的所有 TiDB 集群产生不可预知的影响。使用灰度升级后，你可以在灰度部署的集群中确认 TiDB Operator 升级的影响，在确认 TiDB Operator 新版本稳定工作后，再[正常升级 TiDB Operator](upgrade-tidb-operator.md)。


灰度升级功能仅支持 [tidb-controller-manager](architecture.md) 和 [tidb-scheduler](tidb-scheduler.md)，不支持[增强型 StatefulSet 控制器](advanced-statefulset.md)和[准入控制器](enable-admission-webhook.md)。

在使用 TiDB Operator 时，`tidb-scheduler` 并不是必须使用。你可以参考 [tidb-scheduler 与 default-scheduler](tidb-scheduler.md#tidb-scheduler-与-default-scheduler)，确认是否需要部署 `tidb-scheduler`。

本文介绍如何灰度升级 TiDB Operator。

## 第 1 步：为当前 TiDB Operator 配置 selector

参考[升级 TiDB Operator 文档](upgrade-tidb-operator.md)，在 `values.yaml` 中添加如下配置，升级当前 TiDB Operator：

```yaml
controllerManager:
  selector:
  - version!=canary
```

## 第 2 步：部署灰度的 TiDB Operator

1. 参考[部署 TiDB Operator 文档](deploy-tidb-operator.md)，在 `values.yaml` 中添加如下配置。

    ```yaml
    controllerManager:
      selector:
      - version=canary
    appendReleaseSuffix: true
    #scheduler:
    #  create: false # 如果你不需要 `tidb-scheduler`，将这个值设置为 false
    advancedStatefulset:
      create: false
    admissionWebhook:
      create: false
    ```

    `appendReleaseSuffix` 需要设置为 `true`。

    如果不需要灰度升级 tidb-scheduler，可以设置 `scheduler.create: false`。如果需要灰度升级 tidb-scheduler，配置 `scheduler.create: true`，会创建一个名字为 `{{ .scheduler.schedulerName }}-{{.Release.Name}}` 的 scheduler。如果要在灰度部署的 TiDB Operator 中使用这个 scheduler，需要配置 TidbCluster CR 中的 `spec.schedulerName` 为这个 scheduler 的名字。

    由于灰度升级不支持增强型 StatefulSet 控制器和准入控制器，必须配置 `advancedStatefulset.create: false` 和 `admissionWebhook.create: false`。

    如需了解灰度部署相关参数的详细信息，可参考[使用多套 TiDB Operator 单独管理不同的 TiDB 集群 - 相关参数](deploy-multiple-tidb-operator.md#相关参数)。

2. 在**不同的 namespace** 中（例如 `tidb-admin-canary`），使用**不同的 [Helm Release Name](https://helm.sh/docs/intro/using_helm/#three-big-concepts)**（例如 `helm install tidb-operator-canary ...`）部署灰度的 TiDB Operator：

    ```bash
    helm upgrade tidb-operator pingcap/tidb-operator --version=${operator_version} -f ${HOME}/tidb-operator/${operator_version}/values-tidb-operator.yaml
    ```

    将 `${operator_version}` 替换为你需要灰度升级到的 TiDB Operator 版本号。

    建议在单独的 namespace 部署新的 TiDB Operator。

## 第 3 步：测试灰度的 TiDB Operator (可选)

在正常升级 TiDB Operator 前，可以测试灰度部署的 TiDB Operator 是否稳定工作。支持测试的组件有 tidb-controller-manager 和 tidb-scheduler。

1. 如果需要测试灰度部署的 tidb-controller-manager，可通过如下命令，为某个 TiDB 集群设置 label：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl -n ${namespace} label tc ${cluster_name} version=canary
    ```

    通过查看已经部署的两个 tidb-controller-manager 的日志，可以确认这个设置 label 的 TiDB 集群已经由灰度部署的 TiDB Operator 管理。查看日志的步骤如下：

    1. 查看当前 TiDB Operator 的 tidb-controller-manager 的日志:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl -n tidb-admin logs tidb-controller-manager-55b887bdc9-lzdwv
        ```

        预期的输出如下：

        ```
        I0305 07:52:04.558973       1 tidb_cluster_controller.go:148] TidbCluster has been deleted tidb-cluster-1/basic1
        ```

    2. 查看灰度部署的 TiDB Operator 的 tidb-controller-manager 的日志:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl -n tidb-admin-canary logs tidb-controller-manager-canary-6dcb9bdd95-qf4qr
        ```

        预期的输出如下：

        ```
        I0113 03:38:43.859387       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic1] updated successfully
        ```

2. 如果需要测试灰度部署的 tidb-scheduler，可通过如下命令，为某个 TiDB 集群修改 `spec.schedulerName` 为 `tidb-scheduler-canary`：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl -n ${namespace} edit tc ${cluster_name}
    ```

    修改后，集群内各组件会滚动升级，通过查看灰度部署的 TiDB Operator 的 `tidb-scheduler` 的日志，可以确认集群已经使用灰度 `tidb-scheduler`：

    ```bash
    kubectl -n tidb-admin-canary logs tidb-scheduler-canary-7f7b6c7c6-j5p2j -c tidb-scheduler
    ```

3. 测试完成后，可撤销前两步中的修改，重新使用当前的 TiDB Operator 来管理 TiDB 集群。

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl -n ${namespace} label tc ${cluster_name} version-
    ```

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl -n ${namespace} edit tc ${cluster_name}
    ```

## 第 4 步：正常升级 TiDB Operator

确认灰度部署的 TiDB Operator 已经正常工作后，可以正常升级 TiDB Operator。

1. 删除灰度部署的 TiDB Operator：

    ```bash
    helm -n tidb-admin-canary uninstall ${release_name}
    ```

2. 正常[升级 TiDB Operator](upgrade-tidb-operator.md)。
