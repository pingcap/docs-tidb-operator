---
title: 为 TiDB 组件间开启 TLS
summary: 在 Kubernetes 上如何为 TiDB 集群组件间开启 TLS。
---

# 为 TiDB 组件间开启 TLS

本文主要描述了在 Kubernetes 上如何为 TiDB 集群组件间开启 TLS。开启步骤为：

1. 为即将被创建的 TiDB 集群的每个组件 Group 生成证书：

    为每个组件 Group 分别创建一套证书，保存为 Kubernetes Secret 对象：`${group_name}-${component_name}-cluster-secret`。

    > **注意：**
    >
    > 创建的 Secret 对象必须符合上述命名规范，否则将导致各组件部署失败。

2. 部署集群，为 Cluster Custom Resource (CR) 设置 `.spec.tlsCluster.enabled` 属性为 `true`；

    > **注意：**
    >
    > 在集群创建后，不能修改此字段，否则将导致集群升级失败，此时需要删除已有集群，并重新创建。

3. 配置 `pd-ctl` 和 `tikv-ctl` 连接集群。

其中，颁发证书的方式有多种，本文档提供两种方式，你也可以根据需要为 TiDB 集群颁发证书，这两种方式分别为：

- 使用 `cfssl` 系统颁发证书；
- 使用 `cert-manager` 系统颁发证书；

当需要更新已有 TLS 证书时，可参考[更新和替换 TLS 证书](renew-tls-certificate.md)。

## 第一步：为 TiDB 集群各个组件生成证书

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
    ```

2. 生成 `ca-config.json` 配置文件：

    > **注意：**
    >
    > - TiDB 所有组件在进行组件间通信时，共用一套 TLS 证书来加密客户端与服务端的流量，因此，生成 CA 配置时必须同时指定 `server auth` 和 `client auth`。
    > - 建议所有组件的证书均由同一个 CA 签发。

    ```shell
    cat << EOF > ca-config.json
    {
        "signing": {
            "default": {
                "expiry": "8760h"
            },
            "profiles": {
                "internal": {
                    "expiry": "8760h",
                    "usages": [
                        "signing",
                        "key encipherment",
                        "server auth",
                        "client auth"
                    ]
                }
            }
        }
    }
    EOF
    ```

3. 生成 `ca-csr.json` 配置文件：

    ```shell
    cat << EOF > ca-csr.json
    {
        "CN": "TiDB",
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
    EOF
    ```

4. 使用定义的选项生成 CA：

    ```shell
    cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
    ```

5. 生成证书。

    这里需要为每个 TiDB 集群的组件 Group 生成一套证书。

    - PD 证书

        首先生成默认的 `pd.json` 文件：

        ```shell
        cfssl print-defaults csr > pd.json
        ```

        然后编辑这个文件，修改 `CN` 和 `hosts` 属性：

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${pd_group_name}-pd",
              "${pd_group_name}-pd.${namespace}",
              "${pd_group_name}-pd.${namespace}.svc",
              "${pd_group_name}-pd-peer",
              "${pd_group_name}-pd-peer.${namespace}",
              "${pd_group_name}-pd-peer.${namespace}.svc",
              "*.${pd_group_name}-pd-peer",
              "*.${pd_group_name}-pd-peer.${namespace}",
              "*.${pd_group_name}-pd-peer.${namespace}.svc"
            ],
        ...
        ```

        其中 `${pd_group_name}` 为 PDGroup 的名字，`${namespace}` 为 TiDB 集群部署的命名空间，你也可以添加自定义 `hosts`。

        最后生成 PD 证书：

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal pd.json | cfssljson -bare pd
        ```

    - TiKV 证书

        首先生成默认的 `tikv.json` 文件：

        ```shell
        cfssl print-defaults csr > tikv.json
        ```

        然后编辑这个文件，修改 `CN` 和 `hosts` 属性：

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${tikv_group_name}-tikv",
              "${tikv_group_name}-tikv.${namespace}",
              "${tikv_group_name}-tikv.${namespace}.svc",
              "${tikv_group_name}-tikv-peer",
              "${tikv_group_name}-tikv-peer.${namespace}",
              "${tikv_group_name}-tikv-peer.${namespace}.svc",
              "*.${tikv_group_name}-tikv-peer",
              "*.${tikv_group_name}-tikv-peer.${namespace}",
              "*.${tikv_group_name}-tikv-peer.${namespace}.svc"
            ],
        ...
        ```

        其中 `${tikv_group_name}` 为 TiKVGroup 的名字，`${namespace}` 为 TiDB 集群部署的命名空间，你也可以添加自定义 `hosts`。

        最后生成 TiKV 证书：

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal tikv.json | cfssljson -bare tikv
        ```

    - TiDB 证书

        首先生成默认的 `tidb.json` 文件：

        ```shell
        cfssl print-defaults csr > tidb.json
        ```

        然后编辑这个文件，修改 `CN` 和 `hosts` 属性：

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${tidb_group_name}-tidb",
              "${tidb_group_name}-tidb.${namespace}",
              "${tidb_group_name}-tidb.${namespace}.svc",
              "${tidb_group_name}-tidb-peer",
              "${tidb_group_name}-tidb-peer.${namespace}",
              "${tidb_group_name}-tidb-peer.${namespace}.svc",
              "*.${tidb_group_name}-tidb-peer",
              "*.${tidb_group_name}-tidb-peer.${namespace}",
              "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
            ],
        ...
        ```

        其中 `${tidb_group_name}` 为 TiDBGroup 的名字，`${namespace}` 为 TiDB 集群部署的命名空间，你也可以添加自定义 `hosts`。

        最后生成 TiDB 证书：

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal tidb.json | cfssljson -bare tidb
        ```

    - 其他组件证书

        除了 PD、TiKV 和 TiDB 外，其他组件的 Group 也需要生成各自的 TLS 证书。以下示例展示了生成组件证书的基本步骤：

        首先生成默认的 `${component_name}.json` 文件：

        ```shell
        cfssl print-defaults csr > ${component_name}.json
        ```

        然后编辑这个文件，修改 `CN` 和 `hosts` 属性：

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${group_name}-${component_name}",
              "${group_name}-${component_name}.${namespace}",
              "${group_name}-${component_name}.${namespace}.svc",
              "${group_name}-${component_name}-peer",
              "${group_name}-${component_name}-peer.${namespace}",
              "${group_name}-${component_name}-peer.${namespace}.svc",
              "*.${group_name}-${component_name}-peer",
              "*.${group_name}-${component_name}-peer.${namespace}",
              "*.${group_name}-${component_name}-peer.${namespace}.svc"
            ],
        ...
        ```

        其中：

        - `${group_name}` 为组件 Group 的名字
        - `${component_name}` 为组件名（需使用小写字母，如 `pd`、`tikv`、`tidb`）
        - `${namespace}` 为 TiDB 集群部署的命名空间
        - 你也可以添加自定义 `hosts`

        最后生成组件证书：

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal ${component_name}.json | cfssljson -bare ${component_name}
        ```

6. 创建 Kubernetes Secret 对象。

    假设你已经按照上述文档为每个组件创建了一套 Server 端证书，并为各个客户端创建了一套 Client 端证书。通过下面的命令为 TiDB 集群创建这些 Secret 对象：

    PD 集群证书 Secret：

    ```shell
    kubectl create secret generic ${pd_group_name}-pd-cluster-secret --namespace=${namespace} --from-file=tls.crt=pd.pem --from-file=tls.key=pd-key.pem --from-file=ca.crt=ca.pem
    ```

    TiKV 集群证书 Secret：

    ```shell
    kubectl create secret generic ${tikv_group_name}-tikv-cluster-secret --namespace=${namespace} --from-file=tls.crt=tikv.pem --from-file=tls.key=tikv-key.pem --from-file=ca.crt=ca.pem
    ```

    TiDB 集群证书 Secret：

    ```shell
    kubectl create secret generic ${tidb_group_name}-tidb-cluster-secret --namespace=${namespace} --from-file=tls.crt=tidb.pem --from-file=tls.key=tidb-key.pem --from-file=ca.crt=ca.pem
    ```

    其他组件证书 Secret：

    ```shell
    kubectl create secret generic ${group_name}-${component_name}-cluster-secret --namespace=${namespace} --from-file=tls.crt=${component_name}.pem --from-file=tls.key=${component_name}-key.pem --from-file=ca.crt=ca.pem
    ```

    这里给 PD、TiKV、TiDB 的 Server 端证书分别创建了一个 Secret 供他们启动时加载使用，另外一套 Client 端证书供他们的客户端连接使用。

### 使用 `cert-manager` 系统颁发证书

1. 安装 cert-manager。

    请参考官网安装：[cert-manager installation on Kubernetes](https://cert-manager.io/docs/installation/)。

2. 创建一个 Issuer 用于给 TiDB 集群颁发证书。

    为了配置 `cert-manager` 颁发证书，必须先创建 Issuer 资源。

    首先创建一个目录保存 `cert-manager` 创建证书所需文件：

    ```shell
    mkdir -p cert-manager
    cd cert-manager
    ```

    然后创建一个 `tidb-cluster-issuer.yaml` 文件，输入以下内容：

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
      commonName: "TiDB"
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
      name: ${cluster_name}-certs-issuer
      namespace: ${namespace}
    spec:
      ca:
        secretName: ${cluster_name}-ca-secret
    ```

    其中 `${cluster_name}` 为集群的名字，上面的文件创建三个对象：

    - 一个 SelfSigned 类型的 Issuer 对象（用于生成 CA 类型 Issuer 所需要的 CA 证书）
    - 一个 Certificate 对象，`isCa` 属性设置为 `true`
    - 一个可以用于颁发 TiDB 组件间 TLS 证书的 Issuer

    最后执行下面的命令进行创建：

    ```shell
    kubectl apply -f tidb-cluster-issuer.yaml
    ```

3. 创建组件证书。

    在 `cert-manager` 中，Certificate 资源表示证书接口，该证书将由上面创建的 Issuer 颁发并保持更新。

    根据[为 TiDB 组件间通信开启加密传输](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-components)文档，需要为每个组件创建一个组件证书。

    - PD 组件的证书。

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${pd_group_name}-pd-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${pd_group_name}-pd-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "TiDB"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "${pd_group_name}-pd"
          - "${pd_group_name}-pd.${namespace}"
          - "${pd_group_name}-pd.${namespace}.svc"
          - "${pd_group_name}-pd-peer"
          - "${pd_group_name}-pd-peer.${namespace}"
          - "${pd_group_name}-pd-peer.${namespace}.svc"
          - "*.${pd_group_name}-pd-peer"
          - "*.${pd_group_name}-pd-peer.${namespace}"
          - "*.${pd_group_name}-pd-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        其中 `${pd_group_name}` 为 PDGroup 的名字，`${cluster_name}` 为 TiDB 集群的名字：

        - `spec.secretName` 请设置为 `${pd_group_name}-pd-cluster-secret`；
        - `usages` 请添加上 `server auth` 和 `client auth`；
        - `dnsNames` 需要填写这些 DNS，根据需要可以填写其他 DNS：
          - `${pd_group_name}-pd`
          - `${pd_group_name}-pd.${namespace}`
          - `${pd_group_name}-pd.${namespace}.svc`
          - `${pd_group_name}-pd-peer`
          - `${pd_group_name}-pd-peer.${namespace}`
          - `${pd_group_name}-pd-peer.${namespace}.svc`
          - `*.${pd_group_name}-pd-peer`
          - `*.${pd_group_name}-pd-peer.${namespace}`
          - `*.${pd_group_name}-pd-peer.${namespace}.svc`
        - `ipAddresses` 需要填写这两个 IP，根据需要可以填写其他 IP：
          - `127.0.0.1`
          - `::1`
        - `issuerRef` 请填写上面创建的 Issuer；
        - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

        创建这个对象以后，`cert-manager` 会生成一个名字为 `${pd_group_name}-pd-cluster-secret` 的 Secret 对象供 TiDB 集群的 PD 组件使用。

    - TiKV 组件的证书。

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${tikv_group_name}-tikv-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${tikv_group_name}-tikv-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "TiDB"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "${tikv_group_name}-tikv"
          - "${tikv_group_name}-tikv.${namespace}"
          - "${tikv_group_name}-tikv.${namespace}.svc"
          - "${tikv_group_name}-tikv-peer"
          - "${tikv_group_name}-tikv-peer.${namespace}"
          - "${tikv_group_name}-tikv-peer.${namespace}.svc"
          - "*.${tikv_group_name}-tikv-peer"
          - "*.${tikv_group_name}-tikv-peer.${namespace}"
          - "*.${tikv_group_name}-tikv-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        其中 `${tikv_group_name}` 为 TiKVGroup 的名字，`${cluster_name}` 为 TiDB 集群的名字：

        - `spec.secretName` 请设置为 `${tikv_group_name}-tikv-cluster-secret`；
        - `usages` 请添加上 `server auth` 和 `client auth`；
        - `dnsNames` 需要填写这些 DNS，根据需要可以填写其他 DNS：
          - `${tikv_group_name}-tikv`
          - `${tikv_group_name}-tikv.${namespace}`
          - `${tikv_group_name}-tikv.${namespace}.svc`
          - `${tikv_group_name}-tikv-peer`
          - `${tikv_group_name}-tikv-peer.${namespace}`
          - `${tikv_group_name}-tikv-peer.${namespace}.svc`
          - `*.${tikv_group_name}-tikv-peer`
          - `*.${tikv_group_name}-tikv-peer.${namespace}`
          - `*.${tikv_group_name}-tikv-peer.${namespace}.svc`
        - `ipAddresses` 需要填写这两个 IP，根据需要可以填写其他 IP：
          - `127.0.0.1`
          - `::1`
        - `issuerRef` 请填写上面创建的 Issuer；
        - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

        创建这个对象以后，`cert-manager` 会生成一个名字为 `${tikv_group_name}-tikv-cluster-secret` 的 Secret 对象供 TiDB 集群的 TiKV 组件使用。

    - TiDB 组件的证书。

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${tidb_group_name}-tidb-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${tidb_group_name}-tidb-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "TiDB"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "${tidb_group_name}-tidb"
          - "${tidb_group_name}-tidb.${namespace}"
          - "${tidb_group_name}-tidb.${namespace}.svc"
          - "${tidb_group_name}-tidb-peer"
          - "${tidb_group_name}-tidb-peer.${namespace}"
          - "${tidb_group_name}-tidb-peer.${namespace}.svc"
          - "*.${tidb_group_name}-tidb-peer"
          - "*.${tidb_group_name}-tidb-peer.${namespace}"
          - "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        其中 `${tidb_group_name}` 为 TiDBGroup 的名字，`${cluster_name}` 为 TiDB 集群的名字：

        - `spec.secretName` 请设置为 `${tidb_group_name}-tidb-cluster-secret`；
        - `usages` 请添加上 `server auth` 和 `client auth`；
        - `dnsNames` 需要填写这些 DNS，根据需要可以填写其他 DNS：
          - `${tidb_group_name}-tidb`
          - `${tidb_group_name}-tidb.${namespace}`
          - `${tidb_group_name}-tidb.${namespace}.svc`
          - `${tidb_group_name}-tidb-peer`
          - `${tidb_group_name}-tidb-peer.${namespace}`
          - `${tidb_group_name}-tidb-peer.${namespace}.svc`
          - `*.${tidb_group_name}-tidb-peer`
          - `*.${tidb_group_name}-tidb-peer.${namespace}`
          - `*.${tidb_group_name}-tidb-peer.${namespace}.svc`
        - `ipAddresses` 需要填写这两个 IP，根据需要可以填写其他 IP：
          - `127.0.0.1`
          - `::1`
        - `issuerRef` 请填写上面创建的 Issuer；
        - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

        创建这个对象以后，`cert-manager` 会生成一个名字为 `${tidb_group_name}-tidb-cluster-secret` 的 Secret 对象供 TiDB 集群的 TiDB 组件使用。

    - 其他组件的证书。

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${group_name}-${component_name}-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${group_name}-${component_name}-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "TiDB"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "${group_name}-${component_name}"
          - "${group_name}-${component_name}.${namespace}"
          - "${group_name}-${component_name}.${namespace}.svc"
          - "${group_name}-${component_name}-peer"
          - "${group_name}-${component_name}-peer.${namespace}"
          - "${group_name}-${component_name}-peer.${namespace}.svc"
          - "*.${group_name}-${component_name}-peer"
          - "*.${group_name}-${component_name}-peer.${namespace}"
          - "*.${group_name}-${component_name}-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        其中 `${group_name}` 为组件 Group 的名字，`${component_name}` 为组件名，`${cluster_name}` 为 TiDB 集群的名字：

        - `spec.secretName` 请设置为 `${group_name}-${component_name}-cluster-secret`；
        - `usages` 请添加上 `server auth` 和 `client auth`；
        - `dnsNames` 需要填写这些 DNS，根据需要可以填写其他 DNS：
          - `${group_name}-${component_name}`
          - `${group_name}-${component_name}.${namespace}`
          - `${group_name}-${component_name}.${namespace}.svc`
          - `${group_name}-${component_name}-peer`
          - `${group_name}-${component_name}-peer.${namespace}`
          - `${group_name}-${component_name}-peer.${namespace}.svc`
          - `*.${group_name}-${component_name}-peer`
          - `*.${group_name}-${component_name}-peer.${namespace}`
          - `*.${group_name}-${component_name}-peer.${namespace}.svc`
        - `ipAddresses` 需要填写这两个 IP ，根据需要可以填写其他 IP：
          - `127.0.0.1`
          - `::1`
        - `issuerRef` 请填写上面创建的 Issuer；
        - 其他属性请参考 [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)。

        创建这个对象以后，`cert-manager` 会生成一个名字为 `${group_name}-${component_name}-cluster-secret` 的 Secret 对象供 TiDB 集群的组件使用。

## 第二步：部署 TiDB 集群

在部署 TiDB 集群时，可以开启集群间的 TLS，同时可以设置 `cert-allowed-cn` 配置项（TiDB 为 `cluster-verify-cn`），用来验证集群间各组件证书的 CN (Common Name)。

> **注意：**
>
> - 对于 TiDB v8.3.0 及之前版本，PD 的 `cert-allowed-cn` 配置项只能设置一个值。因此所有认证对象的 `Common Name` 必须设置成同一个值。
> - 从 TiDB v8.4.0 起，PD 的 `cert-allowed-cn` 配置项支持设置多个值。你可以根据需要在 TiDB 的 `cluster-verify-cn` 配置项以及其它组件的 `cert-allowed-cn` 配置项中设置多个 Common Name。
> - 详情参考[为 TiDB 组件间通信开启加密传输](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-components/)。

按照如下步骤部署 TiDB 集群并开启集群间的 TLS：

创建 `tidb-cluster.yaml` 文件：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: Cluster
metadata:
 name: ${cluster_name}
 namespace: ${namespace}
spec:
 tlsCluster:
   enabled: true
---
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: ${pd_group_name}
 namespace: ${namespace}
spec:
  cluster:
    name: ${cluster_name}
  version: v8.1.0
  replicas: 3
  template:
    spec:
      config: |
        [security]
        cert-allowed-cn = ["TiDB"]
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 20Gi
---
apiVersion: core.pingcap.com/v1alpha1
kind: TiKVGroup
metadata:
  name: ${tikv_group_name}
 namespace: ${namespace}
spec:
  cluster:
    name: ${cluster_name}
  version: v8.1.0
  replicas: 3
  template:
    spec:
      config: |
        [security]
        cert-allowed-cn = ["TiDB"]
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 100Gi
---
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: ${tidb_group_name}
  namespace: ${namespace}
spec:
  cluster:
    name: ${cluster_name}
  version: v8.1.0
  replicas: 1
  template:
    spec:
      config: |
        [security]
        cluster-verify-cn = ["TiDB"]
```

然后使用 `kubectl apply -f tidb-cluster.yaml` 来创建 TiDB 集群。
