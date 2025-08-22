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

To scale a TiDB cluster horizontally, use `kubectl` to modify the `spec.replicas` field in the corresponding Component Group Custom Resource (CR) object to the desired value.

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

    When the number of Pods for all components reaches the preset value and all components go to the `Running` state, the horizontal scaling is completed.

    PD and TiDB components usually take 10 to 30 seconds to scale in or out.

    TiKV components usually take 3 to 5 minutes to scale in or out because the process involves data migration.

> **Note:**
>
> - When the TiKV component scales in, TiDB Operator calls the PD interface to mark the corresponding TiKV instance as offline, and then migrates the data on it to other TiKV nodes. During the data migration, the TiKV Pod is still in the `Running` state, and the corresponding Pod is deleted only after the data migration is completed. The time consumed by scaling in depends on the amount of data on the TiKV instance to be scaled in. You can check whether TiKV is in the `Removing` state by running `kubectl get -n ${namespace} tikv`.
> - When the number of `Serving` TiKV is equal to or less than the value of the `MaxReplicas` parameter in the PD configuration, the TiKV components cannot be scaled in.
> - The TiKV component does not support scaling out while a scale-in operation is in progress. Forcing a scale-out operation might cause anomalies in the cluster.
> - The TiFlash component has the same scale-in logic as TiKV.

## Vertical scaling

Vertically scaling TiDB means that you scale TiDB up or down by increasing or decreasing the limit of resources on the Pod. Vertical scaling is essentially the rolling update of the Pods.

To vertically scale up or scale down components including PD, TiKV, TiDB, TiProxy, TiFlash, and TiCDC, use `kubectl` to modify `spec.template.spec.resources` in the Component Group CR object that corresponds to the cluster to desired values.

> **Note:**
>
> Currently, [In-Place Pod Resize](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/) is not supported.

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
