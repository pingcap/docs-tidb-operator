---
title: 升级 TiDB Operator
summary: 介绍如何升级 TiDB Operator。
category: how-to
aliases: ['/docs-cn/dev/tidb-in-kubernetes/upgrade/tidb-operator/','/docs-cn/v3.1/tidb-in-kubernetes/upgrade/tidb-operator/','/docs-cn/stable/tidb-in-kubernetes/upgrade/tidb-operator/']
---

# 升级 TiDB Operator

本文介绍如何升级 TiDB Operator。

## 升级步骤

1. 更新 [CRD (Custom Resource Definition)](https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/)：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/<version>/manifests/crd.yaml && \
    kubectl get crd tidbclusters.pingcap.com
    ```

    > **注意：**
    >
    > `<version>` 在后续文档中代表 TiDB Operator 版本，例如 `v1.1.0`，可以通过 `helm search -l tidb-operator` 查看当前支持的版本。

2. 获取你要安装的 `tidb-operator` chart 中的 `values.yaml` 文件：

    {{< copyable "shell-regular" >}}

    ```shell
    mkdir -p /home/tidb/tidb-operator/<version> && \
    helm inspect values pingcap/tidb-operator --version=<version> > /home/tidb/tidb-operator/<version>/values-tidb-operator.yaml
    ```
    
3. 修改 `/home/tidb/tidb-operator/<version>/values-tidb-operator.yaml` 中 `operatorImage` 镜像版本，并将旧版本 `values.yaml` 中的自定义配置合并到 `/home/tidb/tidb-operator/<version>/values-tidb-operator.yaml`，然后执行 `helm upgrade`：

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade tidb-operator pingcap/tidb-operator --version=<version> -f /home/tidb/tidb-operator/<version>/values-tidb-operator.yaml
    ```

    > **注意：**
    >
    > TiDB Operator 升级之后，所有 TiDB 集群中的 `discovery` deployment 都会自动升级到指定的 TiDB Operator 版本。

## 升级 Kubernetes

当你的 Kubernetes 集群有版本升级，请确保 `kubeSchedulerImageTag` 与之匹配。默认情况下，这个值是由 Helm 在安装或者升级过程中生成的，要修改它你需要执行 `helm upgrade`。
