---
title: 在 Kubernetes 上部署 TiDB HTAP 存储引擎 TiFlash
summary: 了解如何在 Kubernetes 上部署 TiDB HTAP 存储引擎 TiFlash。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/deploy-tiflash/']
---

# 在 Kubernetes 上部署 TiDB HTAP 存储引擎 TiFlash

本文介绍在现有的 TiDB 集群上如何新增或删除 TiDB HTAP 存储引擎 TiFlash。

TiFlash 是 TiKV 的列存扩展，在提供了良好的隔离性的同时，也兼顾了与 TiKV 的强一致性，适用于 HTAP 场景（例如，在线实时分析处理的混合负载场景、实时流处理场景、或者数据中枢场景）。

> **注意**:
>
> 如果尚未部署 TiDB 集群, 你可以在[配置 TiDB 集群](configure-a-tidb-cluster.md)时增加 TiFlash 相关配置，然后[部署 TiDB 集群](deploy-on-general-kubernetes.md)，因此无需参考本文。

## 前置条件

* TiDB Operator [部署](deploy-tidb-operator.md)完成。

## 在现有 TiDB 集群上新增 TiFlash 组件

当 TiDB 集群已经部署完成时，如果你需要在现有 TiDB 集群上新增 TiFlash 组件，请进行以下操作：

> **注意:**
>
> 如果服务器没有外网，请参考[部署 TiDB 集群](deploy-on-general-kubernetes.md#部署-tidb-集群)在有外网的机器上将 `pingcap/tiflash` Docker 镜像下载下来并上传到服务器上, 然后使用 `docker load` 将 Docker 镜像安装到服务器上。

1. 编辑 TidbCluster Custom Resource (CR)：

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. 按照如下示例增加 TiFlash 配置：

    ```yaml
    spec:
    tiflash:
        #如果要部署企业版的 TiFlash, 请修改 `baseImage` 的值为 `pingcap/tiflash-enterprise`。
        baseImage: pingcap/tiflash
        maxFailoverCount: 0
        replicas: 1
        storageClaims:
        - resources:
            requests:
              storage: 100Gi
        storageClassName: local-storage
    ```

3. TiFlash 支持挂载多个 PV。如果要为 TiFlash 配置多个 PV，可以在 `tiflash.storageClaims` 下面配置多个 `resources` 项，每个 `resources` 项可以分别配置 `storage request` 和 `storageClassName`，例如：

    ```yaml
    tiflash:
        baseImage: pingcap/tiflash
        maxFailoverCount: 0
        replicas: 1
        storageClaims:
        - resources:
            requests:
                storage: 100Gi
        storageClassName: local-storage
        - resources:
            requests:
                storage: 100Gi
        storageClassName: local-storage
    ```

    > **注意**:
    >
    > - 建议第一次部署 TiFlash 时规划好使用几个 PV，配置好 `storageClaims` 中`resources` 项的个数。
    > - 当 TiFlash 组件部署完成后，如果你需要为 TiFlash 挂载额外的 PV，直接更新 `storageClaims` 添加磁盘不会生效。因为 TiDB Operator 是通过创建 [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) 管理 TiFlash 的，而 `StatefulSet` 创建后不支持修改 `volumeClaimTemplates`。

4. 配置 TidbCluster CR 中 `spec.tiflash.config` 的相关参数。例如：

    ```yaml
    spec:
    tiflash:
        config:
        config: |
            [flash]
            [flash.flash_cluster]
                log = "/data0/logs/flash_cluster_manager.log"
            [logger]
            count = 10
            level = "information"
            errorlog = "/data0/logs/error.log"
            log = "/data0/logs/server.log"
    ```

    要获取所有可配置的 TiFlash 配置参数，请参考 [TiFlash 配置文档](https://pingcap.com/docs-cn/stable/tiflash/tiflash-configuration/)。

    > **注意:**
    >
    > 针对不同 TiFlash 版本，请注意以下不同配置：
    >
    > - 如果 TiFlash 版本 <= v4.0.4，需要在 TidbCluster CR 中设置 `spec.tiflash.config.config.flash.service_addr` 为 `${clusterName}-tiflash-POD_NUM.${clusterName}-tiflash-peer.${namespace}.svc:3930`。其中，`${clusterName}` 和 `${namespace}` 需要根据实际情况替换。
    > - 如果 TiFlash 版本 >= v4.0.5，不需要手动配置 `spec.tiflash.config.config.flash.service_addr`。
    > - 如果从小于等于 v4.0.4 的 TiFlash 版本升级到大于等于 v4.0.5 TiFlash 版本，需要删除 TidbCluster CR 中 `spec.tiflash.config.config.flash.service_addr` 的配置。

当 TiFlash 组件部署完成后，如果要为 TiFlash 新增 PV，你需要在更新 `storageClaims` 添加磁盘后，手动删除 TiFlash StatefulSet。具体操作如下：

> **警告**:
>
> 删除 TiFlash StatefulSet 将会导致 TiFlash 集群在删除期间不可用并影响相关业务，请谨慎选择是否要进行以下操作。

1. 编辑 TidbCluster Custom Resource：

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. TiDB Operator 会按照 `storageClaims` 列表中的配置**按顺序**自动挂载 PV，如果需要为 TiFlash 增加 `resources` 项，请确保只在列表原有配置**最后添加**，并且**不能**修改列表中原有配置的顺序。例如：

    ```yaml
    tiflash:
        baseImage: pingcap/tiflash
        maxFailoverCount: 0
        replicas: 1
        storageClaims:
        - resources:
            requests:
                storage: 100Gi
        storageClassName: local-storage
        - resources:
            requests:
                storage: 100Gi
        storageClassName: local-storage
        - resources: #新增
            requests:  #新增
                storage: 100Gi  #新增
        storageClassName: local-storage  #新增
    ```

3. 手动删除 TiFlash StatefulSet，等待 TiDB Operator 重新创建 TiFlash StatefulSet。

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl delete sts -n ${namespace} ${cluster_name}-tiflash
    ```

## 移除 TiFlash

如果你的 TiDB 集群不再需要 TiDB HTAP 存储引擎 TiFlash，请进行以下操作移除 TiFlash。

1. 调整同步到 TiFlash 集群中的数据表的副本数。

    需要将集群中所有同步到 TiFlash 的数据表的副本数都设置为 0，才能完全移除 TiFlash。

    1. 参考[访问 TiDB 集群](access-tidb.md)的步骤连接到 TiDB 服务。

    2. 使用以下命令，调整同步到 TiFlash 集群中的数据表的副本数：

        {{< copyable "sql" >}}

        ```sql
        alter table <db_name>.<table_name> set tiflash replica 0;
        ```

2. 等待相关表的 TiFlash 副本被删除。

    连接到 TiDB 服务，执行如下命令，查不到相关表的同步信息时即为副本被删除：

    {{< copyable "sql" >}}

    ```sql
    SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>';
    ```

3. 执行以下命令修改 `spec.tiflash.replicas` 为 0 来移除 TiFlash Pod。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tidbcluster ${cluster_name} -n ${namespace}
    ```

4. 检查 TiFlash Pod 和 TiFlash 节点 store 状态。

    1. 执行以下命令检查 TiFlash Pod 是否被成功删除：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pod -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

        如果输出为空，则表示 TiFlash 集群的 Pod 已经被成功删除。

    2. 使用以下命令检查 TiFlash 节点 store 状态是否为 Tombstone:

        ```shell
        kubectl get tidbcluster ${cluster_name} -n ${namespace} -o yaml
        ```

        输出结果中的 `status.tiflash` 字段值类似下方实例。

        ```
        tiflash:
            ...
            tombstoneStores:
            "88":
                id: "88"
                ip: basic-tiflash-0.basic-tiflash-peer.default.svc
                lastHeartbeatTime: "2020-12-31T04:42:12Z"
                lastTransitionTime: null
                leaderCount: 0
                podName: basic-tiflash-0
                state: Tombstone
            "89":
                id: "89"
                ip: basic-tiflash-1.basic-tiflash-peer.default.svc
                lastHeartbeatTime: "2020-12-31T04:41:50Z"
                lastTransitionTime: null
                leaderCount: 0
                podName: basic-tiflash-1
                state: Tombstone
        ```

        只有 TiFlash 集群的所有 Pod 已经被成功删除并且所有 TiFlash 节点 store 状态都变为 Tombstone 后，才能进行下一步操作。

5. 删除 TiFlash StatefulSet。

    1. 使用以下命令修改 TiDB Cluster CR，删除 `spec.tiflash` 字段。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl edit tidbcluster ${cluster_name} -n ${namespace}
        ```

    2. 使用以下命令删除 TiFlash StatefulSet：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl delete statefulsets -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

    3. 执行以下命令检查是否成功删除 TiFlash 集群的 StatefulSet：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get sts -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

        如果输出为空，则表示 TiFlash 集群的 StatefulSet 已经被成功删除。

6. (可选项) 删除 PVC 和 PV。

    如果确认 TiFlash 中的数据不会被使用，想要删除数据，需要严格按照以下操作步骤来删除 TiFlash 中的数据。

    1. 删除 PV 对应的 PVC 对象

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl delete pvc -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

    2. PV 保留策略是 Retain 时，删除 PVC 对象后对应的 PV 仍将保留。如果想要删除 PV，可以设置 PV 的保留策略为 Delete，PV 会被自动删除并回收。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl patch pv ${pv_name} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
        ```

        其中 `${pv_name}` 表示 TiFlash 集群 PV 的名称，可以执行以下命令查看：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pv -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```