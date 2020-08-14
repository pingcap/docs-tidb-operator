---
title: 在 Kubernetes 上部署 TiDB 企业版
summary: 了解如何在 Kubernetes 上部署 TiDB 企业版。
---

# 部署 TiDB 企业版

本文档介绍如何在 Kubernetes 上部署 TiDB 集群企业版及相应的企业版工具。

## 前置条件

* TiDB Operator [部署](deploy-tidb-operator.md)完成。

## 部署方法

目前 TiDB Operator 的企业版与社区版部署的差异主要体现在镜像命名上。相比于社区版，企业版的镜像都会多一个 `-enterprise` 后缀。

```yaml
spec:
  version: v4.0.2
  ...
  pd:
    baseImage: pingcap/pd-enterprise
  ...
  tikv:
    baseImage: pingcap/tikv-enterprise
  ...
  tidb:
    baseImage: pingcap/tidb-enterprise
  ...
  tiflash:
    baseImage: pingcap/tiflash-enterprise
  ...
  pump:
    baseImage: pingcap/tidb-binlog-enterprise
  ...
  ticdc:
    baseImage: pingcap/ticdc-enterprise
```

如果是部署全新集群，运行 `kubectl apply -f tidb-cluster.yaml -n ${namespace}` apply 上述配置即可部署 TiDB 企业版集群及企业版周边工具。

如果是需要将已有集群切换为企业版，只需将已有集群的配置文件按上述格式在 `baseImage` 后添加 "-enterprise" 后缀并使用 `kubectl apply -f tidb-cluster.yaml -n ${namespace}` 更新集群配置即可。

tidb-operator 会自动通过滚动升级的方式将集群镜像更新为企业版镜像。

## 切换回社区版本

如果需要将集群切换回社区版本，只需要将配置文件中的 "-enterprise" 后缀去除。

```yaml
spec:
  version: v4.0.2
  ...
  pd:
    baseImage: pingcap/pd
  ...
  tikv:
    baseImage: pingcap/tikv
  ...
  tidb:
    baseImage: pingcap/tidb
  ...
  tiflash:
    baseImage: pingcap/tiflash
  ...
  pump:
    baseImage: pingcap/tidb-binlog
  ...
  ticdc:
    baseImage: pingcap/ticdc
```

使用 `kubectl apply -f tidb-cluster.yaml -n ${namespace}` 更新集群配置后，tidb-operator 会自动通过滚动升级的方式将集群镜像切换为社区版镜像。
