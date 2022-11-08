---
title: Manually Scale TiDB on Kubernetes
summary: Learn how to manually scale a TiDB cluster on Kubernetes.
---

# Manually Scale TiDB on Kubernetes

This document introduces how to horizontally and vertically scale a TiDB cluster on Kubernetes.

## Horizontal scaling

Horizontally scaling TiDB means that you scale TiDB out or in by adding or remove Pods in your pool of resources. When you scale a TiDB cluster, PD, TiKV, and TiDB are scaled out or in sequentially according to the values of their replicas.

- To scale out a TiDB cluster, **increase** the value of `replicas` of a certain component. The scaling out operations add Pods based on the Pod ID in ascending order, until the number of Pods equals the value of `replicas`.

- To scale in a TiDB cluster, **decrease** the value of `replicas` of a certain component. The scaling in operations remove Pods based on the Pod ID in descending order, until the number of Pods equals the value of `replicas`.

### Horizontally scale PD, TiKV, and TiDB

To scale PD, TiKV, or TiDB horizontally, use kubectl to modify `spec.pd.replicas`, `spec.tikv.replicas`, and `spec.tidb.replicas` in the `TidbCluster` object of the cluster to a desired value.

1. Modify the `replicas` value of a component as needed. For example, configure the `replicas` value of PD to 3:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch -n ${namespace} tc ${cluster_name} --type merge --patch '{"spec":{"pd":{"replicas":3}}}'
    ```

2. Check whether your configuration has been updated in the corresponding TiDB cluster on Kubernetes.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get tidbcluster ${cluster_name} -n ${namespace} -oyaml
    ```

    If your configuration is successfully updated, in the `TidbCluster` CR output by the command above, the values of `spec.pd.replicas`, `spec.tidb.replicas`, and `spec.tikv.replicas` are consistent with the values you have configured.

3. Check whether the number of `TidbCluster` Pods has increased or decreased.

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    For the PD and TiDB components, it might take 10-30 seconds to scale in or out.

    For the TiKV component, it might take 3-5 minutes to scale in or out because the process involves data migration.

### Horizontally scale TiFlash

This section describes how to horizontally scale out or scale in TiFlash if you have deployed TiFlash in the cluster.

#### Horizontally scale out TiFlash

To scale out TiFlash horizontally, you can modify `spec.tiflash.replicas`.

For example, configure the `replicas` value of TiFlash to 3:

{{< copyable "shell-regular" >}}

```shell
kubectl patch -n ${namespace} tc ${cluster_name} --type merge --patch '{"spec":{"tiflash":{"replicas":3}}}'
```

#### Horizontally scale in TiFlash

To scale in TiFlash horizontally, perform the following steps:

1. Expose the PD service by using `port-forward`:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl port-forward -n ${namespace} svc/${cluster_name}-pd 2379:2379
    ```

2. Open a **new** terminal tab or window. Check the maximum number (`N`) of replicas of all data tables with which TiFlash is enabled by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    curl 127.0.0.1:2379/pd/api/v1/config/rules/group/tiflash | grep count
    ```

    In the printed result, the largest value of `count` is the maximum number (`N`) of replicas of all data tables.

3. Go back to the terminal window in Step 1, where `port-forward` is running. Press <kbd>Ctrl</kbd>+<kbd>C</kbd> to stop `port-forward`.

4. After the scale-in operation, if the number of remaining Pods in TiFlash >= `N`, skip to Step 6. Otherwise, take the following steps:

    1. Refer to [Access TiDB](access-tidb.md) and connect to the TiDB service.

    2. For all the tables that have more replicas than the remaining Pods in TiFlash, run the following command:

        {{< copyable "sql" >}}

        ```sql
        alter table <db_name>.<table_name> set tiflash replica ${pod_number};
        ```

        `${pod_number}` indicates the number of remaining Pods in the TiFlash cluster after scaling in.

5. Wait for the number of TiFlash replicas in the related tables to be updated.

    Connect to the TiDB service, and run the following command to check the number:

    {{< copyable "sql" >}}

    ```sql
    SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>';
    ```

    If you cannot view the replication information of related tables, the TiFlash replicas are successfully deleted.

6. Modify `spec.tiflash.replicas` to scale in TiFlash.

    Check whether TiFlash in the TiDB cluster on Kubernetes has updated to your desired definition. Run the following command and see whether the value of `spec.tiflash.replicas` returned is expected:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get tidbcluster ${cluster-name} -n ${namespace} -oyaml
    ```

### Horizontally scale TiCDC

If TiCDC is deployed in the cluster, you can horizontally scale out or scale in TiCDC by modifying the value of `spec.ticdc.replicas`.

For example, configure the `replicas` value of TiCDC to 3:

{{< copyable "shell-regular" >}}

```shell
kubectl patch -n ${namespace} tc ${cluster_name} --type merge --patch '{"spec":{"ticdc":{"replicas":3}}}'
```

### View the horizontal scaling status

To view the scaling status of the cluster, run the following command:

{{< copyable "shell-regular" >}}

```shell
watch kubectl -n ${namespace} get pod -o wide
```

When the number of Pods for all components reaches the preset value and all components go to the `Running` state, the horizontal scaling is completed.

> **Note:**
>
> - The PD, TiKV and TiFlash components do not trigger the rolling update operations during scaling in and out.
> - When the TiKV component scales in, TiDB Operator calls the PD interface to mark the corresponding TiKV instance as offline, and then migrates the data on it to other TiKV nodes. During the data migration, the TiKV Pod is still in the `Running` state, and the corresponding Pod is deleted only after the data migration is completed. The time consumed by scaling in depends on the amount of data on the TiKV instance to be scaled in. You can check whether TiKV is in the `Offline` state by running `kubectl get -n ${namespace} tidbcluster ${cluster_name} -o json | jq '.status.tikv.stores'`.
> - When the number of `UP` stores is equal to or less than the parameter value of `MaxReplicas` in the PD configuration, the TiKV components can not be scaled in.
> - The TiKV component does not support scale out while a scale-in operation is in progress. Forcing a scale-out operation might cause anomalies in the cluster. If an anomaly already happens, refer to [TiKV Store is in Tombstone status abnormally](exceptions.md#tikv-store-is-in-tombstone-status-abnormally) to fix it.
> - The TiFlash component has the same scale-in logic as TiKV.
> - When the PD, TiKV, and TiFlash components scale in, the PVC of the deleted node is retained during the scaling in process. Because the PV's reclaim policy is changed to `Retain`, the data can still be retrieved even if the PVC is deleted.

## Vertical scaling

Vertically scaling TiDB means that you scale TiDB up or down by increasing or decreasing the limit of resources on the Pod. Vertically scaling is essentially the rolling update of the Pods.

### Vertically scale components

This section describes how to vertically scale up or scale down components including PD, TiKV, TiDB, TiFlash, and TiCDC.

- To scale up or scale down PD, TiKV, TiDB, use kubectl to modify `spec.pd.resources`, `spec.tikv.resources`, and `spec.tidb.resources` in the `TidbCluster` object that corresponds to the cluster to a desired value.

- To scale up or scale down TiFlash, modify the value of `spec.tiflash.resources`.

- To scale up or scale down TiCDC, modify the value of `spec.ticdc.resources`.

### View the vertical scaling progress

To view the upgrade progress of the cluster, run the following command:

{{< copyable "shell-regular" >}}

```shell
watch kubectl -n ${namespace} get pod -o wide
```

When all Pods are rebuilt and in the `Running` state, the vertical scaling is completed.

> **Note:**
>
> - If the resource's `requests` field is modified during the vertical scaling process, and if PD, TiKV, and TiFlash use `Local PV`, they will be scheduled back to the original node after the upgrade. At this time, if the original node does not have enough resources, the Pod ends up staying in the `Pending` status and thus impacts the service.
> - TiDB is a horizontally scalable database, so it is recommended to take advantage of it simply by adding more nodes rather than upgrading hardware resources like you do with a traditional database.

## Scaling troubleshooting

During the horizontal or vertical scaling operation, Pods might go to the Pending state because of insufficient resources. See [Troubleshoot the Pod in Pending state](deploy-failures.md#the-pod-is-in-the-pending-state) to resolve it.
