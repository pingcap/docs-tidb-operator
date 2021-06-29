---
title: TiCDC 组件同步数据到开启 TLS 的下游服务
summary: 了解如何让 TiCDC 组件同步数据到开启 TLS 的下游服务
---

# TiCDC 组件同步数据到开启 TLS 的下游服务

下面主要介绍在 Kubernetes 上如何让 TiCDC 组件同步数据到开启 TLS 的下游服务。

## 开始之前

你需要部署一个下游服务，并开启了客户端 TLS 认证。

你需要生成客户端访问下游服务所需要的密钥文件。

## TiCDC 同步数据到开启 TLS 的下游服务

1. 创建包含访问下游服务的客户端 TLS 证书的 Kubernetes Secret 对象。数据来自于你为客户端生成的密钥文件。
    
    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${cluster_namespace} --from-file=tls.crt=client.pem --from-file=tls.key=client-key.pem --from-file=ca.crt=ca.pem
    ```

2. 设置 TidbCluster 中的 `spec.ticdc.tlsClientSecretNames` 字段，挂载 Secret 对象到 TiCDC 的 Pod。

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

4. 通过 `cdc cli` 工具创建同步任务。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec ${cluster_name}-ticdc-0 -- /cdc cli changefeed create --pd=http://${cluster_name}-pd-0.${cluster_name}-pd-peer:2379 --sink-uri="mysql://${user}:{$password}@${downstream_service}/?ssl-ca=/var/lib/sink-tls/${secret_name}/ca.crt&ssl-cert=/var/lib/sink-tls/${secret_name}/tls.crt&ssl-key=/var/lib/sink-tls/${secret_name}/tls.key"
    ```
