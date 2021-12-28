---
title: Recover the Deleted Cluster
summary: Learn how to recover a TiDB cluster that has been deleted mistakenly.
---

# Recover the Deleted Cluster

This document describes how to recover a TiDB cluster that has been deleted mistakenly in Kubernetes. If you have mistakenly deleted a TiDB cluster using TidbCluster, you can use the method introduced in this document to recover the cluster.

TiDB Operator uses PV (Persistent Volume) and PVC (Persistent Volume Claim) to store persistent data. If you accidentally delete a cluster using `kubectl delete tc`, the PV/PVC objects and data are still retained to ensure data safety.

To recover the deleted cluster, use the `kubectl create` command to create a cluster that has the same name and configuration as the deleted one. In the new cluster, the retained PV/PVC and data are reused.

{{< copyable "shell-regular" >}}

```shell
kubectl -n ${namespace} create -f tidb-cluster.yaml
```
