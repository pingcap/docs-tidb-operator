---
title: Deploy a TiDB Cluster on ARM64 Machine
summary: Learn how to deploy a TiDB cluster on ARM64 Machine.
---

# Deploy a TiDB Cluster on ARM64 Machine

This document describes how to deploy a TiDB cluster on ARM64 machine.

## Prerequisites

Before starting the process, make sure Kubernetes is deployed on your ARM64 machine. If Kubernetes is not deployed, refer to [Deploy the Kubernetes cluster](deploy-tidb-operator.md#deploy-the-kubernetes-cluster).

## Deploy TiDB operator

The process of deploying TiDB operator on ARM64 machine is the same as the process of [Deploy TiDB Operator in Kubernetes](deploy-tidb-operator.md). The only difference is the following part in the step [Customize TiDB operator deployment](deploy-tidb-operator.md#customize-tidb-operator-deployment): after getting the `values.yaml` file of the `tidb-operator` chart, you need to modify the fields of `operatorImage` and `tidbBackupManagerImage` in that file to the image of ARM64 version. For example:

```yaml
# ...
operatorImage: pingcap/tidb-operator-arm64:v1.2.4
# ...
tidbBackupManagerImage: pingcap/tidb-backup-manager-arm64:v1.2.4
# ...
```

## Deploy a TiDB cluster

The process of deploying a TiDB cluster on ARM64 machine is the same as the process of [Deploy TiDB in General Kubernetes](deploy-on-general-kubernetes.md). The only difference is that you need to set the images of the related components in the TidbCluster definition file to ARM64 version. For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: ${cluster_name}
  namespace: ${cluster_namespace}
spec:
  version: "v5.2.1"
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

## Initialize a TiDB Cluster

The process of initializing a TiDB cluster on ARM64 machine is the same as the process of [Initialize a TiDB Cluster in Kubernetes](initialize-a-cluster.md). The only difference is that you need to modify the field `spec.image` in the TidbInitializer definition file to the image of ARM64 version. For example:

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

## Deploy monitoring for a TiDB cluster

The process of deploying monitoring for a TiDB cluster on ARM64 machine is the same as the process of [Deploy Monitoring and Alerts for a TiDB Cluster](monitor-a-tidb-cluster.md). The only difference is that you need to modify the fields of `spec.initializer.baseImage` and `spec.reloader.baseImage` in the TidbMonitor definition file to the image of ARM64 version.

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbMonitor
metadata:
  name: ${monitor_name}
spec:
  # ...
  initializer:
    baseImage: pingcap/tidb-monitor-initializer-arm64
    version: v5.2.1
  reloader:
    baseImage: pingcap/tidb-monitor-reloader-arm64
    version: v1.0.1
  # ...
```