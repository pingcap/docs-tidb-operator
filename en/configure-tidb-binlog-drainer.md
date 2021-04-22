---
title: TiDB Binlog Drainer Configurations in Kubernetes
summary: Learn the configurations of a TiDB Binlog Drainer in Kubernetes.
aliases: ['/docs/tidb-in-kubernetes/stable/configure-tidb-binlog-drainer/','/docs/tidb-in-kubernetes/v1.1/configure-tidb-binlog-drainer/','/docs/stable/tidb-in-kubernetes/reference/configuration/tidb-drainer/']
---

# TiDB Binlog Drainer Configurations in Kubernetes

This document introduces the configuration parameters for a TiDB Binlog drainer in Kubernetes.

## Configuration parameters

The following table contains all configuration parameters available for the `tidb-drainer` chart.  Refer to [Use Helm](tidb-toolkit.md#use-helm) to learn how to configure these parameters.

| Parameter | Description | Default Value |
| :----- | :---- | :----- |
| `timezone` | Timezone configuration | `UTC` |
| `drainerName` | The name of `Statefulset` | `""` |
| `clusterName` | The name of the source TiDB cluster | `demo` |
| `clusterVersion` | The version of the source TiDB cluster | `v3.0.1` |
| `baseImage` | The base image of TiDB Binlog | `pingcap/tidb-binlog` |
| `imagePullPolicy` | The pulling policy of the image | `IfNotPresent` |
| `logLevel` | The log level of the drainer process | `info` |
| `storageClassName` | `storageClass` used by the drainer. `storageClassName` refers to a type of storage provided by the Kubernetes cluster, which might map to a level of service quality, a backup policy, or to any policy determined by the cluster administrator. Detailed reference: [storage-classes](https://kubernetes.io/docs/concepts/storage/storage-classes) | `local-storage` |
| `storage` | The storage limit of the drainer Pod. Note that you should set a larger size if `db-type` is set to `pb` | `10Gi` |
| `disableDetect` |  Determines whether to disable casualty detection | `false` |
| `initialCommitTs` |  Used to initialize a checkpoint if the drainer does not have one. The value is a string type, such as `"424364429251444742"` | `"-1"` |
| `tlsCluster.enabled` | Whether or not to enable TLS between clusters | `false` |
| `config` | The configuration file passed to the drainer. Detailed reference: [drainer.toml](https://github.com/pingcap/tidb-binlog/blob/master/cmd/drainer/drainer.toml) | (see below) |
| `resources` | The resource limits and requests of the drainer Pod | `{}` |
| `nodeSelector` | Ensures that the drainer Pod is only scheduled to the node with the specific key-value pair as the label. Detailed reference: [nodeselector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) | `{}` |
| `tolerations` | Applies to drainer Pods, allowing the Pods to be scheduled to the nodes with specified taints. Detailed reference: [taint-and-toleration](https://kubernetes.io/docs/concepts/configuration/taint-and-toleration) | `{}` |
| `affinity` | Defines scheduling policies and preferences of the drainer Pod. Detailed reference: [affinity-and-anti-affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) | `{}` |

The default value of `config` is:

```toml
detect-interval = 10
compressor = ""
[syncer]
worker-count = 16
disable-dispatch = false
ignore-schemas = "INFORMATION_SCHEMA,PERFORMANCE_SCHEMA,mysql"
safe-mode = false
txn-batch = 20
db-type = "file"
[syncer.to]
dir = "/data/pb"
```
