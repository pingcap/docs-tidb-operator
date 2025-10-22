---
title: 为 MySQL 客户端开启 TLS
summary: 在 Kubernetes 上如何为 TiDB 集群的 MySQL 客户端开启 TLS。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/enable-tls-for-mysql-client/']
---

# 为 MySQL 客户端开启 TLS

本文主要描述了在 Kubernetes 上如何为 TiDB 集群的 MySQL 客户端开启 TLS。TiDB Operator 从 v1.1 开始已经支持为 Kubernetes 上 TiDB 集群开启 MySQL 客户端 TLS。开启步骤为：

1. [为 TiDB Server 颁发一套 Server 端证书](#第一步为-tidb-集群颁发两套证书)，为 MySQL Client 颁发一套 Client 端证书。并创建两个 Secret 对象，Secret 名字分别为：`${cluster_name}-tidb-server-secret` 和  `${cluster_name}-tidb-client-secret`，分别包含前面创建的两套证书；

    > **注意：**
    >
    > 创建的 Secret 对象必须符合上述命名规范，否则将导致 TiDB 集群部署失败。

    其中，颁发证书的方式有多种，本文档介绍了使用 `cert-manager` 系统颁发证书。你也可以根据需要为 TiDB 集群颁发证书。

    当需要更新已有 TLS 证书时，可参考[更新和替换 TLS 证书](renew-tls-certificate.md)。

2. [部署集群](#第二步部署-tidb-集群)，设置 `.spec.tidb.tlsClient.enabled` 属性为 `true`：

    * 如需跳过作为 MySQL 客户端的内部组件（如 TidbInitializer、Dashboard、Backup、Restore）的 TLS 认证，你可以给集群对应的 `TidbCluster` 加上 `tidb.tidb.pingcap.com/skip-tls-when-connect-tidb="true"` 的 annotation。
    * 如需关闭 TiDB 服务端对客户端 CA 证书的认证，你可以设置 `.spec.tidb.tlsClient.disableClientAuthn` 属性为 `true`，即在[配置 TiDB 服务端启用安全连接](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers#配置-tidb-服务端启用安全连接) 中不设置 ssl-ca 参数。
    * 如需跳过作为 MySQL 客户端的内部组件（如 TidbInitializer、Dashboard、Backup、Restore）的 CA 证书认证，你可以设置 `.spec.tidb.tlsClient.skipInternalClientCA` 属性为 `true`。

    > **注意：**
    >
    > 已部署的集群 `.spec.tidb.tlsClient.enabled` 属性从 `false` 改为 `true`，将导致 TiDB Pod 滚动重启。

3. [配置 MySQL 客户端使用加密连接](#第三步配置-mysql-客户端使用-tls-连接)。

## 第一步：为 TiDB 集群颁发两套证书

1. 安装 cert-manager。

    请参考官网安装：[cert-manager installation on Kubernetes](https://cert-manager.io/docs/installation/)。

2. 创建一个 Issuer 用于给 TiDB 集群颁发证书。

    为了配置 `cert-manager` 颁发证书，必须先创建 Issuer 资源。

    首先创建一个目录保存 `cert-manager` 创建证书所需文件：

    ``` shell
    mkdir -p cert-manager
    cd cert-manager
    ```

    然后创建一个 `tidb-server-issuer.yaml` 文件，输入以下内容：

    ``` yaml
    apiVersion: cert-manager.io/v1
    kind: Issuer
    metadata:
      name: ${cluster_name}-selfsigned-ca-issuer
      namespace: ${namespace}
    spec:
      selfSigned: {}
    ---
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${cluster_name}-ca
      namespace: ${namespace}
    spec:
      secretName: ${cluster_name}-ca-secret
      commonName: "TiDB CA"
      isCA: true
      duration: 87600h # 10yrs
      renewBefore: 720h # 30d
      issuerRef:
        name: ${cluster_name}-selfsigned-ca-issuer
        kind: Issuer
    ---
    apiVersion: cert-manager.io/v1
    kind: Issuer
    metadata:
      name: ${cluster_name}-tidb-issuer
      namespace: ${namespace}
    spec:
      ca:
        secretName: ${cluster_name}-ca-secret
    ```

    上面的文件创建三个对象：

    - 一个 SelfSigned 类型的 Issuer 对象（用于生成 CA 类型 Issuer 所需要的 CA 证书）;
    - 一个 Certificate 对象，`isCa` 属性设置为 `true`；
    - 一个可以用于颁发 TiDB Server TLS 证书的 Issuer。

    最后执行下面的命令进行创建：

    ``` shell
    kubectl apply -f tidb-server-issuer.yaml
    ```

3. 创建 Server 端证书。

    在 `cert-manager` 中，Certificate 资源表示证书接口，该证书将由上面创建的 Issuer 颁发并保持更新。

    首先来创建 Server 端证书，创建一个 `tidb-server-cert.yaml` 文件，并输入以下内容：

    ``` yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${cluster_name}-tidb-server-secret
      namespace: ${namespace}
    spec:
      secretName: ${cluster_name}-tidb-server-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB Server"
      usages:
        - server auth
      dnsNames:
        - "${cluster_name}-tidb"
        - "${cluster_name}-tidb.${namespace}"
        - "${cluster_name}-tidb.${namespace}.svc"
        - "*.${cluster_name}-tidb"
        - "*.${cluster_name}-tidb.${namespace}"
        - "*.${cluster_name}-tidb.${namespace}.svc"
        - "*.${cluster_name}-tidb-peer"
        - "*.${cluster_name}-tidb-peer.${namespace}"
        - "*.${cluster_name}-tidb-peer.${namespace}.svc"
      ipAddresses:
        - 127.0.0.1
        - ::1
      issuerRef:
        name: ${cluster_name}-tidb-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    其中 `${cluster_name}` 为集群的名字：

    - `spec.secretName` 请设置为 `${cluster_name}-tidb-server-secret`；
    - `usages` 请添加上 `server auth`；
    - `dnsNames` 需要填写这 6 个 DNS，根据需要可以填写其他 DNS：
      - `${cluster_name}-tidb`
      - `${cluster_name}-tidb.${namespace}`
      - `${cluster_name}-tidb.${namespace}.svc`
      - `*.${cluster_name}-tidb`
      - `*.${cluster_name}-tidb.${namespace}`
      - `*.${cluster_name}-tidb.${namespace}.svc`
      - `*.${cluster_name}-tidb-peer`
      - `*.${cluster_name}-tidb-peer.${namespace}`
      - `*.${cluster_name}-tidb-peer.${namespace}.svc`
    - `ipAddresses` 需要填写这两个 IP ，根据需要可以填写其他 IP：
      - `127.0.0.1`
      - `::1`
    - `issuerRef` 请填写上面创建的 Issuer；
    - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

    通过执行下面的命令来创建证书：

    ``` shell
    kubectl apply -f tidb-server-cert.yaml
    ```

    创建这个对象以后，cert-manager 会生成一个名字为 `${cluster_name}-tidb-server-secret` 的 Secret 对象供 TiDB Server 使用。

4. 创建 Client 端证书。

    创建一个 `tidb-client-cert.yaml` 文件，并输入以下内容：

    ``` yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${cluster_name}-tidb-client-secret
      namespace: ${namespace}
    spec:
      secretName: ${cluster_name}-tidb-client-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB Client"
      usages:
        - client auth
      issuerRef:
        name: ${cluster_name}-tidb-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    其中 `${cluster_name}` 为集群的名字：

    - `spec.secretName` 请设置为 `${cluster_name}-tidb-client-secret`；
    - `usages` 请添加上 `client auth`；
    - `dnsNames` 和 `ipAddresses` 不需要填写；
    - `issuerRef` 请填写上面创建的 Issuer；
    - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

    通过执行下面的命令来创建证书：

    ``` shell
    kubectl apply -f tidb-client-cert.yaml
    ```

    创建这个对象以后，cert-manager 会生成一个名字为 `${cluster_name}-tidb-client-secret` 的 Secret 对象供 TiDB Client 使用。

5. 创建多套 Client 端证书（可选）。

    TiDB Operator 集群内部有 4 个组件需要请求 TiDB Server，当开启 TLS 验证后，这些组件可以使用证书来请求 TiDB Server，每个组件都可以使用单独的证书。这些组件有：

    - TidbInitializer
    - PD Dashboard
    - Backup（使用 Dumpling 时）
    - Restore（使用 TiDB Lightning 时）

    如需要[使用 TiDB Lightning 恢复 Kubernetes 上的集群数据](restore-data-using-tidb-lightning.md)，则也可以为其中的 TiDB Lightning 组件生成 Client 端证书。

    下面就来生成这些组件的 Client 证书。

    1. 创建一个 `tidb-components-client-cert.yaml` 文件，并输入以下内容：

        ``` yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-tidb-initializer-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-tidb-initializer-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "TiDB Initializer client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ---
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-pd-dashboard-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-pd-dashboard-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "PD Dashboard client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ---
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-backup-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-backup-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "Backup client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ---
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-restore-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-restore-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "Restore client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        其中 `${cluster_name}` 为集群的名字：

        - `spec.secretName` 请设置为 `${cluster_name}-${component}-client-secret`；
        - `usages` 请添加上 `client auth`；
        - `dnsNames` 和 `ipAddresses` 不需要填写；
        - `issuerRef` 请填写上面创建的 Issuer；
        - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

        如需要为 TiDB Lignting 组件生成 Client 端证书，则可以使用以下内容并通过在 TiDB Lightning 的 Helm Chart `values.yaml` 中设置 `tlsCluster.tlsClientSecretName` 为 `${cluster_name}-lightning-client-secret`：

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-lightning-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-lightning-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "Lightning client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ```

    2. 通过执行下面的命令来创建证书：

        ``` shell
        kubectl apply -f tidb-components-client-cert.yaml
        ```

    3. 创建这些对象以后，cert-manager 会生成 4 个 Secret 对象供上面四个组件使用。

    > **注意：**
    >
    > TiDB Server 的 TLS 兼容 MySQL 协议。当证书内容发生改变后，需要管理员手动执行 SQL 语句 `alter instance reload tls` 进行刷新。

## 第二步：部署 TiDB 集群

接下来将会创建一个 TiDB 集群，并且执行以下步骤：

- 开启 MySQL 客户端 TLS；
- 对集群进行初始化（这里创建了一个数据库 `app`）;
- 创建一个 Backup 对象对集群进行备份；
- 创建一个 Restore 对象对进群进行恢复；
- TidbInitializer，PD Dashboard，Backup 以及 Restore 分别使用单独的 Client 证书（用 `tlsClientSecretName` 指定）。

1. 创建三个 `.yaml` 文件：

    - `tidb-cluster.yaml`:

        ``` yaml
        apiVersion: pingcap.com/v1alpha1
        kind: TidbCluster
        metadata:
         name: ${cluster_name}
         namespace: ${namespace}
        spec:
         version: {{{ .tidb_version }}}
         timezone: UTC
         pvReclaimPolicy: Retain
         pd:
           baseImage: pingcap/pd
           maxFailoverCount: 0
           replicas: 1
           requests:
             storage: "10Gi"
           config: {}
           tlsClientSecretName: ${cluster_name}-pd-dashboard-client-secret
         tikv:
           baseImage: pingcap/tikv
           maxFailoverCount: 0
           replicas: 1
           requests:
             storage: "100Gi"
           config: {}
         tidb:
           baseImage: pingcap/tidb
           maxFailoverCount: 0
           replicas: 1
           service:
             type: ClusterIP
           config: {}
           tlsClient:
             enabled: true
        ---
        apiVersion: pingcap.com/v1alpha1
        kind: TidbInitializer
        metadata:
         name: ${cluster_name}-init
         namespace: ${namespace}
        spec:
         image: tnir/mysqlclient
         cluster:
           namespace: ${namespace}
           name: ${cluster_name}
         initSql: |-
           create database app;
         tlsClientSecretName: ${cluster_name}-tidb-initializer-client-secret
        ```

    - `backup.yaml`:

        ```
        apiVersion: pingcap.com/v1alpha1
        kind: Backup
        metadata:
          name: ${cluster_name}-backup
          namespace: ${namespace}
        spec:
          backupType: full
          br:
            cluster: ${cluster_name}
            clusterNamespace: ${namespace}
            sendCredToTikv: true
          s3:
            provider: aws
            region: ${my_region}
            secretName: ${s3_secret}
            bucket: ${my_bucket}
            prefix: ${my_folder}
        ```

    - `restore.yaml`:

        ```
        apiVersion: pingcap.com/v1alpha1
        kind: Restore
        metadata:
          name: ${cluster_name}-restore
          namespace: ${namespace}
        spec:
          backupType: full
          br:
            cluster: ${cluster_name}
            clusterNamespace: ${namespace}
            sendCredToTikv: true
          s3:
            provider: aws
            region: ${my_region}
            secretName: ${s3_secret}
            bucket: ${my_bucket}
            prefix: ${my_folder}
        ```

    其中 `${cluster_name}` 为集群的名字，`${namespace}` 为 TiDB 集群部署的命名空间。通过设置 `spec.tidb.tlsClient.enabled` 属性为 `true` 来开启 MySQL 客户端 TLS。

2. 部署 TiDB 集群：

    ``` shell
    kubectl apply -f tidb-cluster.yaml
    ```

3. 集群备份：

    ``` shell
    kubectl apply -f backup.yaml
    ```

4. 集群恢复：

    ``` shell
    kubectl apply -f restore.yaml
    ```

## 第三步：配置 MySQL 客户端使用 TLS 连接

可以根据[官网文档](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers#配置-mysql-client-使用安全连接)提示，使用上面创建的 Client 证书，通过下面的方法连接 TiDB 集群：

获取 Client 证书的方式并连接 TiDB Server 的方法是：

``` shell
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret -ojsonpath='{.data.tls\.crt}' | base64 --decode > client-tls.crt
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret -ojsonpath='{.data.tls\.key}' | base64 --decode > client-tls.key
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret -ojsonpath='{.data.ca\.crt}' | base64 --decode > client-ca.crt
```

``` shell
mysql --comments -uroot -p -P 4000 -h ${tidb_host} --ssl-cert=client-tls.crt --ssl-key=client-tls.key --ssl-ca=client-ca.crt
```

最后请参考[官网文档](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers#检查当前连接是否是加密连接)来验证是否正确开启了 TLS。

如果不使用 Client 证书，可以运行以下命令：

``` shell
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret  -ojsonpath='{.data.ca\.crt}'  | base64 --decode > client-ca.crt
```

``` shell
mysql --comments -uroot -p -P 4000 -h ${tidb_host} --ssl-ca=client-ca.crt
```

## 故障排查

X.509 证书存储在 Kubernetes Secret 中。可以使用类似下面的命令查看这些 Secret：

```shell
kubectl -n ${namespace} get secret
```

这些 Secret 会被挂载到容器内。可以通过查看 Pod 描述中的 **Volumes** 部分来确认挂载的卷信息：

```shell
kubectl -n ${namespace} describe pod ${podname}
```

要在容器内部检查这些 Secret 挂载情况，可以运行以下命令：

```shell
kubectl exec -n ${cluster_name} --stdin=true --tty=true ${cluster_name}-tidb-0 -c tidb -- /bin/sh
```

在容器内查看 TLS 目录的内容：

```shell
sh-5.1# ls -l /var/lib/*tls
/var/lib/tidb-server-tls:
total 0
lrwxrwxrwx. 1 root root 13 Sep 25 12:23 ca.crt -> ..data/ca.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.crt -> ..data/tls.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.key -> ..data/tls.key

/var/lib/tidb-tls:
total 0
lrwxrwxrwx. 1 root root 13 Sep 25 12:23 ca.crt -> ..data/ca.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.crt -> ..data/tls.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.key -> ..data/tls.key
```

检查 TiDB 容器日志以确认 TLS 已启用，示例命令及输出如下：

```shell
kubectl -n ${cluster_name} logs ${cluster_name}-tidb-0 -c tidb
```

```
[2025/09/25 12:23:19.739 +00:00] [INFO] [server.go:291] ["mysql protocol server secure connection is enabled"] ["client verification enabled"=true]
```

## 重新加载证书

如果使用 `cert-manager` 生成证书和密钥文件，Secret 在颁发新证书时会自动更新。

要让 TiDB 使用新的证书，需要运行 [`ALTER INSTANCE RELOAD TLS`](https://docs.pingcap.com/zh/tidb/stable/sql-statement-alter-instance#reload-tls)。

可以执行下面语句查看状态变量 `Ssl_server_not_before` 和 `Ssl_server_not_after` 来检查证书的有效期。

```sql
SHOW GLOBAL STATUS LIKE 'Ssl\_server\_not\_%';
```

```
+-----------------------+--------------------------+
| Variable_name         | Value                    |
+-----------------------+--------------------------+
| Ssl_server_not_after  | Apr 23 07:59:47 2026 UTC |
| Ssl_server_not_before | Jan 24 07:59:47 2025 UTC |
+-----------------------+--------------------------+
2 rows in set (0.011 sec)
```