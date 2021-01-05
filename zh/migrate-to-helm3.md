---
title: 从 Helm2 迁移到 Helm3
summary: 介绍如何将由 Helm2 管理的 TiDB Operator 迁移到由 Helm3 管理。
---

# 从 Helm2 迁移到 Helm3

本文介绍如何将由 Helm2 管理的 TiDB Operator 迁移到由 Helm3 进行管理，有关如何将 Helm2 管理的 release 迁移的 Helm3，可参考 [Helm 官方文档](https://helm.sh/docs/topics/v2_v3_migration/)。

其他如 TiDB Lightning 等由 Helm2 管理的 release 可使用类似的步骤进行迁移。

## 迁移步骤

假设原来由 Helm2 管理的 TiDB Operator 安装在 `tidb-admin` namespace 下，名称为 `tidb-operator`。

{{< copyable "shell-regular" >}}

```shell
helm list
```

```
NAME            REVISION        UPDATED                         STATUS          CHART                   APP VERSION     NAMESPACE
tidb-operator   1               Tue Jan  5 15:28:00 2021        DEPLOYED        tidb-operator-v1.1.8    v1.1.8          tidb-admin
```

1. [参考 Helm 官方文档安装 Helm3](https://helm.sh/docs/intro/install/)。

    Helm3 使用与 Helm2 不同的配置与数据存储方式，因此在安装 Helm3 的过程中无需担心对原有配置或数据的覆盖。

    > **注意：**
    >
    > 安装过程中需避免 Helm3 的 CLI binary 覆盖 Helm2 的 CLI binary。如可将 Helm3 的 CLI binary 命名为 `heml3`（本文后续示例命令中将使用 `helm3`）。

2. 为 Helm3 安装 [helm-2to3 插件](https://github.com/helm/helm-2to3)。

    {{< copyable "shell-regular" >}}

    ```shell
    helm3 plugin install https://github.com/helm/helm-2to3
    ```

    通过如下命令可确认是否已正确安装 helm-2to3 插件。

    {{< copyable "shell-regular" >}}

    ```shell
    helm3 plugin list
    ```

    ```
    NAME    VERSION DESCRIPTION
    2to3    0.8.0   migrate and cleanup Helm v2 configuration and releases in-place to Helm v3
    ```

3. 迁移 Helm2 的仓库、插件等配置到 Helm3。

    {{< copyable "shell-regular" >}}

    ```shell
    helm3 2to3 move config
    ```

    在正式迁移配置前，可使用 `helm3 2to3 move config --dry-run` 了解可能执行的操作及其影响。

    迁移配置完成后，可看到 Helm3 中已包含 PingCAP 仓库。

    {{< copyable "shell-regular" >}}

    ```shell
    helm3 repo list
    ```

    ```
    NAME    URL
    pingcap https://charts.pingcap.org/
    ```

4. 迁移 Helm2 管理的 release 到 Helm3。

    {{< copyable "shell-regular" >}}

    ```shell
    helm3 2to3 convert tidb-operator
    ```

    在正式迁移 release 前，可使用 `helm3 2to3 convert tidb-operator --dry-run` 了解可能执行的操作及其影响。

    迁移 release 完成后，可通过 Helm3 看到 TiDB Operator 对应的 release。

    {{< copyable "shell-regular" >}}

    ```shell
    helm3 list --namespace=tidb-admin
    ```

    ```
    NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                   APP VERSION
    tidb-operator   tidb-admin      1               2021-01-05 07:28:00.3545941 +0000 UTC   deployed        tidb-operator-v1.1.8    v1.1.8
    ```

    > **注意：**
    >
    > 如果原 Helm2 是 Tillerless 的，则可以通过增加 `--tiller-out-cluster` 参数进行迁移，即 `helm3 2to3 convert tidb-operator --tiller-out-cluster`。

5. 确认 TiDB Operator、TidbCluster 及 TidbMonitor 运行正常。

6. 清理 Helm2 对应的配置、release 信息等数据。

    {{< copyable "shell-regular" >}}

    ```shell
    helm3 2to3 cleanup --name=tidb-operator
    ```

    在正式清理数据前，可使用 `helm3 2to3 cleanup --name=tidb-operator --dry-run` 了解可能执行的操作及其影响。

    > **注意：**
    >
    > 清理完成后，Helm2 中将无法再管理对应的 release。
