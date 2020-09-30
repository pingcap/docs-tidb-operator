---
title: 将 TiDB 迁移至 Kubernetes
summary: 介绍如何将部署在物理机或虚拟机中的 TiDB 迁移至 Kubernetes 集群中
aliases: ['/docs-cn/tidb-in-kubernetes/dev/migrate-tidb-to-kubernetes/']
---

# 将 TiDB 迁移至 Kubernetes

本文介绍一种不借助备份恢复工具将部署在物理机或虚拟机中的 TiDB 迁移至 Kubernetes 中的方法。

## 先置条件

- Kubernetes 集群外物理机或虚拟机节点必须与集群内 Pod 网络互通
- Kubernetes 集群外物理机或虚拟机节点必须能够解析 Kubernetes 集群内部 Pod 域名
- 待迁移集群没有开启[组件间 TLS 加密通信](https://docs.pingcap.com/zh/tidb/stable/enable-tls-between-components)

## 第一步：在 Kubernetes 中创建 TiDB 集群

1. 记录待迁移集群 PD 节点地址及端口号，例如: `pd1_addr:2379, pd2_addr:2379, pd3_addr:2379`

2. 在 Kubernetes 中创建目的 TiDB 集群（TiKV节点个数不少于3个），并在`spec.PDAddresses`字段中指定待迁移 TiDB 集群的PD节点地址（以`http://`开头），例如：

``` yaml
spec
  ...
  PDAddresses:
  - http://pd1_addr:2379
  - http://pd2_addr:2379
  - http://pd3_addr:2379
```

## 第二步：缩容源集群 TiDB 节点

1. 若通过负载均衡或访问层中间件接入源 TiDB 集群，则先修改配置，将业务流量迁移至目的 TiDB 集群。

2. 将源集群 TiDB 节点缩容至0

## 第三步：缩容源集群 TiKV 节点

将源集群 TiKV 节点个数缩容至0，raft 协议会自动将所有 region 转移至目的集群。

## 第四步：缩容源集群 PD 节点

将源集群 PD leader 驱逐至目的集群 PD 节点后，将源集群 PD 节点缩容至0。

## 第五步：销毁源集群

销毁源集群，回收资源。
