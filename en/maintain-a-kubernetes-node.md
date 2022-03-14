---
title: Maintain Kubernetes Nodes that Hold the TiDB Cluster
summary: Learn how to maintain Kubernetes nodes that hold the TiDB cluster.
aliases: ['/docs/tidb-in-kubernetes/dev/maintain-a-kubernetes-node/']
---

# Maintain Kubernetes Nodes that Hold the TiDB Cluster

TiDB is a highly available database that can run smoothly when some of the database nodes go offline. For this reason, you can safely shut down and maintain the Kubernetes nodes at the bottom layer without influencing TiDB's service. Specifically, you need to adopt various maintenance strategies when handling PD, TiKV, and TiDB Pods because of their different characteristics.

This document introduces how to perform a temporary or long-term maintenance task for the Kubernetes nodes.

## Prerequisites

- [`kubectl`](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [`tkctl`](use-tkctl.md)
- [`jq`](https://stedolan.github.io/jq/download/)

> **Note:**
>
> Before you maintain a node, you need to make sure that the remaining resources in the Kubernetes cluster are enough for running the TiDB cluster.

## Maintain a node that can be recovered shortly

1. Mark the node to be maintained as non-schedulable to ensure that no new Pod is scheduled to it:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cordon ${node_name}
    ```

2. Check whether there is any TiKV Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep tikv
    ```

    If any TiKV Pod is found, for each TiKV Pod, perform the following operations:

    1. [Evict the TiKV Region Leader](#evict-tikv-region-leader) to another Pod.

    2. Increase the maximum offline duration for TiKV Pods by configuring `max-store-down-time` of PD. After you maintain and recover the Kubernetes node within that duration, all TiKV Pods on that node will be automatically recovered.

        The following example shows how to set `max-store-down-time` to `60m`. You can set it to any reasonable value.

        {{< copyable "shell-regular" >}}

        ```shell
        pd-ctl config set max-store-down-time 60m
        ```

3. Check whether there is any PD Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep pd
    ```

    If any PD Pod is found, for each PD Pod, [transfer the PD leader](#transfer-pd-leader) to other Pods.

4. Confirm that the node to be maintained no longer has any TiKV Pod or PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

5. Migrate all Pods on the node to be maintained to other nodes:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl drain ${node_name} --ignore-daemonsets
    ```

    After running this command, all Pods on this node are automatically migrated to another available node.

6. Confirm that the node to be maintained no longer has any TiKV, TiDB, or PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

7. When the maintenance is completed, after you recover the node, make sure that the node is in a healthy state:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl get node ${node_name}
    ```

    After the node goes into the `Ready` state, proceed with the following operations.

8. Lift the scheduling restriction on the node:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl uncordon ${node_name}
    ```

9. Confirm that all Pods are running normally:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

    When all Pods are running normally, you have successfully finished the maintenance task.

## Maintain a node that cannot be recovered shortly

1. Check whether there is any TiKV Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep tikv
    ```

    If any TiKV Pod is found, for each TiKV Pod, [reschedule the TiKV Pod](#reschedule-tikv-pods) to another node.

2. Check whether there is any PD Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep pd
    ```

    If any PD Pod is found, for each PD Pod, [reschedule the PD Pod](#reschedule-pd-pods) to another node.

3. Confirm that the node to be maintained no longer has any TiKV Pod or PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

4. Migrate all Pods on the node to be maintained to other nodes:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl drain ${node_name} --ignore-daemonsets
    ```

    After running this command, all Pods on this node are automatically migrated to another available node.

5. Confirm that the node to be maintained no longer has any TiKV, TiDB, or PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name}
    ```

6. (Optional) If the node will be offline for a long time, it is recommended to delete the node from your Kubernetes cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete node ${node_name}
    ```

## Reschedule PD Pods

If a node will be offline for a long time, to minimize the impact on your application, you can reschedule the PD Pods on this node to other nodes in advance.

### If the node storage can be automatically migrated

If the node storage can be automatically migrated (such as EBS), to reschedule a PD Pod, you do not need to delete the PD member. You only need to transfer the PD Leader to another Pod and delete the old Pod.

1. Mark the node to be maintained as non-schedulable to ensure that no new Pod is scheduled to it:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cordon ${node_name}
    ```

2. Check the PD Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep pd
    ```

3. [Transfer the PD Leader](#transfer-pd-leader) to another Pod.

4. Delete the old PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete -n ${namespace} pod ${pod_name}
    ```

5. Confirm that the PD Pod is successfully scheduled to another node:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

### If the node storage cannot be automatically migrated

If the node storage cannot be automatically migrated (such as local storage), to reschedule a PD Pod, you need to delete the PD member.

1. Mark the node to be maintained as non-schedulable to ensure that no new Pod is scheduled to it:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cordon ${node_name}
    ```

2. Check the PD Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep pd
    ```

3. [Transfer the PD Leader](#transfer-pd-leader) to another Pod.

4. Take the PD Pod offline:

    {{< copyable "shell-regular" >}}

    ```shell
    pd-ctl member delete name ${pod_name}
    ```

5. Confirm that the PD member is deleted:

    {{< copyable "shell-regular" >}}

    ```shell
    pd-ctl member
    ```

6. Unbind the PD Pod with the local disk on the node.

    1. Check the `PersistentVolumeClaim` used by the Pod:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl -n ${namespace} get pvc -l tidb.pingcap.com/pod-name=${pod_name}
        ```

    2. Delete the `PersistentVolumeClaim`:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl delete -n ${namespace} pvc ${pvc_name} --wait=false
        ```

7. Delete the old PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete -n ${namespace} pod ${pod_name}
    ```

8. Confirm that the PD Pod is successfully scheduled to another node:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

## Reschedule TiKV Pods

If a node will be offline for a long time, to minimize the impact on your application, you can reschedule the TiKV Pods on this node to other nodes in advance.

### If the node storage can be automatically migrated

If the node storage can be automatically migrated (such as EBS), to reschedule a TiKV Pod, you do not need to delete the whole TiKV store. You only need to evict the TiKV Region Leader to another Pod and delete the old Pod.

1. Mark the node to be maintained as non-schedulable to ensure that no new Pod is scheduled to it:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cordon ${node_name}
    ```

2. Check the TiKV Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep tikv
    ```

3. Add annotation with a `tidb.pingcap.com/evict-leader` key to the TiKV Pod to trigger the graceful restart. After TiDB Operator evicts the TiKV Region Leader, TiDB Operator deletes the Pod.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl -n ${namespace} annotate pod ${pod_name} tidb.pingcap.com/evict-leader="delete-pod"
    ```

4. Confirm that the TiKV Pod is successfully scheduled to another node:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

5. Confirm that the Region Leader is transferred back:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} get tc ${cluster_name} -ojson | jq ".status.tikv.stores | .[] | select ( .podName == \"${pod_name}\" ) | .leaderCount"
    ```

### If the node storage cannot be automatically migrated

If the node storage cannot be automatically migrated (such as local storage), to reschedule a TiKV Pod, you need to delete the whole TiKV store.

1. Mark the node to be maintained as non-schedulable to ensure that no new Pod is scheduled to it:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cordon ${node_name}
    ```

2. Check the TiKV Pod on the node to be maintained:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod --all-namespaces -o wide | grep ${node_name} | grep tikv
    ```

3. [Recreate a TiKV Pod](#recreate-a-tikv-pod).

## Transfer PD Leader

1. Check the PD Leader:

    {{< copyable "shell-regular" >}}

    ```shell
    pd-ctl member leader show
    ```

2. If the Leader Pod is on the node to be maintained, you need to transfer the PD Leader to a Pod on another node:

    {{< copyable "shell-regular" >}}

    ```shell
    pd-ctl member leader transfer ${pod_name}
    ```

    `${pod_name}` is the name of the PD Pod on another node.

## Evict TiKV Region Leader

1. Add an annotation with a `tidb.pingcap.com/evict-leader` key to the TiKV Pod:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl -n ${namespace} annotate pod ${pod_name} tidb.pingcap.com/evict-leader="none"
    ```

2. Confirm that all Region Leaders are migrated:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} get tc ${cluster_name} -ojson | jq ".status.tikv.stores | .[] | select ( .podName == \"${pod_name}\" ) | .leaderCount"
    ```

    If the output is `0`, all Region Leaders are successfully migrated.

## Recreate a TiKV Pod

1. [Evict the TiKV Region Leader](#evict-tikv-region-leader) to another Pod.

2. Take the TiKV Pod offline.

    > **Note:**
    >
    > Before you take the TiKV Pod offline, make sure that the remaining TiKV Pods are not fewer than the TiKV replica number set in PD configuration (`max-replicas`, 3 by default). If the remaining TiKV Pods are not enough, scale out TiKV Pods before you take the TiKV Pod offline.

    1. Check `store-id` of the TiKV Pod:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get -n ${namespace} tc ${cluster_name} -ojson | jq ".status.tikv.stores | .[] | select ( .podName == \"${pod_name}\" ) | .id"
        ```

    2. In any of the PD Pods, use `pd-ctl` command to take the TiKV Pod offline:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl exec -n ${namespace} ${cluster_name}-pd-0 -- /pd-ctl store delete ${store_id}
        ```

    3. Wait for the store status (`state_name`) to become `Tombstone`:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl exec -n ${namespace} ${cluster_name}-pd-0 -- watch /pd-ctl store ${store_id}
        ```

        <details>
        <summary>Expected output</summary>

        ```json
        {
          "store": {
            "id": "${store_id}",
            // ...
            "state_name": "Tombstone"
          },
          // ...
        }
        ```

        </details>

3. Unbind the TiKV Pod with the currently used storage.

    1. Check the `PersistentVolumeClaim` used by the Pod:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl -n ${namespace} get pvc -l tidb.pingcap.com/pod-name=${pod_name}
        ```

        <details>
        <summary>Expected output</summary>

        The <code>NAME</code> field is the name of PVC.

        ```
        NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES       STORAGECLASS   AGE
        ${pvc_name}   Bound    pvc-a8f16ca6-a675-448f-82c3-3cae624aa0e2   100Gi      RWO                standard       18m
        ```

        </details>

    2. Delete the `PersistentVolumeClaim`:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl delete -n ${namespace} pvc ${pvc_name} --wait=false
        ```

4. Delete the old TiKV Pod and wait for the new TiKV Pod to join the cluster.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete -n ${namespace} pod ${pod_name}
    ```

    Wait for the state of the new TiKV Pod to become `Up`.

    ```shell
    kubectl get -n ${namespace} tc ${cluster_name} -ojson | jq ".status.tikv.stores | .[] | select ( .podName == \"${pod_name}\" )"
    ```

    <details>
    <summary>Expected output</summary>

    ```json
    {
      "id": "${new_store_id}",
      "ip": "${pod_name}.${cluster_name}-tikv-peer.default.svc",
      "lastTransitionTime": "2022-03-08T06:39:58Z",
      "leaderCount": 3,
      "podName": "${pod_name}",
      "state": "Up"
    }
    ```

    </details>

    As you can see from the output, the new TiKV Pod have a new `store-id`, and Region Leaders are migrated to this TiKV Pod automatically.

5. Remove the useless evict-leader-scheduler:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec -n ${namespace} ${cluster_name}-pd-0 -- /pd-ctl scheduler remove evict-leader-scheduler-${store_id}
    ```
