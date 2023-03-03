---
title: Use PD Recover to Recover the PD Cluster
summary: Learn how to use PD Recover to recover the PD cluster.
---

# Use PD Recover to Recover the PD Cluster

PD Recover is a disaster recovery tool of [PD](https://pingcap.com/docs/stable/architecture/#placement-driver-server), used to recover the PD cluster which cannot start or provide services normally. For detailed introduction of this tool, see [TiDB documentation - PD Recover](https://pingcap.com/docs/stable/reference/tools/pd-recover). This document introduces how to download PD Recover and how to use it to recover a PD cluster.

## Download PD Recover

1. Download the official TiDB package:

    {{< copyable "shell-regular" >}}

    ```shell
    wget https://download.pingcap.org/tidb-community-toolkit-${version}-linux-amd64.tar.gz
    ```

    In the command above, `${version}` is the version of the TiDB cluster, such as `v5.3.0`.

2. Unpack the TiDB package:

    {{< copyable "shell-regular" >}}

    ```shell
    tar -xzf tidb-community-toolkit-${version}-linux-amd64.tar.gz
    tar -xzf tidb-community-toolkit-${version}-linux-amd64/pd-recover-${version}-linux-amd64.tar.gz
    ```

    `pd-recover` is in the current directory.

## Recover the PD cluster

This section introduces how to recover the PD cluster using PD Recover.

### Step 1: Get Cluster ID

{{< copyable "shell-regular" >}}

```shell
kubectl get tc ${cluster_name} -n ${namespace} -o='go-template={{.status.clusterID}}{{"\n"}}'
```

Example:

```
kubectl get tc test -n test -o='go-template={{.status.clusterID}}{{"\n"}}'
6821434242797747735
```

### Step 2. Get Alloc ID

When you use `pd-recover` to recover the PD cluster, you need to specify `alloc-id`. The value of `alloc-id` must be larger than the largest allocated ID (`Alloc ID`) of the original cluster.

1. Access the Prometheus monitoring data of the TiDB cluster by taking steps in [Access the Prometheus monitoring data](monitor-a-tidb-cluster.md#access-the-prometheus-monitoring-data).

2. Enter `pd_cluster_id` in the input box and click the `Execute` button to make a query. Get the largest value in the query result.

3. Multiply the largest value in the query result by `100`. Use the multiplied value as the `alloc-id` value specified when using `pd-recover`.

### Step 3. Recover the PD Pod

> **Warning:**
>
> Restoring the cluster by creating a new PD will lose all the configuration information that the PD has taken effect before.

1. Delete the Pod of the PD cluster.

    Execute the following command to set the value of `spec.pd.replicas` to `0`:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": 0}}}'
    ```

    Because the PD cluster is in an abnormal state, TiDB Operator cannot synchronize the change above to the PD StatefulSet. You need to execute the following command to set the `spec.replicas` of the PD StatefulSet to `0`.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch sts ${cluster_name}-pd -n ${namespace} -p '{"spec":{"replicas": 0}}'
    ```

    Execute the following command to confirm that the PD Pod is deleted:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod -n ${namespace}
    ```

2. After confirming that all PD Pods are deleted, execute the following command to delete the PVCs bound to the PD Pods:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete pvc -l app.kubernetes.io/component=pd,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
    ```

3. After the PVCs are deleted, scale out the PD cluster to one Pod:

    Execute the following command to set the value of `spec.pd.replicas` to `1`:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": 1}}}'
    ```

    Because the PD cluster is in an abnormal state, TiDB Operator cannot synchronize the change above to the PD StatefulSet. You need to execute the following command to set the `spec.replicas` of the PD StatefulSet to `1`.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch sts ${cluster_name}-pd -n ${namespace} -p '{"spec":{"replicas": 1}}'
    ```

    Execute the following command to confirm that the PD cluster is started:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs -f ${cluster_name}-pd-0 -n ${namespace} | grep "Welcome to Placement Driver (PD)"
    ```

### Step 4. Recover the cluster

1. 4.1 Copy `pd-recover` command to the PD pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cp ./pd-recover ${namespace}/${cluster_name}-pd-0:./
    ```

2. Execute the `pd-recover` command to recover the PD cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -- ./pd-recover -endpoints http://127.0.0.1:2379 -cluster-id ${cluster_id} -alloc-id ${alloc_id}
    ```

    In the command above, `${cluster_id}` is the cluster ID got in [Get Cluster ID](#step-1-get-cluster-id). `${alloc_id}` is the largest value of `pd_cluster_id` (got in [Get Alloc ID](#step-2-get-alloc-id)) multiplied by `100`.

    After the `pd-recover` command is successfully executed, the following result is printed:

    ```shell
    recover success! please restart the PD cluster
    ```

### Step 5. Restart the PD Pod

1. Delete the PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete pod ${cluster_name}-pd-0 -n ${namespace}
    ```

2. Execute the following command to confirm the Cluster ID is the one got in [Get Cluster ID](#step-1-get-cluster-id).

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- wget -q http://127.0.0.1:2379/pd/api/v1/cluster
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- cat cluster
    ```

### Step 6. Scale out the PD cluster

Execute the following command to set the value of `spec.pd.replicas` to the desired number of Pods:

{{< copyable "shell-regular" >}}

```shell
kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": $replicas}}}'
```

### Step 7. Restart TiDB and TiKV

Use the following commands to restart the TiDB and TiKV clusters:

{{< copyable "shell-regular" >}}

```shell
kubectl delete pod -l app.kubernetes.io/component=tidb,app.kubernetes.io/instance=${cluster_name} -n ${namespace} &&
kubectl delete pod -l app.kubernetes.io/component=tikv,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
```
