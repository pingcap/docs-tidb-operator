---
title: Modify TiDB Cluster Configuration
summary: Learn how to modify the configuration of TiDB clusters deployed in Kubernetes.
---

# Modify TiDB Cluster Configuration

For a TiDB cluster, you can [update the configuration of components](https://docs.pingcap.com/tidb/stable/dynamic-config/) online using SQL statements, including TiDB, TiKV, and PD, without restarting the cluster components. However, for TiDB clusters deployed in Kubernetes, after you upgrade or restart the cluster, the configurations of some components might be overwritten by the `TidbCluster` CR. This leads to invalid online configuration update.

This document describes how to modify the configuration of TiDB clusters deployed in Kubernetes. Due to the special nature of PD, you need to separately modify the configuration of PD and other components.

## Modify configuration for TiDB, TiKV, and other components

For TiDB and TiKV, if you [dynamically modify their configuration](https://docs.pingcap.com/tidb/stable/dynamic-config/) using SQL statements, after you upgrade or restart the cluster, the configurations will be overwritten by those in the `TidbCluster` CR. This leads to the online configuration update being invalid. Therefore, to persist the configuration, you must directly modify their configurations in the `TidbCluster` CR.

For TiFlash, TiCDC, and Pump, you can only modify their configurations in the `TidbCluster` CR.

To modify the configuration in the `TidbCluster` CR, take the following steps:

1. Refer to the parameters in [Configure TiDB components](configure-a-tidb-cluster.md#configure-tidb-components) to modify the component configuration in the `TidbCluster` CR:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. After the configuration is modified, view the updating progress:

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl -n ${namespace} get pod -o wide
    ```

    After all the Pods are recreated and are in the `Running` state, the configuration is successfully modified.

## Modify PD configuration

After PD is started for the first time, some PD configuration items are persisted in etcd. The persisted configuration in etcd takes precedence over the configuration file in PD. Therefore, after the first start, you cannot modify some PD configuration by using the `TidbCluster` CR.

Among all the PD configuration items listed in [Modify PD configuration online](https://docs.pingcap.com/tidb/stable/dynamic-config/#modify-pd-configuration-online), after the first start, only `log.level` can be modified by using the `TidbCluster` CR. Other configurations cannot be modified by using CR.

For TiDB clusters deployed in Kubernetes, if you need to modify the PD configuration, you can dynamically modify the configuration using [SQL statements](https://docs.pingcap.com/tidb/stable/dynamic-config/#modify-pd-configuration-online), [pd-ctl](https://docs.pingcap.com/tidb/dev/pd-control/#config-show--set-option-value--placement-rules), or PD server API.
