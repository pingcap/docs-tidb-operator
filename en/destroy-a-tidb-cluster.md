---
title: Destroy TiDB Clusters in Kubernetes
summary: Learn how to delete TiDB Cluster in Kubernetes.
category: how-to
---

# Destroy TiDB Clusters in Kubernetes

This document describes how to deploy TiDB clusters in Kubernetes.

## Destroy TiDB clusters managed by TidbCluster

To destroy a TiDB cluster managed by TidbCluster, run the following command:

{{< copyable "shell-regular" >}}

```shell
kubectl delete tc <cluster-name> -n <namespace>
```

If you deploy the monitor in the cluster using `TidbMonitor`, run the folowing command to delete the monitor component:

{{< copyable "shell-regular" >}}

```shell
kubectl delete tidbmonitor <tidb-monitor-name> -n <namespace>
```

## Destroy TiDB clusters managed by Helm

To destroy a TiDB cluster managed by Helm, run the following command:

{{< copyable "shell-regular" >}}

```shell
helm delete <cluster-name> --purge
```

## Delete data

The above commands that destroy the cluster only remove the running Pod, but the data is still retained. If you want the data to be deleted as well, you can use the following commands:

> **Warning:**
>
> The following commands deletes your data completely. Please be cautious.

{{< copyable "shell-regular" >}}

```shell
kubectl delete pvc -n <namespace> -l app.kubernetes.io/instance=<cluster-name>,app.kubernetes.io/managed-by=tidb-operator
```

{{< copyable "shell-regular" >}}

```shell
kubectl get pv -l app.kubernetes.io/namespace=<namespace>,app.kubernetes.io/managed-by=tidb-operator,app.kubernetes.io/instance=<cluster-name> -o name | xargs -I {} kubectl patch {} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
```
