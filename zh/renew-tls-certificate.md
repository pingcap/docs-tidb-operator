---
title: 更新和替换 TLS 证书
summary: 介绍如何更新和替换 TiDB 组件间的 TLS 证书。
---

# 更新和替换 TLS 证书

本文以更新和替换 TiDB 集群中 PD、TiKV、TiDB 组件间的 TLS 证书为例，介绍在证书过期之前，如何更新和替换相应组件的证书。

如需要更新和替换集群中其他组件间的证书、TiDB Server 端证书或 MySQL Client 端证书，可使用类似的步骤进行操作。

本文的更新和替换操作假定原证书尚未过期。若原证书已经过期或失效，可参考[为 TiDB 组件间开启 TLS](enable-tls-between-components.md) 或[为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md) 生成新的证书并重启集群。

## 更新和替换 `cert-manager` 颁发的证书

如原 TLS 证书是[使用 `cert-manager` 系统颁发的证书](enable-tls-between-components.md#使用-cert-manager-系统颁发证书)，且原证书尚未过期，根据是否需要更新 CA 证书需要分别处理。

### 更新和替换 CA 证书及组件间证书

使用 cert-manager 颁发证书时，通过指定 `Certificate` 资源的 `spec.renewBefore` 可由 cert-manager 在证书过期之前自动进行更新。

但 cert-manager 虽然能自动更新 CA 证书及对应的 Kubernetes Secret 对象，但目前并不支持将新旧 CA 证书合并为组合 CA 证书以同时接受新旧 CA 证书签发的证书。因此，在更新和替换 CA 证书的过程中，会出现集群组件间 TLS 无法互相认证的问题。

> **警告：**
>
> 由于组件间无法同时接受新旧 CA 签发的证书，因此在更新和替换证书的过程中需要重建部分组件的 Pod，这可能会引起部分访问 TiDB 集群的请求失败。

相应的更新和替换 PD、TiKV、TiDB 的 CA 证书及组件间证书的步骤如下。

1. 由 cert-manager 在证书过期之前自动更新 CA 证书及 Kubernetes Secret 对象 `${cluster_name}-ca-secret`。

    其中 `${cluster_name}` 为集群的名字。

    若要手动更新 CA 证书，可直接删除相应的 Kubernetes Secret 对象后触发 cert-manager 重新生成 CA 证书。

2. 删除各组件对应证书的 Kubernetes Secret 对象。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete secret ${cluster_name}-pd-cluster-secret --namespace=${namespace}
    kubectl delete secret ${cluster_name}-tikv-cluster-secret --namespace=${namespace}
    kubectl delete secret ${cluster_name}-tidb-cluster-secret --namespace=${namespace}
    kubectl delete secret ${cluster_name}-cluster-client-secret --namespace=${namespace}
    ```

    其中 `${cluster_name}` 为集群的名字，`${namespace}` 为 TiDB 集群部署的命名空间。

3. 等待 cert-manager 基于新的 CA 证书为各组件颁发新的证书。

    观察 `kubectl get secret --namespace=${namespace}` 的输出，直到所有组件对应的 Kubernetes Secret 对象都被创建。

4. 依次强制重建 PD、TiKV 与 TiDB 组件 Pod。

    由于 cert-manager 不支持组合 CA 证书，若尝试滚动升级各组件，则使用新旧不同 CA 签发证书的 Pod 间将无法基于 TLS 正常通信。因此需要强制删除 Pod 并通过基于新 CA 签发的证书重建 Pod。

    {{< copyable "shell-regular" >}}

    ```
    kubectl delete -n ${namespace} pod ${pod_name}
    ```

    其中 `${namespace}` 为 TiDB 集群部署的命名空间，`${pod_name}` 为 PD、TiKV 与 TiDB 各 replica 的 Pod 名称。

### 仅更新和替换组件间证书

1. 由 cert-manager 在证书过期之前自动更新各组件的证书及 Kubernetes Secret 对象。

    对于 PD、TiKV 及 TiDB 组件，在 TiDB 集群部署的命名空间下包含以下 Kubernetes Secret 对象：

    {{< copyable "shell-regular" >}}

    ```
    ${cluster_name}-pd-cluster-secret
    ${cluster_name}-tikv-cluster-secret
    ${cluster_name}-tidb-cluster-secret
    ${cluster_name}-cluster-client-secret
    ```

    其中 `${cluster_name}` 为集群的名字。

    若要手动更新组件间证书，可直接删除相应的 Kubernetes Secret 对象后触发 cert-manager 重新生成组件间证书。

2. 对于各组件间的证书，各组件会在之后新建连接时自动重新加载新的证书，无需手动操作。

    > **注意：**
    >
    > - 各组件目前[暂不支持 CA 证书的自动重新加载](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-components#证书重加载)，需要参考[更新和替换 CA 证书及组件间证书](#更新和替换-ca-证书及组件间证书)进行处理。
    > - 对于 TiDB Server 端证书，可参考以下任意方式进行手动重加载：
    >     - 参考[重加载证书、密钥和 CA](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers#重加载证书密钥和-ca)。
    >     - 参考[滚动重启 TiDB 集群](restart-a-tidb-cluster.md)对 TiDB Server 进行滚动重启。
