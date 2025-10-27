---
title: 更新和替换 TLS 证书
summary: 介绍如何更新和替换 TiDB 组件间的 TLS 证书。
---

# 更新和替换 TLS 证书

本文以更新和替换 TiDB 集群中 PD、TiKV、TiDB 组件间的 TLS 证书为例，介绍在证书过期之前，如何更新和替换相应组件的证书。

如需要更新和替换集群中其他组件间的证书、TiDB Server 端证书或 MySQL Client 端证书，可使用类似的步骤进行操作。

本文的更新和替换操作假定原证书尚未过期。若原证书已经过期或失效，可参考[为 TiDB 组件间开启 TLS](enable-tls-between-components.md) 或[为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md) 生成新的证书并重启集群。

## 更新和替换 `cert-manager` 颁发的证书

如原 TLS 证书是[使用 `cert-manager` 系统颁发的证书](enable-tls-between-components.md#第一步为-tidb-集群各个组件生成证书)，且原证书尚未过期，根据是否需要更新 CA 证书需要分别处理。

### 更新和替换 CA 证书

<!-- TODO -->

### 仅更新和替换组件间证书

使用 cert-manager 颁发证书时，可通过配置 `Certificate` 资源的 `spec.renewBefore` 字段，让 cert-manager 在证书过期前自动进行更新。

1. cert-manager 支持在证书过期前自动更新各组件的证书及对应的 Kubernetes Secret 对象。如需手动更新，可以参考[使用 cmctl renew 证书](https://cert-manager.io/docs/reference/cmctl/#renew)。

2. 对于各组件间的证书，各组件会在之后新建连接时自动重新加载新的证书，无需手动操作。

    > **注意：**
    >
    > - 各组件目前[暂不支持 CA 证书的自动重新加载](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-components#证书重加载)，需要参考[更新和替换 CA 证书](#更新和替换-ca-证书)进行处理。
    > - 对于 TiDB Server 端证书，可参考以下任意方式进行手动重加载：
    >     - 参考[重加载证书、密钥和 CA](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-clients-and-servers#重加载证书密钥和-ca)。
    >     - 参考[滚动重启 TiDB 集群](restart-a-tidb-cluster.md)对 TiDB Server 进行滚动重启。
