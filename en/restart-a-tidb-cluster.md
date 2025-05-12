---
title: Restart a TiDB Cluster on Kubernetes
summary: Learn how to restart a TiDB cluster on Kubernetes, including gracefully rolling restart all Pods in a component and rolling restart a specific Pod individually.
---

# Restart a TiDB Cluster on Kubernetes

When using a TiDB cluster, you might need to restart it if a Pod encounters issues such as memory leaks. This document explains how to perform a graceful rolling restart of all Pods in a component or restart a specific Pod individually.

> **Warning:**
>
> In production environments, it is strongly recommended not to forcefully delete Pods in the TiDB cluster. Although TiDB Operator will automatically recreate deleted Pods, this could cause some requests to the TiDB cluster to fail.

## Gracefully roll restart all Pods in a component

To perform a graceful rolling restart of all Pods in a component (such as PD, TiKV, or TiDB), modify the corresponding Component Group Custom Resource (CR) configuration. Add a `pingcap.com/restartedAt` label or annotation under the `.spec.template.metadata` section and set its value to a string that ensures idempotency, such as a timestamp.

The following example shows how to add an annotation for the PD component to trigger a graceful rolling restart of all PD Pods in the `PDGroup`:

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
spec:
  replicas: 3
  template:
    metadata:
      annotations:
        pingcap.com/restartedAt: 2025-06-30T12:00
```

## Gracefully roll restart a single Pod in a component

You can restart a specific Pod in the TiDB cluster. The process differs slightly depending on the component.

For a TiKV Pod, specify the `--grace-period` option when deleting the Pod to provide sufficient time to evict the Region leader. Otherwise, the operation might fail. The following command sets a 60-second grace period for the TiKV Pod:

```shell
kubectl -n ${namespace} delete pod ${pod_name} --grace-period=60
```

For other component Pods, you can delete them directly, and TiDB Operator will automatically handle a graceful restart:

```shell
kubectl -n ${namespace} delete pod ${pod_name}
```
