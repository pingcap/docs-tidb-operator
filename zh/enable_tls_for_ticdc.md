---
title: 为 TiCDC 开启 TLS
summary: 了解如何让 TiCDC 使用 TLS 连接访问下游服务
---

# TiCDC 开启 TLS 访问下游服务

下面主要介绍在 Kubernetes 上如何让 TiCDC 与下游服务同步时使用 TLS 连接。

## 开始之前

你需要部署一个下游服务，并开启了客户端 TLS 认证。

你需要生成客户端访问下游服务所需要的密钥文件。

## TiCDC 使用 TLS 连接访问下游服务

1. 创建下游服务客户端 TLS 的 Kubernetes Secret 对象。数据来自于你为客户端生成的密钥文件。
    
    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${cluster_namespace} --from-file=tls.crt=client.pem --from-file=tls.key=client-key.pem --from-file=ca.crt=ca.pem
    ```

2. 设置 TiDBCluster 定义中的 `spec.ticdc.tlsClientSecretNames` 字段，使得 Secret 对象被挂载到 TiCDC 的 Pod。

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
      name: ${cluster_name}
      namespace: ${cluster_namespace}
    spec:
      # ...
      ticdc:
        baseImage: pingcap/ticdc
        version: "v5.0.1"
        # ...
        tlsClientSecretNames:
        - ${secret_name}
   ```

3. 部署集群。

    TiCDC Pod 运行后，你可以在 Pod 内的 `/var/lib/sink-tls/${secret_name}` 目录找到被挂载的密钥文件。

4. 使用下面通过 cdc cli 工具使用 TLS 开启同步任务。

    {{< copyable "shell-regular" >}}

    ```shell
    pd_service=$(kubectl get tc my-tidb-cluster-dev -o=jsonpath='{.status.pd.leader.clientURL}')

    kubectl exec ${cluster_name}-ticdc-0 -- /cdc cli changefeed create --pd=http://${pd_service}:2379 - --sink-uri="mysql://${user}:{$password}@${downstream_service}/?ssl-ca=/var/lib/sink-tls/${secret_name}/ca.crt&ssl-cert=/var/lib/sink-tls/${secret_name}/tls.crt&ssl-key=/var/lib/sink-tls/${secret_name}/tls.key"
    ```

