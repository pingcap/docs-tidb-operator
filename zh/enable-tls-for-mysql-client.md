---
title: 为 MySQL 客户端开启 TLS
summary: 在 Kubernetes 上如何为 TiDB 集群的 MySQL 客户端开启 TLS。
---

# 为 MySQL 客户端开启 TLS

本文主要描述了在 Kubernetes 上如何为 TiDB 集群的 MySQL 客户端开启 TLS。开启步骤为：

1. 为 TiDB Server 颁发一套 Server 端证书，为 MySQL Client 颁发一套 Client 端证书。并创建两个 Secret 对象，Secret 名字分别为：`${tidb_group_name}-tidb-server-secret` 和 `${tidb_group_name}-tidb-client-secret`，分别包含前面创建的两套证书；

    > **注意：**
    >
    > - 创建的 Secret 对象必须符合上述命名规范，否则将导致 TiDB 集群部署失败。
    > - 显式指定 MySQL TLS Secret 的功能将在后续版本中支持。
    > - TiDB Operator v2 与 v1 的 Secret 的默认命名方式不同：
    >     - 对于 TiDB Operator v1 创建的 TiDB 集群，Secret 的默认命名为 `${cluster_name}-tidb-server-secret` 和 `${cluster_name}-tidb-client-secret`。
    >     - 在 TiDB Operator v2 中，不同的 `TiDBGroup` 支持使用不同的 TLS 证书，因此 Secret 的默认命名 `${tidb_group_name}-tidb-server-secret` 和 `${tidb_group_name}-tidb-client-secret`。

2. 部署集群，设置 `TiDBGroup` 的 `.spec.template.spec.security.tls.mysql.enabled` 属性为 `true`：

    > **注意：**
    >
    > 开启或变更已部署的 `TiDBGroup` 的 TLS 配置，将导致 TiDB Pod 滚动重启，请谨慎操作。

3. 配置 MySQL 客户端使用加密连接。

其中，颁发证书的方式有多种，本文档介绍了使用 `cert-manager` 系统颁发证书。你也可以根据需要为 TiDB 集群颁发证书。

当需要更新已有 TLS 证书时，可参考[更新和替换 TLS 证书](renew-tls-certificate.md)。

## 第一步：为 TiDB 集群颁发两套证书

1. 安装 cert-manager。

    请参考官网安装：[cert-manager installation on Kubernetes](https://docs.cert-manager.io/en/release-0.11/getting-started/install/kubernetes.html)。

2. 创建一个 Issuer，用于给 TiDB 集群颁发 MySQL TLS 证书。

    为了配置 `cert-manager` 颁发证书，必须先创建 Issuer 资源。

    首先创建一个目录保存 `cert-manager` 创建证书所需文件：

    ```shell
    mkdir -p cert-manager
    cd cert-manager
    ```

    然后创建一个 `tidb-mysql-issuer.yaml` 文件，输入以下内容：

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: Issuer
    metadata:
      name: ${cluster_name}-mysql-selfsigned-ca-issuer
      namespace: ${namespace}
    spec:
      selfSigned: {}
    ---
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${cluster_name}-mysql-ca
      namespace: ${namespace}
    spec:
      secretName: ${cluster_name}-mysql-ca-secret
      commonName: "TiDB MySQL CA"
      isCA: true
      duration: 87600h # 10yrs
      renewBefore: 720h # 30d
      issuerRef:
        name: ${cluster_name}-mysql-selfsigned-ca-issuer
        kind: Issuer
    ---
    apiVersion: cert-manager.io/v1
    kind: Issuer
    metadata:
      name: ${cluster_name}-mysql-certs-issuer
      namespace: ${namespace}
    spec:
      ca:
        secretName: ${cluster_name}-mysql-ca-secret
    ```

    上面的文件创建三个对象：

    - 一个 SelfSigned 类型的 Issuer 对象（用于生成 CA 类型 Issuer 所需要的 CA 证书）;
    - 一个 Certificate 对象，`isCa` 属性设置为 `true`；
    - 一个可以用于颁发 TiDB Server 和 MySQL Client TLS 证书的 Issuer。

    MySQL TLS CA 和 Issuer 的名称与[为 TiDB 组件间开启 TLS](enable-tls-between-components.md)所用对象的名称不同。不要为 MySQL TLS 复用组件间 CA 或 Issuer。MySQL 客户端私钥可能会分发给数据库用户，因此不能将其作为集群组件凭据来信任。

    最后执行下面的命令进行创建：

    ```shell
    kubectl apply -f tidb-mysql-issuer.yaml
    ```

3. 创建 Server 端证书。

    在 `cert-manager` 中，Certificate 资源表示证书接口，该证书将由上面创建的 Issuer 颁发并保持更新。

    首先来创建 Server 端证书，创建一个 `tidb-server-cert.yaml` 文件，并输入以下内容：

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${tidb_group_name}-tidb-server-secret
      namespace: ${namespace}
    spec:
      secretName: ${tidb_group_name}-tidb-server-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB"
      usages:
        - server auth
      dnsNames:
        - "${tidb_group_name}-tidb"
        - "${tidb_group_name}-tidb.${namespace}"
        - "${tidb_group_name}-tidb.${namespace}.svc"
        - "*.${tidb_group_name}-tidb"
        - "*.${tidb_group_name}-tidb.${namespace}"
        - "*.${tidb_group_name}-tidb.${namespace}.svc"
        - "*.${tidb_group_name}-tidb-peer"
        - "*.${tidb_group_name}-tidb-peer.${namespace}"
        - "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
      ipAddresses:
        - 127.0.0.1
        - ::1
      issuerRef:
        name: ${cluster_name}-mysql-certs-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    其中 `${cluster_name}` 为集群的名字，`${tidb_group_name}` 为 `TiDBGroup` 的名字：

    - `spec.secretName` 请设置为 `${tidb_group_name}-tidb-server-secret`；
    - `usages` 请添加上 `server auth`；
    - `dnsNames` 需要填写这 6 个 DNS，根据需要可以填写其他 DNS：
      - `${tidb_group_name}-tidb`
      - `${tidb_group_name}-tidb.${namespace}`
      - `${tidb_group_name}-tidb.${namespace}.svc`
      - `*.${tidb_group_name}-tidb`
      - `*.${tidb_group_name}-tidb.${namespace}`
      - `*.${tidb_group_name}-tidb.${namespace}.svc`
      - `*.${tidb_group_name}-tidb-peer`
      - `*.${tidb_group_name}-tidb-peer.${namespace}`
      - `*.${tidb_group_name}-tidb-peer.${namespace}.svc`
    - `ipAddresses` 需要填写这两个 IP，根据需要可以填写其他 IP：
      - `127.0.0.1`
      - `::1`
    - `issuerRef` 请填写上面创建的 Issuer；
    - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

    通过执行下面的命令来创建证书：

    ```shell
    kubectl apply -f tidb-server-cert.yaml
    ```

    创建这个对象以后，cert-manager 会生成一个名字为 `${tidb_group_name}-tidb-server-secret` 的 Secret 对象供 TiDB Server 使用。

4. 创建 Client 端证书。

    创建一个 `tidb-client-cert.yaml` 文件，并输入以下内容：

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${tidb_group_name}-tidb-client-secret
      namespace: ${namespace}
    spec:
      secretName: ${tidb_group_name}-tidb-client-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB MySQL Client"
      usages:
        - client auth
      issuerRef:
        name: ${cluster_name}-mysql-certs-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    其中 `${cluster_name}` 为集群的名字，`${tidb_group_name}` 为 `TiDBGroup` 的名字：

    - `spec.secretName` 请设置为 `${tidb_group_name}-tidb-client-secret`；
    - `usages` 请添加上 `client auth`；
    - `dnsNames` 和 `ipAddresses` 不需要填写；
    - `commonName` 请设置为组件间 TLS 的 `cert-allowed-cn` 或 `cluster-verify-cn` 配置不接受的值，避免 MySQL 客户端证书被认可为组件间凭据；
    - `issuerRef` 请填写上面创建的 Issuer；
    - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

    通过执行下面的命令来创建证书：

    ```shell
    kubectl apply -f tidb-client-cert.yaml
    ```

    创建这个对象以后，cert-manager 会生成一个名字为 `${tidb_group_name}-tidb-client-secret` 的 Secret 对象供 TiDB Client 使用。

    > **注意：**
    >
    > - 由 cert-manager 签发的 Secret 中包含的 `ca.crt` 是该证书的签发 CA，并非用于验证对端 mTLS 证书的 CA。
    > - 本示例中，MySQL 客户端和服务端的 TLS 证书由同一个 MySQL TLS CA 签发，因此可以直接使用。请确保该 CA 与 TiDB 组件间 TLS 使用的 CA 相互独立。否则，如果分发的 MySQL 客户端证书的 CN 在组件 CN 允许列表中，该证书也可能被信任为组件凭据。如果 MySQL 客户端和服务端证书由不同 CA 签发，建议使用 [Trust manager](https://cert-manager.io/docs/trust/trust-manager/) 分发对应的 `ca.crt`。

### 将使用共享 CA 的现有部署迁移到独立 CA

如果你之前按照本文操作，同时启用了 TiDB 组件间 TLS，则 MySQL 证书和组件间证书可能共享同一个 CA。请勿将更新后的 `Certificate` 资源直接应用到现有对象。更改 `issuerRef` 可能会导致 cert-manager 在 TiDB 和所有客户端信任新 CA 之前，重新签发现有的服务端和客户端 Secret。

按照以下步骤规划迁移：

1. 停止分发旧的 MySQL 客户端凭据，并确认已分发的所有副本。同时确认使用 `REQUIRE SUBJECT` 或 `REQUIRE ISSUER` 的 MySQL 账号。计划在切换期间更新这些账号，或者创建与新客户端证书匹配的替代账号。详情请参阅[基于证书的身份验证](https://docs.pingcap.com/zh/tidb/stable/certificate-authentication/)。
2. 创建专用的 MySQL TLS CA 和 Issuer，将替换用的服务端和客户端证书签发到临时 Secret 中，不要覆盖正在使用的 Secret。临时服务端 Secret 仅用于暂存。TiDB Operator v2 仍从固定名称 `${tidb_group_name}-tidb-server-secret` 读取服务端证书。
3. 创建同时包含新旧 CA 的 bundle。在迁移期间，确保只有一个证书管理流程写入正在使用的 `${tidb_group_name}-tidb-server-secret`。如果对应的 cert-manager `Certificate` 仍在调谐，不要依赖一次性的手动更新，因为续期可能会覆盖 `ca.crt`。请暂时使用能够保留双 CA bundle 的流程管理正在使用的 Secret。保留其中当前的 `tls.crt` 和 `tls.key`，将 `ca.crt` 替换为双 CA bundle，并配置 MySQL 客户端信任同一个 bundle。
4. 在每个 TiDB 实例上执行 `ALTER INSTANCE RELOAD TLS`，或者执行滚动重启。在切换证书之前，确认现有连接仍可正常工作。详情请参阅[重加载证书、密钥和 CA](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers/#重加载证书密钥和-ca)。
5. 将暂存的服务端证书和密钥复制到正在使用的 `${tidb_group_name}-tidb-server-secret`，同时保留双 CA bundle。将客户端切换到新的客户端证书，并在同一切换窗口中更新第 1 步确认的账号。再次重加载每个 TiDB 实例，并确认新连接正常。
6. 所有客户端完成迁移后，从正在使用的服务端 Secret 和客户端信任配置中移除旧 CA。让 cert-manager 使用新 Issuer 重新正常管理正在使用的 Secret，并删除不再需要的临时凭据。再次重加载每个 TiDB 实例。确认使用新凭据的连接成功，并确认使用旧凭据的连接失败。
7. 替换 MySQL 证书不会使组件间 CA 已签发的旧客户端证书失效。要防止这些证书副本继续向组件端点进行身份验证，请安排维护窗口，轮换组件间 CA 和所有组件证书。切换组件证书后，从组件信任配置中移除旧 CA，再次重启受影响的组件，并确认旧客户端凭据无法连接。重启步骤请参阅[滚动重启 TiDB 集群](restart-a-tidb-cluster.md)。

## 第二步：部署 TiDBGroup

以下配置示例展示如何创建一个启用了 MySQL TLS 的 `TiDBGroup`：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: tidb
spec:
  cluster:
    name: tls
  version: {{{ .tidb_version }}}
  replicas: 1
  template:
    spec:
      security:
        tls:
          mysql:
            enabled: true
      config: |
        [security]
        cluster-verify-cn = ["TiDB"]
```

## 第三步：配置 MySQL 客户端使用加密连接

可以根据[官网文档](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers#配置-mysql-client-使用安全连接)提示，使用上面创建的 Client 证书，通过下面的方法连接 TiDB 集群：

获取 Client 证书的方式并连接 TiDB Server 的方法是：

```shell
kubectl get secret -n ${namespace} ${tidb_group_name}-tidb-client-secret  -ojsonpath='{.data.tls\.crt}' | base64 --decode > client-tls.crt
kubectl get secret -n ${namespace} ${tidb_group_name}-tidb-client-secret  -ojsonpath='{.data.tls\.key}' | base64 --decode > client-tls.key
kubectl get secret -n ${namespace} ${tidb_group_name}-tidb-client-secret  -ojsonpath='{.data.ca\.crt}'  | base64 --decode > client-ca.crt
```

```shell
mysql --comments -uroot -p -P 4000 -h ${tidb_host} --ssl-cert=client-tls.crt --ssl-key=client-tls.key --ssl-ca=client-ca.crt
```

最后请参考[官网文档](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers#检查当前连接是否是加密连接)来验证是否正确开启了 TLS。
