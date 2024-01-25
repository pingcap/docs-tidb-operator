---
title: 为已有 TiDB 集群部署负载均衡 TiProxy
summary: 了解如何在 Kubernetes 上为已有 TiDB 集群部署负载均衡 TiProxy。
---

# 为已有 TiDB 集群部署负载均衡 TiProxy

本文介绍在 Kubernetes 上如何为已有的 TiDB 集群部署或删除 TiDB 负载均衡 [TiProxy](https://docs.pingcap.com/zh/tidb/v7.6/tiproxy-overview)。TiProxy 放置在客户端和 TiDB server 之间，为 TiDB 提供负载均衡、连接保持、服务发现等功能。

> **注意：**
>
> 如果尚未部署 TiDB 集群, 你可以在[配置 TiDB 集群](configure-a-tidb-cluster.md)时增加 TiProxy 相关配置，然后[部署 TiDB 集群](deploy-on-general-kubernetes.md)，因此无需参考本文。

## 部署 TiProxy

如果你需要在现有的 TiDB 集群上部署 TiProxy 组件，请进行以下操作：

> **注意：**
>
> 如果服务器没有外网，请参考[部署 TiDB 集群](deploy-on-general-kubernetes.md#部署-tidb-集群)在有外网的机器上将 `pingcap/tiproxy` Docker 镜像下载下来并上传到服务器上, 然后使用 `docker load` 将 Docker 镜像安装到服务器上。

1. 编辑 TidbCluster Custom Resource (CR)：

    ``` shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. 按照如下示例增加 TiProxy 配置：

    ```yaml
    spec:
      tiproxy:
        baseImage: pingcap/tiproxy
        replicas: 3
    ```

3. 配置 TidbCluster CR 中 `spec.tiproxy.config` 的相关参数。例如：

    ```yaml
    spec:
      tiproxy:
        config: |
          [log]
          level = "info"
    ```

    要获取更多可配置的 TiProxy 配置参数，请参考 [TiProxy 配置文档](https://docs.pingcap.com/zh/tidb/v7.6/tiproxy-configuration)。

4. 配置 TidbCluster CR 中 `spec.tidb` 的相关参数：

    + 推荐设置 TiDB `graceful-wait-before-shutdown` 的值大于应用程序中事务的最长的持续时间，配合 TiProxy 的连接迁移。详见 [TiProxy 使用限制](https://docs.pingcap.com/zh/tidb/v7.6/tiproxy-overview#使用限制)。

       ```yaml
       spec:
         tidb:
           config: |
             graceful-wait-before-shutdown = 30
       ```

    + 如果开启了[集群 TLS](enable-tls-between-components.md)，则跳过这一步；如果没有开启集群 TLS，还需要生成自签名证书，并手动配置 TiDB 的 [`session-token-signing-cert`](https://docs.pingcap.com/zh/tidb/stable/tidb-configuration-file#session-token-signing-cert-从-v640-版本开始引入) 和 [`session-token-signing-key`](https://docs.pingcap.com/zh/tidb/stable/tidb-configuration-file#session-token-signing-key-从-v640-版本开始引入)：

        ```yaml
        spec:
          tidb:
            additionalVolumes:
              - name: sessioncert
                secret:
                  secretName: sessioncert-secret
            additionalVolumeMounts:
              - name: sessioncert
                mountPath: /var/session
            config: |
              session-token-signing-cert = "/var/session/tls.crt"
              session-token-signing-key = "/var/session/tls.key"
        ```

       详见 [`session-token-signing-key`](https://docs.pingcap.com/zh/tidb/v7.6/tidb-configuration-file#session-token-signing-cert-从-v640-版本开始引入)。

TiProxy 启动后，可通过以下命令找到对应的 `tiproxy-sql` 负载均衡服务。

``` shell
kubectl get svc -n ${namespace}
```

## 移除 TiProxy

如果你的 TiDB 集群不再需要 TiProxy，执行以下操作移除。

1. 执行以下命令修改 `spec.tiproxy.replicas` 为 `0` 来移除 TiProxy Pod。

    ```shell
    kubectl patch tidbcluster ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"tiproxy":{"replicas": 0}}}'
    ```

2. 检查 TiProxy Pod 状态。

    ```shell
    kubectl get pod -n ${namespace} -l app.kubernetes.io/component=tiproxy,app.kubernetes.io/instance=${cluster_name}
    ```

    如果输出为空，则表示 TiProxy 集群的 Pod 已经被成功删除。

3. 删除 TiProxy StatefulSet。

    1. 使用以下命令修改 TiDB Cluster CR，删除 `spec.tiproxy` 字段。

        ```shell
        kubectl patch tidbcluster ${cluster_name} -n ${namespace} --type json -p '[{"op":"remove", "path":"/spec/tiproxy"}]'
        ```

    2. 使用以下命令删除 TiProxy StatefulSet：

        ```shell
        kubectl delete statefulsets -n ${namespace} -l app.kubernetes.io/component=tiproxy,app.kubernetes.io/instance=${cluster_name}
        ```

    3. 执行以下命令，检查是否已经成功删除 TiProxy 集群的 StatefulSet：

        ```shell
        kubectl get sts -n ${namespace} -l app.kubernetes.io/component=tiproxy,app.kubernetes.io/instance=${cluster_name}
        ```

        如果输出为空，则表示 TiProxy 集群的 StatefulSet 已经被成功删除。
