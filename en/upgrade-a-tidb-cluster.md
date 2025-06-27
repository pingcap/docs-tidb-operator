---
title: Upgrade a TiDB Cluster on Kubernetes
summary: Learn how to upgrade a TiDB cluster on Kubernetes.
---

# Upgrade a TiDB Cluster on Kubernetes

If you deploy and manage your TiDB clusters on Kubernetes using TiDB Operator, you can upgrade your TiDB clusters using the rolling update feature. Rolling update can limit the impact of upgrade on your application. This document describes how to upgrade a TiDB cluster on Kubernetes using rolling updates.

## Rolling update introduction

Kubernetes provides the [rolling update](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) feature to update your application with zero downtime.

When you perform a rolling update, TiDB Operator waits for the new version of a Pod to run successfully before proceeding to the next Pod.

During the rolling update, TiDB Operator automatically completes Leader transfer for PD and TiKV. Under the highly available deployment topology (minimum requirements: PD \* 3, TiKV \* 3, TiDB \* 2), performing a rolling update to PD and TiKV servers does not impact the running application. If your client supports retrying stale connections, performing a rolling update to TiDB servers does not impact application, either.

> **Warning:**
>
> - For the clients that cannot retry stale connections, **performing a rolling update to TiDB servers closes the client connections and causes the request to fail**. In such cases, it is recommended to add a retry function for the clients to retry, or to perform a rolling update to TiDB servers in idle time.
> - Before upgrading, refer to [`ADMIN SHOW DDL [JOBS|JOB QUERIES]`](https://docs.pingcap.com/tidb/stable/sql-statement-admin-show-ddl) to confirm that there are no DDL operations in progress.

## Preparations before upgrade

1. Refer to the [upgrade caveat](https://docs.pingcap.com/tidb/dev/upgrade-tidb-using-tiup#upgrade-caveat) to learn about the precautions. Note that all TiDB versions, including patch versions, currently do not support downgrade or rollback after upgrade.
2. Refer to [TiDB release notes](https://docs.pingcap.com/tidb/dev/release-notes) to learn about the compatibility changes in each intermediate version. If any changes affect your upgrade, take appropriate measures.

    For example, if you upgrade from TiDB v6.4.0 to v6.5.2, you need to check the compatibility changes in the following versions:

    - TiDB v6.5.0 [compatibility changes](https://docs.pingcap.com/tidb/stable/release-6.5.0#compatibility-changes) and [deprecated features](https://docs.pingcap.com/tidb/stable/release-6.5.0#deprecated-feature)
    - TiDB v6.5.1 [compatibility changes](https://docs.pingcap.com/tidb/stable/release-6.5.1#compatibility-changes)
    - TiDB v6.5.2 [compatibility changes](https://docs.pingcap.com/tidb/stable/release-6.5.2#compatibility-changes)

    If you upgrade from v6.3.0 or an earlier version to v6.5.2, you also need to check the compatibility changes in all intermediate versions.

## Upgrade steps

1. Update the version of each component group in the cluster by setting the target `version` in the version field. For example:

    ```yaml
    spec:
      template:
        spec:
          version: v8.1.0
    ```

    You can use the `kubectl apply` command to update all components at once, or use `kubectl edit` to update each component individually. TiDB Operator automatically handles the upgrade order and prevents the upgrade from continuing if the preconditions are not met.

    > **Note:**
    >
    > TiDB Operator requires all components in the cluster to use the same version. Make sure that the `spec.template.spec.version` field for all components is set to the same version.

2. Check the upgrade progress:

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    After all the Pods finish rebuilding and become `Running`, the upgrade is completed.
