---
title: Upgrade a TiDB Cluster in Kubernetes
summary: Learn how to upgrade a TiDB cluster in Kubernetes.
---

# Upgrade a TiDB Cluster in Kubernetes

If you deploy and manage your TiDB clusters in Kubernetes using TiDB Operator, you can upgrade your TiDB clusters using the rolling update feature. Rolling update can limit the impact of upgrade on your application.

This document describes how to upgrade a TiDB cluster in Kubernetes using rolling updates.

## Rolling update introduction

Kubernetes provides the [rolling update](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) feature to update your application with zero downtime.

When you perform a rolling update, TiDB Operator serially deletes an old Pod and creates the corresponding new Pod in the order of PD, TiKV, and TiDB. After the new Pod runs normally, TiDB Operator proceeds with the next Pod.

During the rolling update, TiDB Operator automatically completes Leader transfer for PD and TiKV. Under the highly available deployment topology (minimum requirements: PD \* 3, TiKV \* 3, TiDB \* 2), performing a rolling update to PD and TiKV servers does not impact the running application. If your client supports retrying stale connections, performing a rolling update to TiDB servers does not impact application, either.

> **Warning:**
>
> - For the clients that cannot retry stale connections, **performing a rolling update to TiDB servers closes the client connections and cause the request to fail**. In such cases, it is recommended to add a retry function for the clients to retry, or to perform a rolling update to TiDB servers in idle time.
> - Before upgrading, refer to the [documentation](https://docs.pingcap.com/tidb/stable/sql-statement-admin-show-ddl) to confirm that there are no DDL operations in progress.

## Upgrade steps

> **Note:**
>
> By default, TiDB (starting from v4.0.2) periodically shares usage details with PingCAP to help understand how to improve the product. For details about what is shared and how to disable the sharing, see [Telemetry](https://docs.pingcap.com/tidb/stable/telemetry).

1. In `TidbCluster` CR, modify the image configurations of all components of the cluster to be upgraded.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

    Usually, all components in a cluster are in the same version. You can upgrade the TiDB cluster simply by modifying `spec.version`. If you need to use different versions for different components, modify `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`.

    The `version` field has following formats:

    - `spec.version`: the format is `imageTag`, such as `v5.4.0`
    - `spec.<pd/tidb/tikv/pump/tiflash/ticdc>.version`: the format is `imageTag`, such as `v3.1.0`

2. Check the upgrade progress:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    After all the Pods finish rebuilding and become `Running`, the upgrade is completed.

## Troubleshoot the upgrade

If the PD cluster is unavailable due to PD configuration errors, PD image tag errors, NodeAffinity, or other causes, you might not be able to successfully upgrade the TiDB cluster. In such cases, you can force an upgrade of the cluster to recover the cluster functionality.

The steps of force upgrade are as follows:

1. Set `annotation` for the cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate --overwrite tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade=true
    ```

2. Change the related PD configuration to make sure that PD turns into a normal state.

3. After the PD cluster recovers, you *must* execute the following command to disable the forced upgrade; otherwise, an exception may occur in the next upgrade:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate tc ${cluster_name} -n ${namespace} tidb.pingcap.com/force-upgrade-
    ```

After taking the steps above, your TiDB cluster recovers its functionality. You can upgrade the cluster normally.
