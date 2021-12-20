---
title: TiDB Cluster Configurations in Kubernetes
summary: Learn the configurations of a TiDB cluster in Kubernetes.
aliases: ['/docs/tidb-in-kubernetes/v1.0/configure-a-tidb-cluster/','/docs/dev/tidb-in-kubernetes/reference/configuration/tidb-cluster/','/docs/v3.1/tidb-in-kubernetes/reference/configuration/tidb-cluster/','/docs/v3.0/tidb-in-kubernetes/reference/configuration/tidb-cluster/']
---

# TiDB Cluster Configurations in Kubernetes

This document introduces the following items of a TiDB cluster in Kubernetes:

+ The configuration parameters
+ The configuration of resources
+ The configuration of disaster recovery

## Configuration parameters

TiDB Operator uses `Helm` to deploy and manage TiDB clusters. The configuration file obtained through Helm provides the basic configuration by default with which you could quickly start a TiDB cluster. However, if you want special configurations or are deploying in a production environment, you need to manually configure the corresponding parameters according to the table below.

> **Note:**
>
> In the following table, `values.yaml` refers to the TiDB cluster's configuration file to be modified.

| Parameter | Description | Default Value |
| :----- | :---- | :----- |
| `rbac.create` | Whether to enable the RBAC mode of Kubernetes | `true` |
| `clusterName` |The TiDB cluster name. This variable is unset by default. In this case, `tidb-cluster` directly replaces it with `ReleaseName` when the cluster is being installed. | `nil` |
| `extraLabels` | Adds extra labels to the `TidbCluster` object (CRD). See [labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) | `{}` |
| `schedulerName` | The scheduler used by the TiDB cluster | `tidb-scheduler` |
| `timezone` | The default timezone used by the TiDB cluster | `UTC` |
| `pvReclaimPolicy` | The reclaim policy for PV (Persistent Volume) used by the TiDB cluster | `Retain` |
| `services[0].name` | The name of the service that the TiDB cluster exposes | `nil` |
| `services[0].type` | The type of the service that the TiDB cluster exposes (selected from `ClusterIP`, `NodePort` and `LoadBalancer`) | `nil` |
| `discovery.image` | The image of PD's service discovery component in the TiDB cluster. This component is used to provide service discovery for each PD instance to coordinate the starting sequence when the PD cluster is started for the first time. | `pingcap/tidb-operator:v1.0.0` |
| `discovery.imagePullPolicy` | The pulling policy for the image of PD's service discovery component | `IfNotPresent` |
| `discovery.resources.limits.cpu` | The CPU resource limit of PD's service discovery component | `250m` |
| `discovery.resources.limits.memory` | The memory resource limit of PD's service discovery component | `150Mi` |
| `discovery.resources.requests.cpu` | The CPU resource request of PD's service discovery component | `80m` |
| `discovery.resources.requests.memory` | The memory resource request of PD's service discovery component | `50Mi` |
| `enableConfigMapRollout` | Whether to enable the automatic rolling update of the TiDB cluster. If enabled, the TiDB cluster automatically updates the corresponding components when the `ConfigMap` of this cluster changes. This configuration is only supported in `tidb-operator` v1.0 and later versions. | `false` |
| `pd.config` | The configuration of PD. Check [the `config.toml` file](https://github.com/pingcap/pd/blob/master/conf/config.toml) for the default PD configuration file (by choosing the tag of the corresponding PD version). You can see [PD Configuration Flags](https://pingcap.com/docs/v3.0/reference/configuration/pd-server/configuration) for the detailed description of the configuration parameters (by choosing the corresponding document version). Here you must **modify the configuration based on the format of the configuration file**. | If the version of TiDB Operator is v1.0.0 or earlier, the default value is <br/>`nil`<br/>If the version of TiDB Operator is later than v1.0.0, the default value is <br/>`[log]`<br/>`level = "info"`<br/>`[replication]`<br/>`location-labels = ["region", "zone", "rack", "host"]`.<br/>Sample configuration:<br/>&nbsp;&nbsp;`config:` \|<br/>&nbsp;&nbsp;&nbsp;&nbsp;`[log]`<br/>&nbsp;&nbsp;&nbsp;&nbsp;`level = "info"`<br/>&nbsp;&nbsp;&nbsp;&nbsp;`[replication]`<br/>&nbsp;&nbsp;&nbsp;&nbsp;`location-labels = ["region", "zone", "rack", "host"]` |
| `pd.replicas` | The number of Pods in PD | `3` |
| `pd.image` | The PD image | `pingcap/pd:v3.0.0-rc.1` |
| `pd.imagePullPolicy` | The pulling policy for the PD image | `IfNotPresent` |
| `pd.logLevel` | The log level of PD<br/>If the version of TiDB Operator is later than v1.0.0, configure the parameter via `pd.config`: <br/>`[log]`<br/>`level = "info"` | `info` |
| `pd.storageClassName` | The `storageClass` used by PD. `storageClassName` refers to a type of storage provided by the Kubernetes cluster, which might map to a level of service quality, a backup policy, or to any policy determined by the cluster administrator. Detailed reference: [storage-classes](https://kubernetes.io/docs/concepts/storage/storage-classes) | `local-storage` |
| `pd.maxStoreDownTime` | This parameter indicates how soon a store node is marked as `down` after it is disconnected. When the state changes to `down`, the store node starts migrating data to other store nodes.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `pd.config`:<br/>`[schedule]`<br/>`max-store-down-time = "30m"`  | `30m` |
| `pd.maxReplicas` | The number of data replicas in the TiDB cluster<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `pd.config`:<br/>`[replication]`<br/>`max-replicas = 3` | `3` |
| `pd.resources.limits.cpu` | The CPU resource limit per PD Pod | `nil` |
| `pd.resources.limits.memory` | The memory resource limit per PD Pod | `nil` |
| `pd.resources.limits.storage` | The storage limit per PD Pod | `nil` |
| `pd.resources.requests.cpu` | The CPU resource requests of each PD Pod | `nil` |
| `pd.resources.requests.memory` | The memory resource requests of each PD Pod | `nil` |
| `pd.resources.requests.storage` | The storage requests of each PD Pod | `1Gi` |
| `pd.affinity` | Defines PD's scheduling rules and preferences. Detailed reference: [affinity-and-anti-affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) | `{}` |
| `pd.nodeSelector` | Ensures that PD Pods are only scheduled to the node with the specific key-value pair as the label. Detailed reference: [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) | `{}` |
| `pd.tolerations` | Applies to PD Pods, allowing the Pods to be scheduled to the nodes with specified taints. Detailed reference: [taint-and-toleration](https://kubernetes.io/docs/concepts/configuration/taint-and-toleration) | `{}` |
| `pd.annotations` | Adds a specific `annotations` for PD Pods. | `{}` |
| `tikv.config` | The configuration of TiKV. Check [the `config-template.toml` file](https://github.com/tikv/tikv/blob/master/etc/config-template.toml) for the default TiKV configuration file (by choosing the tag of the corresponding TiKV version). You can see [TiKV Configuration Flags](https://pingcap.com/docs/v3.0/reference/configuration/tikv-server/configuration) for the detailed description of the configuration parameters (by choosing the corresponding document version). Here you must **modify the configuration based on the format of the configuration file**.<br/><br/>You need to explicitly configure the following two configuration items:<br/><br/>`[storage.block-cache]`<br/>&nbsp;&nbsp;`shared = true`<br/>&nbsp;&nbsp;`capacity = "1GB"`<br/>It is recommended to set `capacity` to 50% of the value of `tikv.resources.limits.memory`.<br/><br/>`[readpool.coprocessor]`<br/>&nbsp;&nbsp;`high-concurrency = 8`<br/>&nbsp;&nbsp;`normal-concurrency = 8`<br/>&nbsp;&nbsp;`low-concurrency = 8`<br/>It is recommended to set to 80% of the value of `tikv.resources.limits.cpu`. | If the version of TiDB Operator is v1.0.0-beta.3 or earlier, the default value is<br/>`nil`<br/>If the version of TiDB Operator is later than v1.0.0-beta.3, the default value is<br/>`log-level = "info"`<br/>Sample configuration:<br/>&nbsp;&nbsp;`config:` \|<br/>&nbsp;&nbsp;&nbsp;&nbsp;`log-level = "info"` |
| `tikv.replicas` | The number of Pods in TiKV | `3` |
| `tikv.image` | The TiKV image | `pingcap/tikv:v3.0.0-rc.1` |
| `tikv.imagePullPolicy` | The pulling policy for the TiKV image | `IfNotPresent` |
| `tikv.logLevel` | The level of TiKV logs<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`log-level = "info"` | `info` |
| `tikv.storageClassName` | The `storageClass` used by TiKV. `storageClassName` refers to a type of storage provided by the Kubernetes cluster, which might map to a level of service quality, a backup policy, or to any policy determined by the cluster administrator. Detailed reference: [storage-classes](https://kubernetes.io/docs/concepts/storage/storage-classes) | `local-storage` |
| `tikv.syncLog` | `SyncLog` means whether to enable the raft log replication. Enabling this feature ensures that data will not be lost when power is off.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`[raftstore]`<br/>`sync-log = true`  | `true` |
| `tikv.grpcConcurrency` | Configures the thread pool size of the gRPC server.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`[server]`<br/>`grpc-concurrency = 4` | `4` |
| `tikv.resources.limits.cpu` | The CPU resource limit per TiKV Pod | `nil` |
| `tikv.resources.limits.memory` | The memory resource limit per TiKV Pod | `nil` |
| `tikv.resources.limits.storage` | The storage limit per TiKV Pod | `nil` |
| `tikv.resources.requests.cpu` | The CPU resource requests of each TiKV Pod | `nil` |
| `tikv.resources.requests.memory` | The memory resource requests of each TiKV Pod | `nil` |
| `tikv.resources.requests.storage` | The storage requests of each TiKV Pod | `10Gi` |
| `tikv.affinity` | Defines TiKV's scheduling rules and preferences. Detailed reference:[affinity-and-anti-affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) | `{}` |
| `tikv.nodeSelector` | Ensures that TiKV Pods are only scheduled to the node with the specific key-value pair as the label. Detailed reference: [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) | `{}` |
| `tikv.tolerations` | Applies to TiKV Pods, allowing TiKV Pods to be scheduled to the nodes with specified taints. Detailed reference: [taint-and-toleration](https://kubernetes.io/docs/concepts/configuration/taint-and-toleration) | `{}` |
| `tikv.annotations` | Adds a specific `annotations` for TiKV Pods. | `{}` |
| `tikv.defaultcfBlockCacheSize` | Specifies the size of block cache which is used to cache uncompressed blocks. Larger block cache settings speed up reads. It is recommended to set the parameter to 30%-50% of the value of `tikv.resources.limits.memory`.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`[rocksdb.defaultcf]`<br/>`block-cache-size = "1GB"`<br/>From TiKV v3.0.0 on, you do not need to configure `[rocksdb.defaultcf].block-cache-size` and `[rocksdb.writecf].block-cache-size`. Instead, configure `[storage.block-cache].capacity`. | `1GB` |
| `tikv.writecfBlockCacheSize` | Specifies the size of writecf block cache. It is recommended to set the parameter to 10%-30% of the value of `tikv.resources.limits.memory`.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`[rocksdb.writecf]`<br/>`block-cache-size = "256MB"`<br/>From TiKV v3.0.0 on, you do not need to configure `[rocksdb.defaultcf].block-cache-size` and `[rocksdb.writecf].block-cache-size`. Instead, configure `[storage.block-cache].capacity`. | `256MB` |
| `tikv.readpoolStorageConcurrency` | The size of thread pool for high priority, normal priority or low priority operations in the TiKV storage<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`[readpool.storage]`<br/>`high-concurrency = 4`<br/>`normal-concurrency = 4`<br/>`low-concurrency = 4` | `4` |
| `tikv.readpoolCoprocessorConcurrency` | If `tikv.resources.limits.cpu` is greater than `8`, set the value of `tikv.readpoolCoprocessorConcurrency` to `tikv.resources.limits.cpu` * 0.8<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`[readpool.coprocessor]`<br/>`high-concurrency = 8`<br/>`normal-concurrency = 8`<br/>`low-concurrency = 8` | `8` |
| `tikv.storageSchedulerWorkerPoolSize` | The worker pool size of the TiKV scheduler. This size must be increased in the case of rewriting but be smaller than the total CPU cores.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tikv.config`:<br/>`[storage]`<br/>`scheduler-worker-pool-size = 4` | `4` |
| `tidb.config` | The configuration of TiDB. Check [the `config.toml.example` file](https://github.com/pingcap/tidb/blob/master/config/config.toml.example) for the default TiDB configuration file (by choosing the tag of the corresponding TiDB version). You can see [TiDB Configuration File Description](https://pingcap.com/docs/v3.0/reference/configuration/tidb-server/configuration-file/) for the detailed description of the configuration parameters (by choosing the corresponding document version). Here you must **modify the configuration based on the format of the configuration file**.<br/><br/>You need to explicitly configure the following configuration items:<br/><br/>`[performance]`<br/>&nbsp;&nbsp;`max-procs = 0`<br/>It is recommended to set `max-procs` to the value of corresponding cores of `tidb.resources.limits.cpu` | If the version of TiDB Operator is v1.0.0-beta.3 or earlier, the default value is<br/>`nil`<br/>If the version of TiDB Operator is later than v1.0.0-beta.3, the default value is<br/>`[log]`<br/>`level = "info"`<br/>Sample configuration:<br/>&nbsp;&nbsp;`config:` \|<br/>&nbsp;&nbsp;&nbsp;&nbsp;`[log]`<br/>&nbsp;&nbsp;&nbsp;&nbsp;`level = "info"` |
| `tidb.replicas` | The number of Pods in TiDB | `2` |
| `tidb.image` | The TiDB image | `pingcap/tidb:v3.0.0-rc.1` |
| `tidb.imagePullPolicy` | The pulling policy for the TiDB image | `IfNotPresent` |
| `tidb.logLevel` | The level of TiDB logs<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`[log]`<br/>`level = "info"`  | `info` |
| `tidb.resources.limits.cpu` | The CPU resource limit per TiDB Pod | `nil` |
| `tidb.resources.limits.memory` | The memory resource limit per TiDB Pod | `nil` |
| `tidb.resources.requests.cpu` | The CPU resource requests of each TiDB Pod | `nil` |
| `tidb.resources.requests.memory` | The memory resource requests of each TiDB Pod | `nil` |
| `tidb.passwordSecretName`| The name of the `Secret` that stores the TiDB username and password. The `Secret` can create a secret with this command: `kubectl create secret generic tidb secret--from literal=root=<root password>--namespace=<namespace>`. If the parameter is unset, TiDB root password is empty. | `nil` |
| `tidb.initSql`| The initialization script that will be executed after a TiDB cluster is successfully started. | `nil` |
| `tidb.affinity` | Defines TiDB's scheduling rules and preferences. Detailed reference: [affinity-and-anti-affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) | `{}` |
| `tidb.nodeSelector` | Ensures that TiDB Pods are only scheduled to the node with the specific key-value pair as the label. Detailed reference: [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) | `{}` |
| `tidb.tolerations` | Applies to TiDB Pods, allowing TiDB Pods to be scheduled to nodes with specified taints. Detailed reference: [taint-and-toleration](https://kubernetes.io/docs/concepts/configuration/taint-and-toleration) | `{}` |
| `tidb.annotations` | Adds a specific `annotations` for TiDB Pods. | `{}` |
| `tidb.maxFailoverCount` | The maximum number of failovers for TiDB. Assuming the number is `3`, that is, up to 3 failovers TiDB instances are supported at the same time. | `3` |
| `tidb.service.type` | The type of service that the TiDB cluster exposes | `Nodeport` |
| `tidb.service.externalTrafficPolicy` | Whether this Service routes external traffic to a node-local or cluster-wide endpoint. There are two options available: `Cluster`(by default) and `Local`. `Cluster` obscures the client source IP and some traffic needs to hop twice among nodes for the intended node, but with a good overall load distribution. `Local` preserves the client source IP and avoids a second hop for the LoadBalancer and `Nodeport` type services, but risks potentially imbalanced traffic distribution. Detailed reference: [External LoadBalancer](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/#preserving-the-client-source-ip) | `nil` |
| `tidb.service.loadBalancerIP` | Specifies the IP of LoadBalancer. Some cloud providers allow you to specify `loadBalancerIP`. In these cases, the LoadBalancer will be created using the user-specified `loadBalancerIP`. If the `loadBalancerIP` field is not specified, the LoadBalancer will be set using the temporary IP address. If `loadBalancerIP` is specified but the cloud provider does not support this feature, the `loadbalancerIP` field you set will be ignored.| `nil` |
| `tidb.service.mysqlNodePort` | The MySQL `NodePort` that TiDB Service exposes |  |
| `tidb.service.exposeStatus` | The port that indicates the expose status of TiDB Service | `true` |
| `tidb.service.statusNodePort` | The `NodePort` exposed through specifying the status of TiDB Service |  |
| `tidb.separateSlowLog` | Whether to run in the sidecar mode the `SlowLog` of TiDB exported by the independent container | If the version of TiDB Operator is v1.0.0 or earlier, the default value is `false`.<br/>If the version of TiDB Operator is later than v1.0.0, the default value is `true`.  |
| `tidb.slowLogTailer.image` | The image of TiDB's `slowLogTailer`. `slowLogTailer` is a container of the sidecar type, used to export the `SlowLog` of TiDB. This configuration only takes effect when `tidb.separateSlowLog`=`true`. | `busybox:1.26.2` |
| `tidb.slowLogTailer.resources.limits.cpu` | The CPU resource limit per TiDB Pod's `slowLogTailer` | `100m` |
| `tidb.slowLogTailer.resources.limits.memory` | The memory resource limit per TiDB Pod's `slowLogTailer` | `50Mi` |
| `tidb.slowLogTailer.resources.requests.cpu` | The requests of each TiDB Pod's `slowLogTailer` for CPU resources | `20m` |
| `tidb.slowLogTailer.resources.requests.memory` | The requests of each TiDB Pod's `slowLogTailer` for memory resources | `5Mi` |
| `tidb.plugin.enable` | Whether to enable the TiDB plugin | `false` |
| `tidb.plugin.directory` | Specifies the directory where the TiDB plugin is located. | `/plugins` |
| `tidb.plugin.list` | Specifies a list of plugins loaded on TiDB. The naming rules of Plugin ID: `plugin name-version`. For example: `'conn_limit-1'`. | `[]` |
| `tidb.preparedPlanCacheEnabled` | Whether to enable TiDB's prepared plan cache<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`[prepared-plan-cache]`<br/>`enabled = false` | `false` |
| `tidb.preparedPlanCacheCapacity` | The cache capacity of TiDB's prepared plan<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`[prepared-plan-cache]`<br/>`capacity = 100`  | `100` |
| `tidb.txnLocalLatchesEnabled` | Whether to enable the memory lock for transactions. It is recommended to enable the lock when there are many local transaction conflicts.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`[txn-local-latches]`<br/>`enabled = false` | `false` |
| `tidb.txnLocalLatchesCapacity` |  The capacity of the transaction memory lock. The number of slots corresponding to Hash is automatically adjusted upward to an exponential multiple of `2`. Each slot occupies 32 Bytes of memory. When the range of writing data is relatively wide (such as importing data), setting this parameter too small a value results in lower performance.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`[txn-local-latches]`<br/>`capacity = 10240000` | `10240000` |
| `tidb.tokenLimit` | The restrictions on TiDB to execute concurrent sessions<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`token-limit = 1000` | `1000` |
| `tidb.memQuotaQuery` | The memory quota for TiDB queries, which is 32GB by default.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`mem-quota-query = 34359738368` | `34359738368` |
| `tidb.checkMb4ValueInUtf8` | Controls whether to check the `mb4` characters when the character set is `utf8`.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`check-mb4-value-in-utf8 = true` | `true` |
| `tidb.treatOldVersionUtf8AsUtf8mb4` | This parameter is used for upgrading compatibility. When it is set to `true`, `utf8` character set in the old table/column is treated as `utf8mb4`.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`treat-old-version-utf8-as-utf8mb4 = true` | `true` |
| `tidb.lease` | The lease time of TiDB Schema lease. It is highly risky to change this parameter. Therefore, it is not recommended to do so unless you know exactly what might be happening.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`lease = "45s"`  | `45s` |
| `tidb.maxProcs` | The maximum available CPU cores. `0` represents the number of CPU on the machine or Pod.<br/>If the version of TiDB Operator is later than v1.0.0, configure this parameter via `tidb.config`:<br/>`[performance]`<br/>`max-procs = 0` | `0` |

## Resource configuration

Before deploying a TiDB cluster, it is necessary to configure the resources for each component of the cluster depending on your needs. PD, TiKV and TiDB are the core service components of a TiDB cluster. In a production environment, their resource configurations must be specified according to component needs. Detailed reference: [Hardware Recommendations](https://pingcap.com/docs/v3.0/how-to/deploy/hardware-recommendations/).

To ensure the proper scheduling and stable operation of the components of the TiDB cluster in Kubernetes, it is recommended to set Guaranteed-level QoS by letting `limits` equal to `requests` when configuring resources. Detailed reference: [Configure Quality of Service for Pods](https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/).

If you are using a NUMA-based CPU, you need to enable `Static`'s CPU management policy on the node for better performance. In order to allow the TiDB cluster component to monopolize the corresponding CPU resources, the CPU quota must be an integer greater than or equal to `1` besides setting Guaranteed-level QoS as mentioned above. Detailed reference: [Control CPU Management Policies on the Node](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies).

## Disaster recovery configuration

TiDB is a distributed database and its disaster recovery must ensure that when any physical topology node fails, not only the service is unaffected, but also the data is complete and available. The two configurations of disaster recovery are described separately as follows.

### Disaster recovery of TiDB service

The disaster recovery of TiDB service is essentially based on Kubernetes' scheduling capabilities. To optimize scheduling, TiDB Operator provides a custom scheduler that guarantees the disaster recovery of TiDB service at the host level through the specified scheduling algorithm. Currently, the TiDB cluster uses this scheduler as the default scheduler, which is configured through the item `schedulerName` in the above table.

Disaster recovery at other levels (such as rack, zone, region) are guaranteed by Affinity's `PodAntiAffinity`. `PodAntiAffinity` can avoid the situation where different instances of the same component are deployed on the same physical topology node. In this way, disaster recovery is achieved. Detailed user guide for Affinity: [Affinity & AntiAffinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity).

The following is an example of a typical disaster recovery setup:

{{< copyable "" >}}

<<<<<<< HEAD
```shell
=======
```yaml
  pd:
    baseImage: pingcap/pd
    replicas: 1
    # if storageClassName is not set, the default Storage Class of the Kubernetes cluster will be used
    # storageClassName: local-storage
    requests:
      storage: "1Gi"
    config:
      log:
        file:
          filename: /var/log/pdlog/pd.log
        level: "warn"
    storageVolumes:
    - name: log
      storageSize: "2Gi"
      mountPath: "/var/log/pdlog"
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config:
      log:
        file:
          filename: /var/log/tidblog/tidb.log
        level: "warn"
    storageVolumes:
    - name: log
      storageSize: "2Gi"
      mountPath: "/var/log/tidblog"
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    # if storageClassName is not set, the default Storage Class of the Kubernetes cluster will be used
    # storageClassName: local-storage
    requests:
      storage: "1Gi"
    config:
      storage:
        # In basic examples, you can set this to avoid using too much storage.
        reserve-space: "0MB"
      rocksdb:
        wal-dir: "/data_sbi/tikv/wal"
      titan:
        dirname: "/data_sbj/titan/data"
    storageVolumes:
    - name: wal
      storageSize: "2Gi"
      mountPath: "/data_sbi/tikv/wal"
    - name: titan
      storageSize: "2Gi"
      mountPath: "/data_sbj/titan/data"
```

> **Note:**
>
> TiDB Operator uses some mount paths by default. For example, it mounts `EmptyDir` to the `/var/log/tidb` directory for the TiDB Pod. Therefore, avoid duplicate `mountPath` when you configure `storageVolumes`.

### HostNetwork

For PD, TiKV, TiDB, TiFlash, TiCDC, and Pump, you can configure the Pods to use the host namespace [`HostNetwork`](https://kubernetes.io/docs/concepts/policy/pod-security-policy/#host-namespaces).

To enable `HostNetwork` for all supported components, configure `spec.hostNetwork: true`.

To enable `HostNetwork` for specified components, configure `hostNetwork: true` for the components.

### Discovery

TiDB Operator starts a Discovery service for each TiDB cluster. The Discovery service can return the corresponding startup parameters for each PD Pod to support the startup of the PD cluster. You can configure resources of the Discovery service using `spec.discovery`. For details, see [Managing Resources for Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/).

A `spec.discovery` configuration example is as follows:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  version: v5.2.1
  pvReclaimPolicy: Retain
  discovery:
    limits:
      cpu: "0.2"
    requests:
      cpu: "0.2"
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: {}
...
```

### Cluster topology

#### PD/TiKV/TiDB

The deployed cluster topology by default has three PD Pods, three TiKV Pods, and two TiDB Pods. In this deployment topology, the scheduler extender of TiDB Operator requires at least three nodes in the Kubernetes cluster to provide high availability. You can modify the `replicas` configuration to change the number of pods for each component.

> **Note:**
>
> If the number of Kubernetes cluster nodes is less than three, one PD Pod goes to the Pending state, and neither TiKV Pods nor TiDB Pods are created. When the number of nodes in the Kubernetes cluster is less than three, to start the TiDB cluster, you can reduce the number of PD Pods in the default deployment to `1`.

#### Enable TiFlash

If you want to enable TiFlash in the cluster, configure `spec.pd.config.replication.enable-placement-rules: true` and configure `spec.tiflash` in the `${cluster_name}/tidb-cluster.yaml` file as follows:

```yaml
  pd:
    config: |
      ...
      [replication]
      enable-placement-rules = true
  tiflash:
    baseImage: pingcap/tiflash
    maxFailoverCount: 3
    replicas: 1
    storageClaims:
    - resources:
        requests:
          storage: 100Gi
      storageClassName: local-storage
```

TiFlash supports mounting multiple Persistent Volumes (PVs). If you want to configure multiple PVs for TiFlash, configure multiple `resources` in `tiflash.storageClaims`, each `resources` with a separate `storage request` and `storageClassName`. For example:

```yaml
  tiflash:
    baseImage: pingcap/tiflash
    maxFailoverCount: 3
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

TiFlash mounts all PVs to directories such as `/data0` and `/data1` in the container in the order of configuration. TiFlash has four log files. The proxy log is printed in the standard output of the container. The other three logs are stored in the disk under the `/data0` directory by default, which are `/data0/logs/flash_cluster_manager.log`, `/ data0/logs/error.log`, `/data0/logs/server.log`. To modify the log storage path, refer to [Configure TiFlash parameters](#configure-tiflash-parameters).

> **Warning:**
>
> Since TiDB Operator will mount PVs automatically in the **order** of the items in the `storageClaims` list, if you need to add more disks to TiFlash, make sure to append the new item only to the **end** of the original items, and **DO NOT** modify the order of the original items.

#### Enable TiCDC

If you want to enable TiCDC in the cluster, you can add TiCDC spec to the `TiDBCluster` CR. For example:

```yaml
  spec:
    ticdc:
      baseImage: pingcap/ticdc
      replicas: 3
```

#### Deploy Enterprise Edition

To deploy Enterprise Edition of TiDB/PD/TiKV/TiFlash/TiCDC, edit the `db.yaml` file to set `spec.<tidb/pd/tikv/tiflash/ticdc>.baseImage` to the enterprise image (`pingcap/<tidb/pd/tikv/tiflash/ticdc>-enterprise`).

For example:

```yaml
spec:
  ...
  pd:
    baseImage: pingcap/pd-enterprise
  ...
  tikv:
    baseImage: pingcap/tikv-enterprise
```

### Configure TiDB components

This section introduces how to configure the parameters of TiDB/TiKV/PD/TiFlash/TiCDC.

#### Configure TiDB parameters

TiDB parameters can be configured by `spec.tidb.config` in TidbCluster Custom Resource.

For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
....
  tidb:
    image: pingcap/tidb:v5.2.1
    imagePullPolicy: IfNotPresent
    replicas: 1
    service:
      type: ClusterIP
    config: |
      split-table = true
      oom-action = "log"
    requests:
      cpu: 1
```

For all the configurable parameters of TiDB, refer to [TiDB Configuration File](https://pingcap.com/docs/stable/reference/configuration/tidb-server/configuration-file/).

> **Note:**
>
> If you deploy your TiDB cluster using CR, make sure that `Config: {}` is set, no matter you want to modify `config` or not. Otherwise, TiDB components might not be started successfully. This step is meant to be compatible with `Helm` deployment.

#### Configure TiKV parameters

TiKV parameters can be configured by `spec.tikv.config` in TidbCluster Custom Resource.

For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
....
  tikv:
    image: pingcap/tikv:v5.0.1
    config: |
      [storage]
        [storage.block-cache]
          capacity = "16GB"
    replicas: 1
    requests:
      cpu: 2
```

For all the configurable parameters of TiKV, refer to [TiKV Configuration File](https://pingcap.com/docs/stable/reference/configuration/tikv-server/configuration-file/).

> **Note:**
>
> If you deploy your TiDB cluster using CR, make sure that `Config: {}` is set, no matter you want to modify `config` or not. Otherwise, TiKV components might not be started successfully. This step is meant to be compatible with `Helm` deployment.

#### Configure PD parameters

PD parameters can be configured by `spec.pd.config` in TidbCluster Custom Resource.

For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
.....
  pd:
    image: pingcap/pd:v5.0.1
    config: |
      lease = 3
      enable-prevote = true
```

For all the configurable parameters of PD, refer to [PD Configuration File](https://pingcap.com/docs/stable/reference/configuration/pd-server/configuration-file/).

> **Note:**
>
> - If you deploy your TiDB cluster using CR, make sure that `Config: {}` is set, no matter you want to modify `config` or not. Otherwise, PD components might not be started successfully. This step is meant to be compatible with `Helm` deployment.
> - After the cluster is started for the first time, some PD configuration items are persisted in etcd. The persisted configuration in etcd takes precedence over that in PD. Therefore, after the first start, you cannot modify some PD configuration using parameters. You need to dynamically modify the configuration using SQL statements, pd-ctl, or PD server API. Currently, among all the configuration items listed in [Modify PD configuration online](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-pd-configuration-online), except `log.level`, all the other configuration items cannot be modified using parameters after the first start.

#### Configure TiFlash parameters

TiFlash parameters can be configured by `spec.tiflash.config` in TidbCluster Custom Resource.

For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  ...
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

For all the configurable parameters of TiFlash, refer to [TiFlash Configuration File](https://pingcap.com/docs/stable/tiflash/tiflash-configuration/).

#### Configure TiCDC start parameters

You can configure TiCDC start parameters through `spec.ticdc.config` in TidbCluster Custom Resource.

For example:

For TiDB Operator v1.2.0-rc.2 and later versions, configure the parameters in the TOML format as follows:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  ...
  ticdc:
    config: |
      gc-ttl = 86400
      log-level = "info"
```

For TiDB Operator versions earlier than v1.2.0-rc.2, configure the parameters in the YAML format as follows:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  ...
  ticdc:
    config:
      timezone: UTC
      gcTTL: 86400
      logLevel: info
```

For all configurable start parameters of TiCDC, see [TiCDC configuration](https://github.com/pingcap/tiflow/blob/bf29e42c75ae08ce74fbba102fe78a0018c9d2ea/pkg/cmd/util/ticdc.toml).

#### Configure automatic failover thresholds of PD, TiDB, TiKV, and TiFlash

The [automatic failover](use-auto-failover.md) feature is enabled by default in TiDB Operator. When the Pods of PD, TiDB, TiKV, TiFlash fail or the corresponding nodes fail, TiDB Operator performs failover automatically and replenish the number of Pod replicas by scaling the corresponding components.

To avoid that the automatic failover feature creates too many Pods, you can configure the threshold of the maximum number of Pods that TiDB Operator can create during failover for each component. The default threshold is `3`. If the threshold for a component is configured to `0`, it means that the automatic failover feature is disabled for this component. An example configuration is as follows:

```yaml
  pd:
    maxFailoverCount: 3
  tidb:
    maxFailoverCount: 3
  tikv:
    maxFailoverCount: 3
  tiflash:
    maxFailoverCount: 3
```

### Configure graceful upgrade for TiDB cluster 

When you perform a rolling update to the TiDB cluster, Kubernetes sends a [`TERM`](https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods) signal to the TiDB server before it stops the TiDB Pod. When the TiDB server receives the `TERM` signal, it tries to wait for all connections to close. After 15 seconds, the TiDB server forcibly closes all the connections and exits the process.

You can enable this feature by configuring the following items:

- `spec.tidb.terminationGracePeriodSeconds`: The longest tolerable duration to delete the old TiDB Pod during the rolling upgrade. If this duration is exceeded, the TiDB Pod will be deleted forcibly.
- `spec.tidb.lifecycle`: Sets the `preStop` hook for the TiDB Pod, which is the operation executed before the TiDB server stops.

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
  version: v5.2.1
  pvReclaimPolicy: Retain
  discovery: {}
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "1Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "1Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: {}
    terminationGracePeriodSeconds: 60
    lifecycle:
      preStop:
        exec:
          command:
          - /bin/sh
          - -c
          - "sleep 10 && kill -QUIT 1"
```

The YAML file above:

- Sets the longest tolerable duration to delete the TiDB Pod to 60 seconds. If the client does not close the connections after 60 seconds, these connections will be closed forcibly. You can adjust the value according to your needs.
- Sets the value of `preStop` hook to `sleep 10 && kill -QUIT 1`. Here `PID 1` refers to the PID of the TiDB server process in the TiDB Pod. When the TiDB server process receives the signal, it exits only after all the connections are closed by the client.

When Kubernetes deletes the TiDB Pod, it also removes the TiDB node from the service endpoints. This is to ensure that the new connection is not established to this TiDB node. However, because this process is asynchronous, you can make the system sleep for a few seconds before you send the `kill` signal, which makes sure that the TiDB node is removed from the endpoints.

### Configure graceful upgrade for TiKV cluster

During TiKV upgrade, TiDB Operator evicts all Region leaders from TiKV Pod before restarting TiKV Pod. Only after the eviction is completed (which means the number of Region leaders on TiKV Pod drops to 0) or the eviction exceeds the specified timeout (10 minutes by default), TiKV Pod is restarted. 

If the eviction of Region leaders exceeds the specified timeout, restarting TiKV Pod causes issues such as failures of some requests or more latency. To avoid the issues, you can configure the timeout `spec.tikv.evictLeaderTimeout` (10 minutes by default) to a larger value. For example:

```
spec:
  tikv:
    evictLeaderTimeout: 10000m
```

> **Warning:**
>
> If the TiKV version is earlier than 4.0.14 or 5.0.3, due to [a bug of TiKV](https://github.com/tikv/tikv/pull/10364), you need to configure the timeout `spec.tikv.evictLeaderTimeout` as large as possible to ensure that all Region leaders on the TiKV Pod can be evicted within the timeout. If you are not sure about the proper value, greater than '1500m' is recommended.

### Configure PV for TiDB slow logs

By default, TiDB Operator creates a `slowlog` volume (which is an `EmptyDir`) to store the slow logs, mounts the `slowlog` volume to `/var/log/tidb`, and prints slow logs in the `stdout` through a sidecar container.

> **Warning:**
>
> By default, after a Pod is deleted (for example, rolling update), the slow query logs stored using the `EmptyDir` volume are lost. Make sure that a log collection solution has been deployed in the Kubernetes cluster to collect logs of all containers. If you do not deploy such a log collection solution, you **must** make the following configuration to use a persistent volume to store the slow query logs.

If you want to use a separate PV to store the slow logs, you can specify the name of the PV in `spec.tidb.slowLogVolumeName`, and then configure the PV in `spec.tidb.storageVolumes` or `spec.tidb.additionalVolumes`.

This section shows how to configure PV using `spec.tidb.storageVolumes` or `spec.tidb.additionalVolumes`.

#### Configure using `spec.tidb.storageVolumes`

Configure the `TidbCluster` CR as the following example. In the example, TiDB Operator uses the `${volumeName}` PV to store slow logs. The log file path is `${mountPath}/${volumeName}`.

For how to configure the `spec.tidb.storageVolumes` field, refer to [Multiple disks mounting](#multiple-disks-mounting).

> **Warning:
>
> You need to configure `storageVolumes` before creating the cluster. After the cluster is created, adding or removing `storageVolumes` is no longer supported. For the `storageVolumes` already configured, except for increasing `storageVolume.storageSize`, other modifications are not supported. To increase `storageVolume.storageSize`, you need to make sure that the corresponding StorageClass supports [dynamic expansion](https://kubernetes.io/blog/2018/07/12/resizing-persistent-volumes-using-kubernetes/).

{{< copyable "" >}}

```yaml
  tidb:
    ...
    separateSlowLog: true  # can be ignored
    slowLogVolumeName: ${volumeName}
    storageVolumes:
      # name must be consistent with slowLogVolumeName
      - name: ${volumeName}
        storageClassName: ${storageClass}
        storageSize: "1Gi"
        mountPath: ${mountPath}
```

#### Configure using `spec.tidb.additionalVolumes`

In the following example, NFS is used as the storage, and TiDB Operator uses the `${volumeName}` PV to store slow logs. The log file path is `${mountPath}/${volumeName}`.

For the supported PV types, refer to [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#types-of-persistent-volumes).

{{< copyable "" >}}

```yaml
  tidb:
    ...
    separateSlowLog: true  # can be ignored
    slowLogVolumeName: ${volumeName}
    additionalVolumes:
    # name must be consistent with slowLogVolumeName
    - name: ${volumeName}
      nfs:
        server: 192.168.0.2
        path: /nfs
    additionalVolumeMounts:
    # name must be consistent with slowLogVolumeName
    - name: ${volumeName}
      mountPath: ${mountPath}
```

### Configure TiDB service

You need to configure `spec.tidb.service` so that TiDB Operator creates a service for TiDB. You can configure Service with different types according to the scenarios, such as `ClusterIP`, `NodePort`, `LoadBalancer`, etc.

#### ClusterIP

`ClusterIP` exposes services through the internal IP of the cluster. When selecting this type of service, you can only access it within the cluster using ClusterIP or the Service domain name (`${cluster_name}-tidb.${namespace}`).

```yaml
spec:
  ...
  tidb:
    service:
      type: ClusterIP
```

#### NodePort

If there is no LoadBalancer, you can choose to expose the service through NodePort. NodePort exposes services through the node's IP and static port. You can access a NodePort service from outside of the cluster by requesting `NodeIP + NodePort`.

```yaml
spec:
  ...
  tidb:
    service:
      type: NodePort
      # externalTrafficPolicy: Local
```

NodePort has two modes:

- `externalTrafficPolicy=Cluster`: All machines in the cluster allocate a NodePort port to TiDB, which is the default value.

    When using the `Cluster` mode, you can access the TiDB service through the IP and NodePort of any machine. If there is no TiDB Pod on the machine, the corresponding request will be forwarded to the machine with TiDB Pod.

    > **Note:**
    >
    > In this mode, the request source IP obtained by the TiDB service is the host IP, not the real client source IP, so access control based on the client source IP is not available in this mode.

-`externalTrafficPolicy=Local`: Only the machine that TiDB is running on allocates a NodePort port to access the local TiDB instance.

#### LoadBalancer

If the TiDB cluster runs in an environment with LoadBalancer, such as on GCP or AWS, it is recommended to use the LoadBalancer feature of these cloud platforms by setting `tidb.service.type=LoadBalancer`.

```yaml
spec:
  ...
  tidb:
    service:
      annotations:
        cloud.google.com/load-balancer-type: "Internal"
      externalTrafficPolicy: Local
      type: LoadBalancer
```

See [Kubernetes Service Documentation](https://kubernetes.io/docs/concepts/services-networking/service/) to know more about the features of Service and what LoadBalancer in the cloud platform supports.

## Configure high availability

> **Note:**
>
> TiDB Operator provides a custom scheduler that guarantees TiDB service can tolerate host-level failures through the specified scheduling algorithm. Currently, the TiDB cluster uses this scheduler as the default scheduler, which is configured through the item `spec.schedulerName`. This section focuses on configuring a TiDB cluster to tolerate failures at other levels such as rack, zone, or region. This section is optional.

TiDB is a distributed database and its high availability must ensure that when any physical topology node fails, not only the service is unaffected, but also the data is complete and available. The two configurations of high availability are described separately as follows.

### High availability of TiDB service

#### Use affinity to schedule pods

By configuring `PodAntiAffinity`, you can avoid the situation in which different instances of the same component are deployed on the same physical topology node. In this way, disaster recovery (high availability) is achieved. For the user guide of Affinity, see [Affinity & AntiAffinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity).

The following is an example of a typical service high availability setup:

{{< copyable "" >}}

```yaml
>>>>>>> 0b4bb8f2 (changed github.com/pingcap/ticdc to github.com/pingcap/tiflow (#1482))
affinity:
 podAntiAffinity:
   preferredDuringSchedulingIgnoredDuringExecution:
   # this term works when the nodes have the label named region
   - weight: 10
     podAffinityTerm:
       labelSelector:
         matchLabels:
           app.kubernetes.io/instance: <release name>
           app.kubernetes.io/component: "pd"
       topologyKey: "region"
       namespaces:
       - <helm namespace>
   # this term works when the nodes have the label named zone
   - weight: 20
     podAffinityTerm:
       labelSelector:
         matchLabels:
           app.kubernetes.io/instance: <release name>
           app.kubernetes.io/component: "pd"
       topologyKey: "zone"
       namespaces:
       - <helm namespace>
   # this term works when the nodes have the label named rack
   - weight: 40
     podAffinityTerm:
       labelSelector:
         matchLabels:
           app.kubernetes.io/instance: <release name>
           app.kubernetes.io/component: "pd"
       topologyKey: "rack"
       namespaces:
       - <helm namespace>
   # this term works when the nodes have the label named kubernetes.io/hostname
   - weight: 80
     podAffinityTerm:
       labelSelector:
         matchLabels:
           app.kubernetes.io/instance: <release name>
           app.kubernetes.io/component: "pd"
       topologyKey: "kubernetes.io/hostname"
       namespaces:
       - <helm namespace>
```

### Disaster recovery of data

Before configuring the data disaster recovery, read [Information Configuration of the Cluster Typology](https://pingcap.com/docs/v3.0/how-to/deploy/geographic-redundancy/location-awareness/) which describes how the disaster recovery of the TiDB cluster is implemented.

To add the data disaster recovery feature in Kubernetes:

1. Set the label collection of topological location for PD

    Configure `location-labels` in the `pd.config` file using the labels that describe the topology on the nodes in the Kubernetes cluster.

    > **Note:**
    >
    > * For PD versions < v3.0.9, the `/` in the label name is not supported.
    > * If you configure `hostname` in the `location-labels`, TiDB Operator will get the value from the `kubernetes.io/hostname` label on the node.

2. Set the topological information of the Node where the TiKV node is located.

    TiDB Operator automatically obtains the topological information of the Node for TiKV and calls the PD interface to set this information as the information of TiKV's store labels. Based on this topological information, the TiDB cluster schedules the replicas of the data.

    If the Node of the current Kubernetes cluster does not have a label indicating the topological location, or if the existing label name of topology contains `/`, you can manually add a label to the Node by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl label node <nodeName> region=<regionName> zone=<zoneName> rack=<rackName> kubernetes.io/hostname=<hostName>
    ```

    In the command above, `region`, `zone`, `rack`, and `kubernetes.io/hostname` are just examples. The name and number of the label to be added can be arbitrarily defined, as long as it conforms to the specification and is consistent with the labels set by `location-labels` in `pd.config`.
