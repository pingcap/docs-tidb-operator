---
title: Perform a Rolling Update to a TiDB Cluster in Kubernetes
summary: Learn how to perform a rolling update to a TiDB cluster in Kubernetes.
aliases: ['/docs/tidb-in-kubernetes/dev/upgrade-a-tidb-cluster/']
---

# Perform a Rolling Update to a TiDB Cluster in Kubernetes

When you perform a rolling update to a TiDB cluster in Kubernetes, the Pod is shut down and recreated with the new image or/and configuration serially in the order of PD, TiKV, TiDB. Under the highly available deployment topology (minimum requirements: PD \* 3, TiKV \* 3, TiDB \* 2), performing a rolling update to PD and TiKV servers does not impact the running clients.

+ For the clients that can retry stale connections, performing a rolling update to TiDB servers neither impacts the running clients.
+ For the clients that **can not** retry stale connections, performing a rolling update to TiDB servers will close the client connections and cause the request to fail. For this situation, it is recommended to add a function for the clients to retry, or to perform a rolling update to TiDB servers in idle time.

## Upgrade using TidbCluster CR

If the TiDB cluster is deployed directly using TidbCluster CR, or deployed using Helm but switched to management by TidbCluster CR, you can upgrade the TiDB cluster by the following steps.

### Upgrade the version of TiDB using TidbCluster CR

1. Modify the image configurations of all components in TidbCluster CR.

    Usually, components in a cluster are in the same version. You can upgrade the TiDB cluster simply by modifying `spec.version`. If you need to use different versions for different components, configure `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`.

    > **Note:**
    >
    > If you want to upgrade to Enterprise Edition, edit the `db.yaml` file to set `spec.<tidb/pd/tikv/tiflash/ticdc/pump>.baseImage` to the enterprise image (`pingcap/<tidb/pd/tikv/tiflash/ticdc/tidb-binlog>-enterprise`).
    >
    > For example, change `spec.pd.baseImage` from `pingcap/pd` to `pingcap/pd-enterprise`.

    The `version` field has following formats:

    - `spec.version`: the format is `imageTag`, such as `v4.0.7`

    - `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`: the format is `imageTag`, such as `v3.1.0`

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. Check the upgrade progress:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    After all the Pods finish rebuilding and become `Running`, the upgrade is completed.

### Force an upgrade of TiDB cluster using TidbCluster CR

If the PD cluster is unavailable due to factors such as PD configuration error, PD image tag error and NodeAffinity, then [scaling the TiDB cluster](scale-a-tidb-cluster.md), [upgrading the TiDB cluster](#upgrade-the-version-of-tidb-using-tidbcluster-cr) and changing the TiDB cluster configuration cannot be done successfully.

In this case, you can use `force-upgrade` to force an upgrade of the cluster to recover cluster functionality.

First, set `annotation` for the cluster:

{{< copyable "shell-regular" >}}

```shell
kubectl annotate --overwrite tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade=true
```

Change the related PD configuration to make sure that PD is in a normal state.

> **Note:**
>
> After the PD cluster recovers, you *must* execute the following command to disable the forced upgrade, or an exception may occur in the next upgrade:
>
> {{< copyable "shell-regular" >}}
>
> ```shell
> kubectl annotate tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade-
> ```

## Upgrade using Helm

If you continue to manage your cluster using Helm, refer to the following steps to upgrade the TiDB cluster.

### Upgrade the version of TiDB using Helm

1. Change the `image` of PD, TiKV and TiDB to different image versions in the `values.yaml` file.

    > **Note:**
    >
    > If you want to upgrade to Enterprise Edition, set the value of `<tidb/pd/tikv>.image` to the enterprise image.
    >
    > For example, change `pd.image` from `pingcap/pd:v4.0.7` to `pingcap/pd-enterprise:v4.0.7`.

2. Run the `helm upgrade` command:

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade ${release_name} pingcap/tidb-cluster -f values.yaml --version=${version}
    ```

3. Check the upgrade progress:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    After all the Pods finish rebuilding and become `Running`, the upgrade is completed.

### Force an upgrade of TiDB cluster using Helm

If the PD cluster is unavailable due to factors such as PD configuration error, PD image tag error and NodeAffinity, then [scaling the TiDB cluster](scale-a-tidb-cluster.md), [upgrading the TiDB cluster](#upgrade-the-version-of-tidb-using-helm) and changing the TiDB cluster configuration cannot be done successfully.

In this case, you can use `force-upgrade` (the version of TiDB Operator must be later than v1.0.0-beta.3) to force an upgrade of the cluster to recover cluster functionality.

First, set `annotation` for the cluster:

{{< copyable "shell-regular" >}}

```shell
kubectl annotate --overwrite tc ${release_name} -n ${namespace} tidb.pingcap.com/force-upgrade=true
```

Then execute the `helm upgrade` command to continue your interrupted operation:

{{< copyable "shell-regular" >}}

```shell
helm upgrade ${release_name} pingcap/tidb-cluster -f values.yaml --version=${chart_version}
```

> **Warning:**
>
> After the PD cluster recovers, you *must* execute the following command to disable the forced upgrade, or an exception may occur in the next upgrade:
>
> {{< copyable "shell-regular" >}}
>
> ```shell
> kubectl annotate tc ${release_name} -n ${namespace} tidb.pingcap.com/force-upgrade-
> ```
