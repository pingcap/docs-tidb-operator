---
title: Destroy TiDB Clusters on Kubernetes
summary: Learn how to delete TiDB Cluster on Kubernetes.
---

# Destroy TiDB Clusters on Kubernetes

This document describes how to destroy TiDB clusters on Kubernetes.

## Destroy a TiDB cluster managed by `Cluster`

To destroy a TiDB cluster managed by `Cluster`, run the following command:

```shell
kubectl delete cluster ${cluster_name} -n ${namespace}
```
