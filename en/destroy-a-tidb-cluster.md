---
title: Destroy TiDB Clusters in Kubernetes
summary: Learn how to delete TiDB Cluster in Kubernetes.
aliases: ['/docs/tidb-in-kubernetes/stable/destroy-a-tidb-cluster/','/docs/tidb-in-kubernetes/v1.1/destroy-a-tidb-cluster/','/docs/v3.0/tidb-in-kubernetes/maitain/delete-tidb-cluster/']
---

# Destroy TiDB Clusters in Kubernetes

This document describes how to deploy TiDB clusters in Kubernetes.

## Destroy a TiDB cluster managed by `TidbCluster`

To destroy a TiDB cluster managed by `TidbCluster`, run the following command:

{{< copyable "shell-regular" >}}

```shell
kubectl delete tc ${cluster_name} -n ${namespace}
```

If you deploy the monitor in the cluster using `TidbMonitor`, run the following command to delete the monitor component:

{{< copyable "shell-regular" >}}

```shell
kubectl delete tidbmonitor ${tidb_monitor_name} -n ${namespace}
```

## Destroy a TiDB cluster managed by Helm

To destroy a TiDB cluster managed by Helm, run the following command:

{{< copyable "shell-regular" >}}

```shell
helm delete ${cluster_name} --purge
```

## Delete data

The above commands that destroy the cluster only remove the running Pod, but the data is still retained. If you want to delete the data as well, use the following commands:

> **Warning:**
>
> The following commands delete your data completely. Please be cautious.
>
> To ensure data safety, do not delete PVs on any circumstances, unless you are familiar with the working principles of PVs.

{{< copyable "shell-regular" >}}

```shell
kubectl delete pvc -n ${namespace} -l app.kubernetes.io/instance=${cluster_name},app.kubernetes.io/managed-by=tidb-operator
```

{{< copyable "shell-regular" >}}

```shell
kubectl get pv -l app.kubernetes.io/namespace=${namespace},app.kubernetes.io/managed-by=tidb-operator,app.kubernetes.io/instance=${cluster_name} -o name | xargs -I {} kubectl patch {} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
```
