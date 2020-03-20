---
title: 为 Kubernetes 上的 TiDB 集群的 MySQL 客户端开启 TLS
category: how-to
---

# 为 Kubernetes 上的 TiDB 集群的 MySQL 客户端开启 TLS

本文主要描述了如何为 Kubernetes 上的 TiDB 集群的 MySQL 客户端开启 TLS。


- [概述](#概述)	
+ 为 TiDB 集群生成两套证书
  - [用户自己提供证书](#用户自己提供证书)
  - [使用 cert-manager 颁发证书](#使用-cert-manager-颁发证书)
- [创建 TiDB 集群](#创建-TiDB-集群)
- [MySQL 客户端使用方法](#MySQL-客户端使用方法)

## 概述

TiDB Operator 从 v1.1 开始已经支持为 Kubernetes 上的 TiDB 集群开启 MySQL 客户端 TLS。

开启此功能的步骤为：

- 为即将创建的 TiDB 集群生成两套证书：为 TiDB Server 创建一套 Server 端证书，为 MySQL Client 创建一套 Client 端证书。有多种生成证书的方式：
    - 用户自己提供证书，并使用 Kubernetes 内置证书颁发系统
    - 使用 `cert-manager` 颁发证书
- 创建两个 K8s Secret 对象，这两个 Secret 对象分别包含上述创建的 Server 端证书和客户端证书，这两个 Secret 的名字为 `<cluster-name>-tidb-server-secret` 和  `<cluster-name>-tidb-client-secret`； 
- 在创建集群的时候开启此功能。

## 为 TiDB 集群生成两套证书

### 用户自己提供证书

需要创建两套证书：为 TiDB Server 创建一套 Server 端证书，为 MySQL Client
创建一套 Client 端证书。可以使用官网提供的方式创建证书或者使用 `cfssl`
创建证书。

#### 官网创建证书

请参考官网文档：[Enable TLS for MySQL Clients | TiDB Documentation](https://pingcap.com/docs/stable/how-to/secure/enable-tls-clients/)。

#### 使用 cfssl 创建证书

##### 下载 cfssl 软件并初始化证书颁发机构

{{< copyable "shell-regular" >}}

``` shell
mkdir -p ~/bin
curl -s -L -o ~/bin/cfssl https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
curl -s -L -o ~/bin/cfssljson https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
chmod +x ~/bin/{cfssl,cfssljson}
export PATH=$PATH:~/bin

mkdir -p ~/cfssl
cd ~/cfssl
cfssl print-defaults config > ca-config.json
cfssl print-defaults csr > ca-csr.json
```

##### 配置 CA 选项

{{< copyable "shell-regular" >}}

``` shell
$ vim ca-config.json
{
    "signing": {
        "default": {
            "expiry": "43800h"
        },
        "profiles": {
            "server": {
                "expiry": "43800h",
                "usages": [
                    "signing",
                    "key encipherment",
                    "server auth"
                ]
            },
            "client": {
                "expiry": "43800h",
                "usages": [
                    "signing",
                    "key encipherment",
                    "client auth"
                ]
            }
        }
    }
}

$ vim ca-csr.json
{
    "CN": "TiDB Server",
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

##### 使用定义的选项生成 CA

{{< copyable "shell-regular" >}}

``` shell
$ cfssl gencert -initca ca-csr.json | cfssljson -bare ca -

ca-key.pem
ca.csr
ca.pem
```

##### 生成 Server 端证书

首先生成默认的 `server.json` 文件

{{< copyable "shell-regular" >}}

``` shell
cfssl print-defaults csr > server.json
```

然后编辑这个文件，修改 `CN`，`hosts` 属性：

{{< copyable "shell-regular" >}}

``` shell
...
    "CN": "TiDB",
    "hosts": [
        "1.1.1.1",
        "example.com",
    ],
...
```

最后生成 Server 端证书：

{{< copyable "shell-regular" >}}

``` shell
$ cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server server.json | cfssljson -bare server

server-key.pem
server.csr
server.pem
```

##### 生成 Client 端证书

首先生成默认的 `client.json` 文件

{{< copyable "shell-regular" >}}

``` shell
cfssl print-defaults csr > client.json
```

然后编辑这个文件，修改 `CN`，`hosts` 属性，`hosts` 可以留空：

{{< copyable "shell-regular" >}}

``` shell
...
    "CN": "MySQL Client",
    "hosts": [],
...
```

最后生成 Client 端证书：

{{< copyable "shell-regular" >}}

``` shell
$ cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client client.json | cfssljson -bare client

client-key.pem
client.csr
client.pem
```

##### 创建 K8s Secret 对象

到这里假设你已经按照上述文档把两套证书都创建好了。假设你使用 `cfssl` 创建了
Server 端证书和 Client 端证书。通过下面的命令为 TiDB 集群创建 Secret 对象：

{{< copyable "shell-regular" >}}

``` shell
kubectl create secret generic <cluster-name>-tidb-server-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/server.pem --from-file=tls.key=~/cfssl/server-key.pem --from-file=ca.crt=~/cfssl/ca.pem
kubectl create secret generic <cluster-name>-tidb-client-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/client.pem --from-file=tls.key=~/cfssl/client-key.pem --from-file=ca.crt=~/cfssl/ca.pem
```

这样就给 Server/Client 端证书分别创建了：

- 一个 Secret 供 TiDB Server 启动时加载使用;
- 另一个 Secret 供 MySQL 客户端连接 TiDB 集群时候使用。

### 使用 cert-manager 颁发证书

#### 安装 cert-manager

请参考官网安装：[cert-manager installation in Kubernetes](https://docs.cert-manager.io/en/release-0.11/getting-started/install/kubernetes.html)。 

#### 创建 ClusterIssuer

为了配置 `cert-manager` 颁发证书，必须先创建 Issuer 或 ClusterIssuer
资源，这里使用 ClusterIssuer 资源可以颁发多个 `namespace` 下的证书。

首先创建一个 SelfSigned 类型的 ClusterIsser 对象（用于生成 CA 类型 ClusterIssuer 所需要的 CA 证书）：

{{< copyable "shell-regular" >}}

``` shell
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: tidb-selfsigned-ca-issuer
spec:
  selfSigned: {}
```

然后创建一个 Cerfificate 对象，`isCa` 属性设置为 `true`：

{{< copyable "shell-regular" >}}

``` shell
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: tidb-server-issuer-cert
  namespace: cert-manager
spec:
  secretName: tidb-server-issuer-cert
  commonName: "TiDB CA"
  isCA: true
  issuerRef:
    name: tidb-selfsigned-ca-issuer
    kind: ClusterIssuer
```

最后创建一个可以用于颁发 TiDB 组件间 TLS 证书的 ClusterIssuer：

{{< copyable "shell-regular" >}}

``` shell
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: tidb-server-issuer
spec:
  ca:
    secretName: tidb-server-issuer-cert
```

#### 创建 Server/Client 端证书

在 `cert-manager` 中，Certificate 资源表示证书接口，该证书将由上面创建的
ClusterIssuer 颁发并保持更新。

所以需要为了创建 Server/Client 端证书，需要创建两个 Certificate 对象。

##### Server 端证书

{{< copyable "shell-regular" >}}

``` shell
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: <cluster-name>-tidb-server-secret
  namespace: <namespace>
spec:
  secretName: <cluster-name>-tidb-server-secret
  duration: 8760h # 265d
  renewBefore: 360h # 14d
  organization:
  - PingCAP
  commonName: "TiDB Server"
  usages:
    - server auth
  dnsNames:
  - <cluster-name>-tidb
  - <cluster-name>-tidb.<namespace>
  - <cluster-name>-tidb.<namespace>.svc
  ipAddresses:
  - 127.0.0.1
  - ::1
  issuerRef:
    name: tidb-server-issuer
    kind: ClusterIssuer
    group: cert-manager.io
```

其中 `<cluster-name>` 为集群的名字

- `spec.secretName` 请设置为 `<cluster-name>-tidb-server-secret`；
- `usages` 请添加上 `server auth`；
- `dnsNames` 需要填写这三个 DNS，根据需要可以填写其他 DNS： 
  - `<cluster-name>-tidb`
  - `<cluster-name>-tidb.<namespace>`
  - `<cluster-name>-tidb.<namespace>.svc`
- `ipAddresses` 需要填写这两个 IP ，根据需要可以填写其他 IP： 
  - `127.0.0.1`
  - `::1`
- `issuerRef` 请填写上面创建的 ClusterIssuer；
- 其他属性请参考
  [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec)。

创建这个对象以后，cert-manager 会生成一个名字为 
`<cluster-name>-tidb-server-secret` 的 Secret 对象供 TiDB Server 使用。


### Client 端证书

用户可以生成多套 Client 端证书供使用，并且至少要生成一套 Client 证书供 TiDB 
Operator 内部组件访问 TiDB Server（目前有 TidbInitializer 会访问 TiDB
Server 来设置密码或者一些初始化操作）。

{{< copyable "shell-regular" >}}

``` shell
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: <cluster-name>-tidb-client-secret
  namespace: <namespace>
spec:
  secretName: <cluster-name>-tidb-client-secret
  duration: 8760h # 265d
  renewBefore: 360h # 14d
  organization:
  - PingCAP
  commonName: "TiDB Client"
  usages:
    - client auth
  issuerRef:
    name: tidb-server-issuer
    kind: ClusterIssuer
    group: cert-manager.io
```

其中 `<cluster-name>` 为集群的名字：
- `spec.secretName` 请设置为 `<cluster-name>-tidb-client-secret`；
- `usages` 请添加上 `client auth`；
- `dnsNames` 和 `ipAddresses` 不需要填写；
- `issuerRef` 请填写上面创建的 ClusterIssuer；
- 其他属性请参考 
  [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec)。

创建这个对象以后，cert-manager 会生成一个名字为
`<cluster-name>-tidb-client-secret` 的 Secret 对象供 TiDB Client 使用。获取
Client 证书的方式是：

{{< copyable "shell-regular" >}}

``` shell
$ mkdir -p ~/<cluster-name>-tidb-client-tls
$ cd ~/<cluster-name>-tidb-client-tls
$ kubectl get secret -n <namespace> <cluster-name>-tidb-client-secret  -ojsonpath='{.data.tls\.crt}' | base64 --decode > tls.crt
$ kubectl get secret -n <namespace> <cluster-name>-tidb-client-secret  -ojsonpath='{.data.tls\.key}' | base64 --decode > tls.key
$ kubectl get secret -n <namespace> <cluster-name>-tidb-client-secret  -ojsonpath='{.data.ca\.crt}' | base64 --decode > ca.crt
```

## 创建 TiDB 集群

接下来将会通过两个 CR 文件来创建一个 TiDB 集群，并且：

- 开启 MySQL 客户端 TLS；
- 对集群进行初始化（这里创建了一个数据库 `app`）。

{{< copyable "shell-regular" >}}

``` shell
---
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
 name: demo
 namespace: demo
spec:
 version: v3.0.8
 timezone: UTC
 pvReclaimPolicy: Retain
 pd:
   baseImage: pingcap/pd
   replicas: 1
   requests:
     storage: "1Gi"
   config: {}
 tikv:
   baseImage: pingcap/tikv
   replicas: 1
   requests:
     storage: "1Gi"
   config: {}
 tidb:
   baseImage: pingcap/tidb
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
 name: basic-init
 namespace: default
spec:
 image: tnir/mysqlclient
 cluster:
   namespace: default
   name: basic
 initSql: |-
   create database app;
```

上面通过设置 `spec.tidb.tlsClient.enabled` 属性为 `true` 来开启 MySQL
客户端 TLS：


{{< copyable "shell-regular" >}}

``` shell
spec:
 tidb:
   tlsClient:
     enabled: true
```

然后使用 `kubectl apply -f cr.yaml` 来创建 TiDB 集群。

## MySQL 客户端使用方法

根据
[官网文档](https://github.com/pingcap/tidb-operator/blob/master/docs/CONTRIBUTING.md#start-tidb-operator-locally-and-do-manual-tests)
提示，使用上面创建的 Client 证书，通过下面的方法连接 TiDB 集群：

{{< copyable "shell-regular" >}}

``` shell
mysql -uroot -p -P 4000 -h <tidb-host> --ssl-cert=~/cfssl/client.pem --ssl-key=~/cfssl/client-key.pem --ssl-ca=~/cfssl/ca.pem
```

最后请参考
[官网文档](https://pingcap.com/docs/stable/how-to/secure/enable-tls-clients/#check-whether-the-current-connection-uses-encryption)
来验证是否正确开启了 TLS。
