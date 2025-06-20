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

其中，颁发证书的方式有多种，本文档提供两种方式，用户也可以根据需要为 TiDB 集群颁发证书，这两种方式分别为：

- 使用 `cfssl` 系统颁发证书；
- （推荐）使用 `cert-manager` 系统颁发证书；

当需要更新已有 TLS 证书时，可参考[更新和替换 TLS 证书](renew-tls-certificate.md)。

## 第一步：为 TiDB 集群颁发两套证书

### 使用 `cfssl` 系统颁发证书

1. 首先下载 `cfssl` 软件并初始化证书颁发机构：

    ```shell
    mkdir -p ~/bin
    curl -s -L -o ~/bin/cfssl https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
    curl -s -L -o ~/bin/cfssljson https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
    chmod +x ~/bin/{cfssl,cfssljson}
    export PATH=$PATH:~/bin

    mkdir -p cfssl
    cd cfssl
    cfssl print-defaults config > ca-config.json
    cfssl print-defaults csr > ca-csr.json
    ```

2. 在 `ca-config.json` 配置文件中配置 CA 选项：

    ```json
    {
        "signing": {
            "default": {
                "expiry": "8760h"
            },
            "profiles": {
                "server": {
                    "expiry": "8760h",
                    "usages": [
                        "signing",
                        "key encipherment",
                        "server auth"
                    ]
                },
                "client": {
                    "expiry": "8760h",
                    "usages": [
                        "signing",
                        "key encipherment",
                        "client auth"
                    ]
                }
            }
        }
    }
    ```

3. 您还可以修改 `ca-csr.json` 证书签名请求 (CSR)：

    ```json
    {
        "CN": "TiDB Server",
        "CA": {
            "expiry": "87600h"
        },
        "key": {
            "algo": "rsa",
            "size": 2048
        },
        "names": [
            {
                "C": "US",
                "L": "CA",
                "O": "PingCAP",
                "ST": "Beijing",
                "OU": "TiDB"
            }
        ]
    }
    ```

4. 使用定义的选项生成 CA：

    ```shell
    cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
    ```

5. 生成 Server 端证书。

    首先生成默认的 `server.json` 文件：

    ```shell
    cfssl print-defaults csr > server.json
    ```

    然后编辑这个文件，修改 `CN`，`hosts` 属性：

    ```json
    ...
        "CN": "TiDB Server",
        "hosts": [
          "127.0.0.1",
          "::1",
          "${tidb_group_name}-tidb",
          "${tidb_group_name}-tidb.${namespace}",
          "${tidb_group_name}-tidb.${namespace}.svc",
          "*.${tidb_group_name}-tidb",
          "*.${tidb_group_name}-tidb.${namespace}",
          "*.${tidb_group_name}-tidb.${namespace}.svc",
          "*.${tidb_group_name}-tidb-peer",
          "*.${tidb_group_name}-tidb-peer.${namespace}",
          "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
        ],
    ...
    ```

    其中 `${tidb_group_name}` 为 `TiDBGroup` 的名字，`${namespace}` 为 TiDB 集群部署的命名空间，用户也可以添加自定义 `hosts`。

    最后生成 Server 端证书：

    ```shell
    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server server.json | cfssljson -bare server
    ```

6. 生成 Client 端证书。

    首先生成默认的 `client.json` 文件：

    ```shell
    cfssl print-defaults csr > client.json
    ```

    然后编辑这个文件，修改 `CN`，`hosts` 属性，`hosts` 可以留空：

    ```json
    ...
        "CN": "TiDB Client",
        "hosts": [],
    ...
    ```

    最后生成 Client 端证书：

    ```shell
    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client client.json | cfssljson -bare client
    ```

7. 创建 Kubernetes Secret 对象。

    到这里假设你已经按照上述文档把两套证书都创建好了。通过下面的命令为 TiDB 集群创建 Secret 对象：

    ```shell
    kubectl create secret generic ${tidb_group_name}-tidb-server-secret --namespace=${namespace} --from-file=tls.crt=server.pem --from-file=tls.key=server-key.pem --from-file=ca.crt=ca.pem
    kubectl create secret generic ${tidb_group_name}-tidb-client-secret --namespace=${namespace} --from-file=tls.crt=client.pem --from-file=tls.key=client-key.pem --from-file=ca.crt=ca.pem
    ```

    这样就给 Server/Client 端证书分别创建了：

    - 一个 Secret 供 TiDB Server 启动时加载使用;
    - 另一个 Secret 供 MySQL 客户端连接 TiDB 集群时候使用。

用户可以生成多套 Client 端证书，并且至少要生成一套 Client 证书供 TiDB Operator 内部组件访问 TiDB Server。

### 使用 cert-manager 颁发证书

1. 安装 cert-manager。

    请参考官网安装：[cert-manager installation on Kubernetes](https://docs.cert-manager.io/en/release-0.11/getting-started/install/kubernetes.html)。

2. 创建一个 Issuer 用于给 TiDB 集群颁发证书。

    为了配置 `cert-manager` 颁发证书，必须先创建 Issuer 资源。

    首先创建一个目录保存 `cert-manager` 创建证书所需文件：

    ```shell
    mkdir -p cert-manager
    cd cert-manager
    ```

    然后创建一个 `tidb-server-issuer.yaml` 文件，输入以下内容：

    ```yaml
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
      name: ${cluster_name}-cert-issuer
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

    ```shell
    kubectl apply -f tidb-server-issuer.yaml
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
        name: ${cluster_name}-cert-issuer
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
      commonName: "TiDB"
      usages:
        - client auth
      issuerRef:
        name: ${cluster_name}-cert-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    其中 `${cluster_name}` 为集群的名字，`${tidb_group_name}` 为 `TiDBGroup` 的名字：

    - `spec.secretName` 请设置为 `${tidb_group_name}-tidb-client-secret`；
    - `usages` 请添加上 `client auth`；
    - `dnsNames` 和 `ipAddresses` 不需要填写；
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
    > - 本示例中，客户端和服务端的 TLS 证书由同一个 CA 签发，因此可以直接使用。如果客户端和服务端的证书由不同 CA 签发，建议使用 [Trust manager](https://cert-manager.io/docs/trust/trust-manager/) 分发对应的 `ca.crt`。

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
  version: v8.1.0
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
