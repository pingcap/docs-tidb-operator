---
title: Deploy the HTAP Storage Engine Tiflash for an Existing TiDB Cluster
summary:  Learn how to deploy TiFlash, the TiDB HTAP storage engine, on Kubernetes for an existing TiDB cluster.
aliases: ['/docs/tidb-in-kubernetes/dev/deploy-tiflash/']
---

# Deploy the HTAP Storage Engine Tiflash for an Existing TiDB Cluster 

This document describes how to add or remove the TiDB HTAP storage engine TiFlash for an existing TiDB cluster in Kubernetes. As a columnar storage extension of TiKV, TiFlash provides both good isolation level and strong consistency guarantee.

> **Note**:
>
> If a TiDB cluster has not been deployed yet, instead of referring to this document, you can [configure a TiDB cluster in Kubernetes](configure-a-tidb-cluster.md) with the TiFlash-related parameters, and then [deploy the TiDB cluster](deploy-on-general-kubernetes.md).

## Usage scenarios

This document is applicable to scenarios in which you already have a TiDB cluster and need to use TiDB HTAP capabilities by deploying TiFlash, such as the following:

- Hybrid workload scenarios with online real-time analytic processing
- Real-time stream processing scenarios
- Data hub scenarios

## Deploy TiFlash

If you need to deploy TiFlash for an existing TiDB cluster, do the following:

> **Note:**
>
> If your server does not have an external network, you can download the required Docker image on the machine with an external network, upload the Docker image to your server, and then use `docker load` to install the Docker image on the server. For details, see [deploy the TiDB cluster](deploy-on-general-kubernetes.md#deploy-the-tidb-cluster).

1. Edit the `TidbCluster` Custom Resource (CR):

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl eidt tc ${cluster_name} -n ${namespace}
    ```

2. Add the TiFlash configuration as the following example:

    {{< copyable "shell-regular" >}}

    ```yaml
    spec:
    tiflash:
        # To deploy the enterprise edition of TiFlash, change the value of `baseImage` to `pingcap/tiflash-enterprise`.
        baseImage: pingcap/tiflash
        maxFailoverCount: 0
        replicas: 1
        storageClaims:
        - resources:
            requests:
              storage: 100Gi
          storageClassName: local-storage
    ```

3. TiFlash supports mounting multiple Persistent Volumes (PVs). If you want to configure multiple PVs for TiFlash, configure multiple `resources` in `tiflash.storageClaims`, each `resources` with a separate `requests.storage` and `storageClassName`. For example:

    ```yaml
    tiflash:
        baseImage: pingcap/tiflash
        maxFailoverCount: 0
        replicas: 1
        storageClaims:
        - resources:
            requests:
                storage: 100Gi
          storageClassName: local-storage
        - resources:
            requests:
                storage: 100Gi
          storageClassName: local-storage
    ```

    > **Note**:
    >
    > - When deploying TiFlash for the first time, it is recommended that you plan how many PVs are required and configure the number of `resources` items in `storageClaims` accordingly.
    > - Once the deployment of TiFlash is completed, if you need to mount additional PVs for TiFlash, updating `storageClaims` directly to add disks does not take effect. This is because TiDB Operator manages TiFlash by creating a [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/), and the `StatefulSet` does not support modifying `volumeClaimTemplates` after being created.

4. Configure the relevant parameters of `spec.tiflash.config` in TidbCluster CR. For example:

    ```yaml
    spec:
      tiflash:
        config:
          config: |
            [flash]
              [flash.flash_cluster]
                log = "/data0/logs/flash_cluster_manager.log"
            [logger]
              count = 10
              level = "information"
              errorlog = "/data0/logs/error.log"
              log = "/data0/logs/server.log"
    ```

    For more TiFlash parameters that can be configured, refer to [TiFlash Configuration Documentation](https://docs.pingcap.com/tidb/stable/tiflash-configuration).

    > **Note:**
    >
    > For different TiFlash versions, note the following configuration differences:
    >
    > - If TiFlash version <= v4.0.4, you need to set `spec.tiflash.config.config.flash.service_addr` to `${clusterName}-tiflash-POD_NUM.${clusterName}-tiflash-peer.${namespace}.svc:3930` in TidbCluster CR, where `${clusterName}` and `${namespace}` need to be replaced according to the real case.
    > - If TiFlash version >= v4.0.5, there is no need to manually configure `spec.tiflash.config.config.flash.service_addr`.
    > - If you upgrade from TiFlash v4.0.4 or an earlier version to TiFlash v4.0.5 or a later version, you need to delete the configuration of `spec.tiflash.config.config.flash.service_addr` from the `TidbCluster` CR.

## Adding PVs to TiFlash

Once the deployment of TiFlash is completed, to add PVs for TiFlash, you need to update the `storageClaims` to add disks, and then manually delete the TiFlash StatefulSet. The following are the detailed steps.

> **Warnings**:
>
> Deleting the TiFlash StatefulSet makes the TiFlash cluster unavailable during the deletion and affects related business. You must be cautious about whether to do the following.

1. Edit the TidbCluster Custom Resource (CR).

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. TiDB Operator automatically mounts PVs in the **order** of the items in the `storageClaims` list. If you need to add more `resources` items to TiFlash, make sure to append new items only to the **end** of the original items, and **DO NOT** modify the order of the original items. For example:

    {{< copyable "shell-regular" >}}

    ```yaml
    tiflash:
        baseImage: pingcap/tiflash
        maxFailoverCount: 0
        replicas: 1
        storageClaims:
        - resources:
            requests:
                storage: 100Gi
          storageClassName: local-storage
        - resources:
            requests:
                storage: 100Gi
          storageClassName: local-storage
        - resources: #newly added
            requests:  #newly added
                storage: 100Gi  #newly added
          storageClassName: local-storage  #newly added
    ```

3. Manually delete the TiFlash StatefulSet by running the following command. Then, wait for the TiDB Operator to recreate the TiFlash StatefulSet.

    {{< copyable "shell-regular" >}}

    ``` shell
    kubectl delete sts -n ${namespace} ${cluster_name}-tiflash
    ```

## Remove TiFlash

If your TiDB cluster no longer needs the TiDB HTAP storage engine TiFlash, take the following steps to remove TiFlash:

1. Adjust the number of replicas of the tables replicated to the TiFlash cluster.

    To completely remove TiFlash, you need to set the number of replicas of all tables replicated to the TiFlash to `0`.

    1. To connect to the TiDB service, refer to the steps in [Access the TiDB Cluster in Kubernetes](access-tidb.md).

    2. To adjust the number of replicas of the tables replicated to the TiFlash cluster, run the following command:

       {{< copyable "sql" >}}

        ```sql
        alter table <db_name>.<table_name> set tiflash replica 0;
        ```

2. Wait for the TiFlash replicas of the related tables to be deleted.

    Connect to the TiDB service and run the following command. If you can not find the replication information of the related tables, it means that the replicas are deleted:

    {{< copyable "sql" >}}

    ```sql
    SELECT * FROM information_schema.tiflash_replica WHERE TABLE_SCHEMA = '<db_name>' and TABLE_NAME = '<table_name>';
    ```

3. To remove TiFlash Pods, run the following command to modify `spec.tiflash.replicas` to `0`:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tidbcluster ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"tiflash":{"replicas": 0}}}
    ```

4. Check the state of TiFlash Pods and TiFlash stores.

    1. Run the following command to check whether you delete the TiFlash Pod successfully:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pod -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

        If the output is empty, it means that you delete the Pod of the TiFlash cluster successfully.

   2. To check whether the stores of the TiFlash are in the `Tombstone` state, run the following command:

        ```shell
        kubectl get tidbcluster ${cluster_name} -n ${namespace} -o yaml
        ```

        The value of the `status.tiflash` field in the output result is similar to the example below.

        ```
        tiflash:
            ...
            tombstoneStores:
            "88":
                id: "88"
                ip: basic-tiflash-0.basic-tiflash-peer.default.svc
                lastHeartbeatTime: "2020-12-31T04:42:12Z"
                lastTransitionTime: null
                leaderCount: 0
                podName: basic-tiflash-0
                state: Tombstone
            "89":
                id: "89"
                ip: basic-tiflash-1.basic-tiflash-peer.default.svc
                lastHeartbeatTime: "2020-12-31T04:41:50Z"
                lastTransitionTime: null
                leaderCount: 0
                podName: basic-tiflash-1
                state: Tombstone
        ```

        Only after you delete all Pods of the TiFlash cluster successfully and all the TiFlash stores have changed to the `Tombstone` state, can you perform the next operation.

5. Delete the TiFlash StatefulSet.

   1. To modify the TidbCluster CR and delete the `spec.tiflash` field, run the following command:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl patch tidbcluster ${cluster_name} -n ${namespace} --type json -p '[{"op":"remove", "path":"/spec/tiflash"}]'
        ```

   2. To delete the TiFlash StatefulSet, run the following command:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl delete statefulsets -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

   3. To check whether you delete the StatefulSet of the TiFlash cluster successfully, run the following command:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get sts -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

        If the output is empty, it means that you delete the StatefulSet of the TiFlash cluster successfully.

6. (Optional) Delete PVC and PV.

   If you confirm that you do not use the data in TiFlash, and you want to delete the data, you need to strictly follow the steps below to delete the data in TiFlash:

   1. Delete the PVC object corresponding to the PV

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl delete pvc -n ${namespace} -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```

    2. If the PV reclaim policy is `Retain`, the corresponding PV is still retained after you delete the PVC object. If you want to delete the PV, you can set the reclaim policy of the PV to `Delete`, and the PV can be deleted and recycled automatically.

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl patch pv ${pv_name} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
        ```

        In the above command, `${pv_name}` represents the PV name of the TiFlash cluster. You can check the PV name by running the following command:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl get pv -l app.kubernetes.io/component=tiflash,app.kubernetes.io/instance=${cluster_name}
        ```