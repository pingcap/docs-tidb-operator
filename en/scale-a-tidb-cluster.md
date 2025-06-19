---
title: Manually Scale TiDB on Kubernetes
summary: Learn how to manually scale a TiDB cluster on Kubernetes, including horizontal scaling and vertical scaling.
---

# Manually Scale TiDB on Kubernetes

This document introduces how to horizontally and vertically scale a TiDB cluster on Kubernetes.

## Horizontal scaling

Horizontal scaling refers to increasing or decreasing the number of Pods in a component to scale the cluster. You can control the number of Pods by modifying the value of `replicas` of a certain component to scale out or scale in.

* To scale out a TiDB cluster, **increase** the value of `replicas` of a certain component. The scaling out operations add Pods until the number of Pods equals the value of `replicas`.
* To scale in a TiDB cluster, **decrease** the value of `replicas` of a certain component. The scaling in operations remove Pods until the number of Pods equals the value of `replicas`.

### Horizontally scale PD, TiKV, TiDB, and TiCDC

To scale PD, TiKV, TiDB, or TiCDC horizontally, use `kubectl` to modify the `spec.replicas` field in the corresponding component group custom resource (CR) to the desired value.

1. Modify the `replicas` value of a component as needed. For example, configure the `replicas` value of PD to `3`:

    ```shell
    kubectl patch -n ${namespace} pdgroup ${name} --type merge --patch '{"spec":{"replicas":3}}'
    ```

2. Verify that the Component Group CR for the corresponding component in the Kubernetes cluster has been updated to the expected configuration. For example, run the following command to check the PDGroup CR:

    ```shell
    kubectl get pdgroup ${name} -n ${namespace}
    ```

    The `DESIRED` value in the output should match the value you have configured.

3. Check whether the number of Pods has increased or decreased:

    ```shell
    kubectl -n ${namespace} get pod -w
    ```

    For the PD and TiDB components, it might take 10 seconds to 30 seconds to scale in or out.

    For the TiKV component, it might take 3 minutes to 5 minutes to scale in or out because the process involves data migration.

### Horizontally scale TiFlash

This section describes how to horizontally scale out or scale in TiFlash if you have deployed TiFlash in the cluster.

#### Horizontally scale out TiFlash

To scale out TiFlash horizontally, you can modify `spec.replicas` in the TiFlashGroup CR. For example, configure the `replicas` value of TiFlash to `3`:

```shell
kubectl patch -n ${namespace} tiflashgroup ${name} --type merge --patch '{"spec":{"replicas":3}}'
```

#### Horizontally scale in TiFlash

To scale in TiFlash horizontally, perform the following steps:

1. Expose the PD service by using `port-forward`:

    ```shell
    kubectl port-forward -n ${namespace} svc/${pd_group_name}-pd 2379:2379
    ```

2. Open a **new** terminal tab or window. Check the maximum number (`N`) of replicas of all data tables with which TiFlash is enabled by running the following command:

    ```shell
    curl 127.0.0.1:2379/pd/api/v1/config/rules/group/tiflash | grep count
    ```

    In the printed result, the largest value of `count` is the maximum number (`N`) of replicas of all data tables.

3. Go back to the terminal window in Step 1, where `port-forward` is running. Press <kbd>Ctrl</kbd>+<kbd>C</kbd> to stop `port-forward`.

4. After the scale-in operation, if the number of remaining Pods in TiFlash >= `N`, skip to Step 6. Otherwise, take the following steps:

    1. Refer to [Access TiDB](access-tidb.md) and connect to the TiDB service.

    2. For all the tables that have more replicas than the remaining Pods in TiFlash, run the following command:

        ```sql
        alter table <db_name>.<table_name> set tiflash replica ${pod_number};
        ```

        `${pod_number}` indicates the number of remaining Pods in the TiFlash cluster after scaling in.

5. Wait for the number of TiFlash replicas in the related tables to be updated.

    Connect to the TiDB service, and run the following command to check the number:

    ```sql
    SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>';
    ```

6. Modify `spec.replicas` to scale in TiFlash.

    Check whether TiFlash in the TiDB cluster on Kubernetes has updated to your desired definition. Run the following command and see whether the value of `DESIRED` returned is expected:

    ```shell
    kubectl get tiflashgroup ${name} -n ${namespace}
    ```

### View the horizontal scaling status

To view the scaling status of the cluster, run the following command:

```shell
kubectl -n ${namespace} get pod -w
```

When the number of Pods for all components reaches the preset value and all components go to the `Running` state, the horizontal scaling is completed.

> **Note:**
>
> - When the TiKV component scales in, TiDB Operator calls the PD interface to mark the corresponding TiKV instance as offline, and then migrates the data on it to other TiKV nodes. During the data migration, the TiKV Pod is still in the `Running` state, and the corresponding Pod is deleted only after the data migration is completed. The time consumed by scaling in depends on the amount of data on the TiKV instance to be scaled in. You can check whether TiKV is in the `Removing` state by running `kubectl get -n ${namespace} tikv`.
> - When the number of `Serving` TiKV is equal to or less than the value of the `MaxReplicas` parameter in the PD configuration, the TiKV components cannot be scaled in.
> - The TiKV component does not support scaling out while a scale-in operation is in progress. Forcing a scale-out operation might cause anomalies in the cluster. If an anomaly already happens, refer to [TiKV Store is in Tombstone status abnormally](exceptions.md#tikv-store-is-in-tombstone-status-abnormally) to fix it.
> - The TiFlash component has the same scale-in logic as TiKV.

## Vertical scaling

Vertically scaling TiDB means that you scale TiDB up or down by increasing or decreasing the limit of resources on the Pod. Vertical scaling is essentially the rolling update of the Pods.

To vertically scale up or scale down components including PD, TiKV, TiDB, TiFlash, and TiCDC, use `kubectl` to modify `spec.template.spec.resources` in the Component Group CR object that corresponds to the cluster to desired values.

### View the vertical scaling progress

To view the upgrade progress of the cluster, run the following command:

```shell
kubectl -n ${namespace} get pod -w
```

When all Pods are rebuilt and in the `Running` state, the vertical scaling is completed.

> **Note:**
>
> - If the resource's `requests` field is modified during the vertical scaling process, and if PD, TiKV, TiFlash, and TiCDC use `Local PV`, they will be scheduled back to the original node after the upgrade. At this time, if the original node does not have enough resources, the Pod ends up staying in the `Pending` status and thus impacts the service.
> - TiDB is a horizontally scalable database, so it is recommended to take advantage of it simply by adding more nodes rather than upgrading hardware resources like you do with a traditional database.

## Scaling troubleshooting

During the horizontal or vertical scaling operation, Pods might go to the Pending state because of insufficient resources. See [Troubleshoot the Pod in Pending state](deploy-failures.md#the-pod-is-in-the-pending-state) to resolve it.
