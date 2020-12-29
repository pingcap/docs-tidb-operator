---
title: 在 Kubernetes 上部署 TiFlash
summary: 了解如何在 Kubernetes 上部署 TiFlash。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/deploy-tiflash/']
---

# 在 Kubernetes 上部署 TiFlash

本文介绍如何在 Kubernetes 上部署 TiFlash。

## 前置条件

* TiDB Operator [部署](deploy-tidb-operator.md)完成。

## 全新部署 TiDB 集群同时部署 TiFlash

参考 [在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)进行部署。

## 在现有 TiDB 集群上新增 TiFlash 组件

编辑 TidbCluster Custom Resource：

{{< copyable "shell-regular" >}}

``` shell
kubectl edit tc ${cluster_name} -n ${namespace}
```

按照如下示例增加 TiFlash 配置：

```yaml
spec:
  tiflash:
    baseImage: pingcap/tiflash
    maxFailoverCount: 3
    replicas: 1
    storageClaims:
    - resources:
        requests:
          storage: 100Gi
      storageClassName: local-storage
```

其他参数可以参考[集群配置文档](configure-a-tidb-cluster.md)进行配置。

值得注意的是，如果需要部署企业版的 TiFlash，需要将 db.yaml 中 `spec.tiflash.baseImage` 配置为企业版镜像，格式为 `pingcap/tiflash-enterprise`。

例如:

```yaml
spec:
  tiflash:
    baseImage: pingcap/tiflash-enterprise
```

TiFlash 支持挂载多个 PV，如果要为 TiFlash 配置多个 PV，可以在 `tiflash.storageClaims` 下面配置多项，每一项可以分别配置 `storage reqeust` 和 `storageClassName`，例如：

```yaml
  tiflash:
    baseImage: pingcap/tiflash
    maxFailoverCount: 3
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

> **警告：**
>
> 由于 TiDB Operator 会按照 `storageClaims` 列表中的配置**按顺序**自动挂载 PV，如果需要为 TiFlash 增加磁盘，请确保只在列表原有配置**最后添加**，并且**不能**修改列表中原有配置的顺序。

新增部署 TiFlash 需要 PD 配置 `replication.enable-placement-rules: true`，通过上述步骤在 TidbCluster 中增加 TiFlash 配置后，TiDB Operator 会自动为 PD 配置 `replication.enable-placement-rules: true`。

如果服务器没有外网，请参考[部署 TiDB 集群](deploy-on-general-kubernetes.md#部署-tidb-集群)在有外网的机器上将用到的 Docker 镜像下载下来并上传到服务器上。

## 移除 TiFlash

1. 删除同步到 TiFlash 的数据表。

    由于移除 TiFlash 后，TiFlash 集群剩余 Pod 数将为0，因此需要将 TiFlash 集群中所有同步数据表的副本数都置为0，才能完全移除 TiFlash。
    
    1. 参考[访问 TiDB 集群](access-tidb.md)的步骤连接到 TiDB 服务，并使用以下命令删除 同步到 TiFlash 集群中的数据表。

    2. 使用以下命令，删除同步到 TiFlash 集群中的数据表：

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

3. 删除 TiFlash 同步数据表后，使用以下命令修改 `spec.tiflash.replicas` 为 0 来移除 TiFlash。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tidbcluster ${cluster_name}
    ```

4. 检查是否成功移除 TiFlash

    检查 TiFlash 集群的 statefulSet 和 Pod 是否被删除。

    执行以下命令查看 TiFlash 集群的 statefulSet：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get sts -n ${namespace} -l app.kubernetes.io/component=tiflash
    ```

    输出类似如下结果，可见 TiFlash 集群的 statefulSet 数为 0，表示 TiFlash 集群的 statefulSet 已被成功移除。

    ```
    NAME            READY   AGE
    basic-tiflash   0/0     5d
    ```

    执行以下命令查看 Kubernetes 集群的 Pod：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod -n ${namespace} -l app.kubernetes.io/component=tiflash
    ```

    如果输出为空，则表示 TiFlash 集群的 Pod 已经被成功删除。

5. (可选项) 删除 PVC 和 PV

    如果确认 TiFlash 中的数据不会被使用，想要删除数据。需要严格按照以下操作步骤来删除 TiFlash 中的数据。

    1. 删除 PV 对应的 PVC 对象

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl delete pvc ${pvc_name} --namespace=${namespace}
        ```

        其中 `${pvc_name}` 表示 TiFlash 集群 PVC 的名称，可以执行以下命令查看：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pvc --namespace=${namespace} -l app.kubernetes.io/component=tiflash
        ```

    2. PV 保留策略是 Retain 时，删除 PVC 对象后对应的 PV 仍将保留。如果想要删除 PV 中的数据，设置 PV 的保留策略为 Delete，PV 会被自动删除并回收。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl patch pv ${pv_name} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
        ```

        其中 `${pv_name}` 表示 TiFlash 集群 PV 的名称，可以执行以下命令查看：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pv -l app.kubernetes.io/component=tiflash
        ```

## 不同版本配置注意事项

从 TiDB Operator v1.1.5 版本开始，`spec.tiflash.config.config.flash.service_addr` 的默认配置从 `${clusterName}-tiflash-POD_NUM.${clusterName}-tiflash-peer.${namespace}.svc:3930` 修改为 `0.0.0.0:3930`，而 TiFlash 从 v4.0.5 开始需要配置 `spec.tiflash.config.config.flash.service_addr` 为 `0.0.0.0:3930`，因此针对不同 TiFlash 和 TiDB Operator 版本，需要注意以下配置：

* 如果 TiDB Operator 版本 <= v1.1.4
    * 如果 TiFlash 版本 <= v4.0.4，不需要手动配置 `spec.tiflash.config.config.flash.service_addr`。
    * 如果 TiFlash 版本 >= v4.0.5，需要在 TidbCluster CR 中设置 `spec.tiflash.config.config.flash.service_addr` 为 `0.0.0.0:3930`。
* 如果 TiDB Operator 版本 >= v1.1.5
    * 如果 TiFlash 版本 <= v4.0.4，需要在 TidbCluster CR 中设置 `spec.tiflash.config.config.flash.service_addr` 为 `${clusterName}-tiflash-POD_NUM.${clusterName}-tiflash-peer.${namespace}.svc:3930`。其中，`${clusterName}` 和 `${namespace}` 需要根据实际情况替换。
    * 如果 TiFlash 版本 >= v4.0.5，不需要手动配置 `spec.tiflash.config.config.flash.service_addr`。
    * 如果从小于等于 v4.0.4 的 TiFlash 版本升级到大于等于 v4.0.5 TiFlash 版本，需要删除 TidbCluster CR 中 `spec.tiflash.config.config.flash.service_addr` 的配置。
