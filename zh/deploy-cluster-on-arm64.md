---
title: 在 ARM64 机器上部署 TiDB 集群
summary: 本文档介绍如何在 ARM64 机器上部署 TiDB 集群
---

# 在 ARM64 机器上部署 TiDB 集群

本文档介绍在 ARM64 机器上部署 TiDB 集群

## 前置条件
* 在 ARM64 机器上已经部署了 Kubernetes。

## 部署 TiDB Operator

部署步骤与文档 [部署 TiDB Operator](deploy-tidb-operator) 中相同，仅需要将使用的 TiDB Operator 相关镜像变为 ARM64 版本。

在部署过程中的 [自定义部署 TiDB Operator](deploy-tidb-operator#自定义部署-tidb-operator) 这一步，在获取到的 `tidb-operator` chart 中的 `value.yaml` 文件后，修改文件中的 `operatorImage` 与 `tidbBackupManagerImage` 字段：

```yaml
# ...
operatorImage: pingcap/tidb-operator-arm64:v1.1.13
# ...
tidbBackupManagerImage: pingcap/tidb-backup-manager-arm64:v1.1.13
# ...
```

## 部署 TiDB 集群

部署步骤与文档 [部署 TiDB 集群](deploy-on-general-kubernetes) 中相同，仅需要将 TidbCluster 定义文件中相关组件镜像设置为 ARM64 版本镜像。

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: ${cluster_name}
  namespace: ${cluster_namespace}
spec:
  version: "v5.1.0"
  # ...
  helper:
    image: busybox:1.33.0
  # ...
  pd:
    baseImage: pingcap/pd-arm64
    # ...
  tidb:
    baseImage: pingcap/tidb-arm64
    # ...
  tikv:
    baseImage: pingcap/tikv-arm64
    # ...
  pump:
    baseImage: pingcap/tidb-binlog-arm64
    # ...
  ticdc:
    baseImage: pingcap/ticdc-arm64
    # ...
  tiflash:
    baseImage: pingcap/tiflash-arm64
    # ...
```

## 初始化 TiDB 集群

部署步骤与文档 [初始化 TiDB 集群](initialize-a-cluster) 中相同，仅需要将 TidbInitializer 定义文件中的 `spec.image` 字段设置为 ARM64 版本镜像。

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbInitializer
metadata:
  name: ${initializer_name}
  namespace: ${cluster_namespace}
spec:
  image: kanshiori/mysqlclient-arm64
  # ...
```

## 部署 TiDB 集群监控

部署步骤与文档 [TiDB 集群的监控与告警](monitor-a-tidb-cluster) 中相同，仅需要将 TidbMonitor 定义文件中的 `spec.initializer.baseImage` 与 `spec.reloader.baseImage` 字段设置为 ARM64 版本镜像。

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: ${monitor_name}
spec:
  # ...
  initializer:
    baseImage: pingcap/tidb-monitor-initializer-arm64
    version: v5.1.0
  reloader:
    baseImage: pingcap/tidb-monitor-reloader
    version: v1.0.1
  # ...
```