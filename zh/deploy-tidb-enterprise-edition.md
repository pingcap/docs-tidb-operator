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

按照上述配置文件进行部署，即可部署 TiDB 企业版集群及企业版周边工具。
