---
title: Automatic Failover
summary: Learn the automatic failover policies of TiDB cluster components on Kubernetes.
---

# Automatic Failover

TiDB Operator manages the deployment and scaling of Pods based on `StatefulSet`. When some Pods or nodes fail, `StatefulSet`does not support automatically creating new Pods to replace the original ones. To solve this issue, TiDB Operator supports the automatic failover feature by scaling Pods automatically.

## Configure automatic failover

The automatic failover feature is enabled by default in TiDB Operator. 

When deploying TiDB Operator, you can configure the waiting timeout for failover of PD, TiKV, TiDB, and TiFlash components in a TiDB cluster in the `charts/tidb-operator/values.yaml` file. An example is as follows.

```yaml
controllerManager:
 ...
 # autoFailover is whether tidb-operator should auto failover when failure occurs
 autoFailover: true
 # pd failover period default(5m)
 pdFailoverPeriod: 5m
 # tikv failover period default(5m)
 tikvFailoverPeriod: 5m
 # tidb failover period default(5m)
 tidbFailoverPeriod: 5m
 # tiflash failover period default(5m)
 tiflashFailoverPeriod: 5m
```

In the example, `pdFailoverPeriod`, `tikvFailoverPeriod`, `tiflashFailoverPeriod` and `tidbFailoverPeriod` indicate the waiting timeout (5 minutes by default) after an instance failure is identified. After the timeout, TiDB Operator begins the automatic failover process.

In addition, when configuring a TiDB cluster, you can specify the threshold number of Pods that the TiDB Operator can scale in case of automatic failover of each component via `spec.${component}.maxFailoverCount`. For more information, refer to [TiDB Component Configuration Documentation](configure-a-tidb- cluster.md#configure-a-pdtidbtikvtiflash-failure-auto-transfer-threshold).

> **Note:**
> 
> If there are not enough resources in the cluster for TiDB Operator to create new Pods, the new  Pods will be in the Pending state.

## Automatic failover policies

There are six components in a TiDB cluster - PD, TiKV, TiDB, TiFlash, TiCDC and Pump. Currently, TiCDC and Pump do not support the automatic failover feature, and PD, TiKV, TiDB and TiFlash have different failover policies. This section gives an in-depth introduction to these policies.

### Failover with PD

TiDB Operator collects the health status of PD members via the `pd/health` PD API and records the status in the `.status.pd.members` field of the TidbCluster CR.

Take a PD cluster with 3 Pods as an example. If a Pod fails for more than 5 minutes (`pdFailoverPeriod` is configurable), TiDB Operator automatically does the following operations:

1. TiDB Operator records this Pod information in the `.status.pd.failureMembers` field of TidbCluster CR.
2. TiDB Operator takes this Pod offline: TiDB Operator calls PD API to remove this Pod from the member list, and then deletes the Pod and its PVC. 
3. The StatefulSet controller recreates this Pod, and this Pod will join the cluster as a new member.
4. When calculating the replicas of PD StatefulSet, TiDB Operator takes the deleted `.status.pd.failureMembers` into account, so it will create a new Pod. Then, 4 Pods will exist at the same time.

When all the failed Pods in the cluster get back to normal, TiDB Operator will automatically delete the newly created Pods, and the number of Pods get back to the original.

> **Note:**
>
> - For each PD cluster, the number of new Pods that TiDB Operator can create is up to `spec.pd.maxFailoverCount` (the default value is `3`). After the threshold is reached, TiDB Operator will not perform failover. 
> - If most members in a PD cluster fail, which makes the PD cluster unavailable, TiDB Operator will not perform failover for the PD cluster.

### Failover with TiDB

TiDB Operator collects the Pod health status by accessing the `/status` interface of each TiDB Pod and records the status in the `.status.tidb.members` field of the TidbCluster CR.

Take a TiDB cluster with 3 Pods as an example. If a Pod fails for more than 5 minutes (`tidbFailoverPeriod` is configurable), TiDB Operator automatically does the following operations:

1. TiDB Operator records this Pod information in the `.status.tidb.failureMembers` field of TidbCluster CR. 
2. When calculating the replicas of TiDB StatefulSet, TiDB Operator takes the `.status.tidb.failureMembers` into account, so it will create a new Pod. Then, 4 Pods will exist at the same time.

When the failed Pod in the cluster gets back to normal, TiDB Operator will automatically delete the newly created Pod, and the number of Pods get back to 3.

> **Note:**
>
> For each TiDB cluster, the number of new Pods that TiDB Operator can create is up to `spec.tidb.maxFailoverCount` (the default value is `3`). After the threshold is reached, TiDB Operator will not perform failover.

### Failover with TiKV

TiDB Operator collects the TiKV store health status by accessing the PD API and records the status in the `.status.tikv.stores` field in TidbCluster CR.

Take a TiKV cluster with 3 Pods as an example. When a TiKV Pod fails, the store status of the Pod changes to `Disconnected`. By default, after 30 minutes (configurable by changing `max-store-down-time = "30m"` in the `[schedule]` section of `pd.config`), the status changes to `Down`. Then, TiDB Operator automatically does the following operations:

1. Wait for another 5 minutes (configurable by modifying `tikvFailoverPeriod`), if this TiKV Pod is still not recovered, TiDB Operator records this Pod information in the `.status.tikv.failureStores` field of TidbCluster CR.
2. When calculating the replicas of TiKV StatefulSet, TiDB Operator takes the `.status.tikv.failureStores` into account, so it will create a new Pod. Then, 4 Pods will exist at the same time.

When the failed Pod in the cluster recovers, TiDB Operator **DOES NOT** scale in the newly created Pod, but continues to keep 4 Pods. This is because scaling in TiKV Pods will trigger data migration, which might affect the cluster performance.

> **Note:**
>
> For each TiKV cluster, the number of new Pods that TiDB Operator can create is up to `spec.tikv.maxFailoverCount` (the default value is `3`). After the threshold is reached, TiDB Operator will not perform failover.

If **all** failed Pods have recovered, and you want to scale in the newly created Pods, you can follow the procedure below:

Configure `spec.tikv.recoverFailover: true` (Supported since TiDB Operator v1.1.5):

{{< copyable "shell-regular" >}}

```shell
kubectl edit tc -n ${namespace} ${cluster_name}
```

TiDB Operator will scale in the newly created Pods automatically. When the scaling in is finished, configure `spec.tikv.recoverFailover: false` to avoid the auto-scaling operation when the next failover occurs and recovers.

### Failover with TiFlash

TiDB Operator collects the TiFlash store health status by accessing the PD API and records the status in the `.status.tiflash.stores` field in TidbCluster CR.

Take a TiFlash cluster with 3 Pods as an example. When a TiFlash Pod fails, the store status of the Pod changes to `Disconnected`. By default, after 30 minutes (configurable by changing `max-store-down-time = "30m"` in the `[schedule]` section of `pd.config`), the status changes to `Down`. Then, TiDB Operator automatically does the following operations:

1. Wait for another 5 minutes (configurable by modifying `tiflashFailoverPeriod`), if this TiFlash Pod is still not recovered, TiDB Operator records this Pod information in the `.status.tiflash.failureStores` field of TidbCluster CR.
2. When calculating the replicas of TiFlash StatefulSet, TiDB Operator takes the `.status.tiflash.failureStores` into account, so it will create a new Pod. Then, 4 Pods will exist at the same time.

When the failed Pod in the cluster recovers, TiDB Operator **DOES NOT** scale in the newly created Pod, but continues to keep 4 Pods. This is because scaling in TiFlash Pods will trigger data migration, which might affect the cluster performance.

> **Note:**
>
> For each TiFlash cluster, the number of new Pods that TiDB Operator can create is up to `spec.tiflash.maxFailoverCount` (the default value is `3`). After the threshold is reached, TiDB Operator will not perform failover.

If **all** of the failed Pods have recovered, and you want to scale in the newly created Pods, you can follow the procedure below:

Configure `spec.tiflash.recoverFailover: true` (Supported since TiDB Operator v1.1.5):

{{< copyable "shell-regular" >}}

```shell
kubectl edit tc -n ${namespace} ${cluster_name}
```

TiDB Operator will scale in the newly created Pods automatically. When the scaling in is finished, configure `spec.tiflash.recoverFailover: false` to avoid the auto-scaling operation when the next failover occurs and recovers.

### Disable automatic failover

You can disable the automatic failover feature at the cluster or component level:

- To disable the automatic failover feature at the cluster level, set `controllerManager.autoFailover` to `false` in the `charts/tidb-operator/values.yaml` file when deploying TiDB Operator. For example:

```yaml
controllerManager:
 serviceAccount: tidb-controller-manager
 logLevel: 2
 replicas: 1
 resources:
   limits:
     cpu: 250m
     memory: 150Mi
   requests:
     cpu: 80m
     memory: 50Mi
 # autoFailover is whether tidb-operator should auto failover when failure occurs
 autoFailover: false
 # pd failover period default(5m)
 pdFailoverPeriod: 5m
 # tikv failover period default(5m)
 tikvFailoverPeriod: 5m
 # tidb failover period default(5m)
 tidbFailoverPeriod: 5m
 # tiflash failover period default(5m)
 tiflashFailoverPeriod: 5m
```

- To disable the automatic failover feature at the component level, set `spec.${component}.maxFailoverCount` of the target component to `0` in the TidbCluster CR.
