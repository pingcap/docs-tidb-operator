---
title: 基于 EBS 卷快照备份恢复的性能介绍
summary: 了解 EBS 卷快照备份恢复的性能基线。
---

# EBS 卷快照备份的性能

本节介绍影响备份性能的因素以及性能测试结果。
以下测试指标基于 AWS region：us-west-2。

## EBS 卷快照备份各阶段的耗时

EBS 卷快照备份阶段包含创建备份任务，停止调度，停止 GC，获取备份时间 backupts 以及 卷快照。其中最耗时的部分是创建卷快照。备份过程中卷的快照创建是并行的，一个备份完成时间取决于用时最长的快照完成时间。

## EBS 卷快照备份的性能

卷快照备份时间取决于最长数据卷快照完成时间，这部分工作由 AWS EBS 服务来完成，当前 AWS 并没有提供卷快照完成量化指标。根据我们的测试，在 TiDB-Operator 推荐配置下 （GP3）整个备份时间大致如下：

![EBS Snapshot backup perf](/media/volume-snapshot-backup-perf.png)

| 单卷数据  | 卷大小   | 卷配置         | 备份大致耗时 |
| :------: | :-----: | :-----------: | :--------: |
| 50 GB    | 500 GB  | 125MB/3000IOPS | 20 min    |
| 100 GB   | 500 GB  | 125MB/3000IOPS | 50 min    |
| 200 GB   | 500 GB  | 125MB/3000IOPS | 100 min   |
| 500 GB   | 1024 GB | 125MB/3000IOPS | 150 min   |
| 1024 GB  | 3500 GB | 125MB/7000IOPS | 350 min   |

# EBS 卷快照恢复的性能

本节介绍影响恢复性能的因素以及性能测试结果。
## EBS 卷快照恢复各阶段的耗时

EBS 卷快照恢复阶段包含以下阶段，详细见 [基于 EBS 卷快照的备份恢复功能架构](backup-restore-overview.md)

1. 创建集群阶段

TiDB Operator 创建 recoveryMode 的待恢复集群，启动所有 PD 节点。

2. 卷恢复阶段

TiDB Operator 创建 BR 卷恢复子任务，BR 从卷快照中恢复出 TiKV 启动需要的数据卷。

3. 启动 TiKV 阶段

TiDB Operator 挂载 TiKV 卷，启动 TiKV。

4. 数据恢复阶段

TiDB Operator 创建 TiKV 卷数据恢复子任务，BR 把所以 TiKV 数据卷恢复到一致性状态。

5. 启动 TiDB：启动 TiDB，恢复完成

### 各阶段耗时总占比

| 恢复阶段     | 恢复大致耗时 | 恢复总占比 | 备注                                          |
| :--------: | :---------: | :------: | :-------------------------------------------: |
| 创建集群     | 30s         | %1       | 包含下载 docker image 和启动 pd                 |
| 卷恢复      | 20s         | %1       | 包含启动 br pod 和卷恢复                         |
| TiKV 启动   | 3min/30min  | 58%      | 有写入的备份恢复，rocksdb 启动产生额外耗时 2～30min |
| 数据恢复阶段 | 20min       | 38%      | 20 min 是已验证最大数据量 20 TB 的耗时            |
| 启动 TiDB   | 1min        | 2%       | 包含下载 tidb docker image， 和启动 tidb         |

Notice: 因为卷快照是 crash consistency 的状态，EBS 卷快照恢复阶段 TiKV 启动阶段， 需要先启动 kv db (rocksdb), 此阶段在有写入的备份恢复中，会产生额外的耗时。经测试，额外的耗时在 30 分钟以内，如使用高性能盘恢复，如 io2, 额外耗时可缩短到 5 分钟内，如果使用标准 GP3 盘 （3000IOPS/125MBps），额外耗时可能到达到 30 分钟左右。

## EBS 卷快照恢复阶段的性能

卷快照恢复时间取主要决于 TiKV 启动和数据恢复阶段，TiKV 启动受 EBS 卷快照恢复延迟初始化影响，启动时间在2分钟到30分钟之间，这部分工作由 AWS EBS 服务来完成，当前 AWS 并没有提供卷快照完成量化指标。根据我们的测试，在 TiDB-Operator 推荐 EC2 机型配置下 使用 GP3 整个恢复时间大致如下：

![EBS Snapshot backup perf](/media/volume-snapshot-restore-perf.png)

| 单卷数据  | 卷大小   | 卷配置         | 恢复大致耗时 |
| :------: | :-----: | :-----------: | :--------: |
| 50 GB    | 500 GB  | 400MB/7000IOPS | 16 min    |
| 100 GB   | 500 GB  | 400MB/7000IOPS | 18 min    |
| 200 GB   | 500 GB  | 400MB/7000IOPS | 21 min   |
| 500 GB   | 1024 GB | 400MB/7000IOPS | 25 min   |
| 1024 GB  | 3500 GB | 400MB/7000IOPS | 34 min   |

## EBS 卷快照恢复的性能案例

此案例主要用于探索 EBS 卷快照恢复速度的上限。
### EKS 集群配置
| 节点类型 | EC2 型号     | 个数  | AZ         |
| :-----: | :---------: | :--: | :--------: |
| admin   | NA          | 1    | us-west-2a |
| pd      | c5.xlarge   | 3    | us-west-2a |
| tidb    | c5.2xlarge  | 3    | us-west-2a |
| tikv    | r5n.2xlarge | 20   | us-west-2a |

### TiDB Cluster 集群配置

GP3 storage class 配置：

```yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
parameters:
  type: gp3
  fsType: ext4
  iops: "7000"
  throughput: "400"
mountOptions:
- nodelalloc,noatime
```

TiDB Cluster 配置：

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
  namespace: tidb-cluster
spec:
  version: nightly
  timezone: UTC
  configUpdateStrategy: RollingUpdate
  pvReclaimPolicy: Retain
  schedulerName: default-scheduler
  recoveryMode: true
  topologySpreadConstraints:
  - topologyKey: topology.kubernetes.io/zone
  enableDynamicConfiguration: true
  helper:
    image: alpine:3.16.0
  pd:
    baseImage: pingcap/pd
    maxFailoverCount: 0
    replicas: 3
    requests:
      storage: "100Gi"
    version: "nightly"
    config: |
      [dashboard]
        internal-proxy = true
      [replication]
        location-labels = ["topology.kubernetes.io/zone", "kubernetes.io/hostname"]
        max-replicas = 3
    nodeSelector:
      dedicated: pd
    tolerations:
    - effect: NoSchedule
      key: dedicated
      operator: Equal
      value: pd
    affinity:
      podAntiAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
            - key: app.kubernetes.io/component
              operator: In
              values:
              - pd
          topologyKey: kubernetes.io/hostname
  tikv:
    baseImage: pingcap/tikv
    maxFailoverCount: 0
    replicas: 20
    requests:
      storage: "3200Gi"
    version: "nightly"
    storageClassName: gp3
    config: |
      [backup]
        num-threads = 8
        enable-auto-tune = false
    nodeSelector:
          dedicated: tikv
    tolerations:
    - effect: NoSchedule
      key: dedicated
      operator: Equal
      value: tikv
    affinity:
      podAntiAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
            - key: app.kubernetes.io/component
              operator: In
              values:
              - tikv
          topologyKey: kubernetes.io/hostname
  tidb:
    baseImage: pingcap/tidb
    maxFailoverCount: 0
    replicas: 3
    service:
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: 'true'
        service.beta.kubernetes.io/aws-load-balancer-type: nlb
        service.beta.kubernetes.io/aws-load-balancer-scheme: internal
        service.beta.kubernetes.io/aws-load-balancer-internal: "true"
      exposeStatus: true
      externalTrafficPolicy: Local
      type: LoadBalancer
    config: |
      [performance]
        tcp-keep-alive = true
    annotations:
      tidb.pingcap.com/sysctl-init: "true"
    podSecurityContext:
      sysctls:
      - name: net.ipv4.tcp_keepalive_time
        value: "300"
      - name: net.ipv4.tcp_keepalive_intvl
        value: "75"
      - name: net.core.somaxconn
        value: "32768"
    separateSlowLog: true
    version: "nightly"
    nodeSelector:
      dedicated: tidb
    tolerations:
    - effect: NoSchedule
      key: dedicated
      operator: Equal
      value: tidb
    affinity:
      podAntiAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
            - key: app.kubernetes.io/component
              operator: In
              values:
              - tidb
          topologyKey: kubernetes.io/hostname
```

### EBS 卷快照恢复 BR 配置

```yaml
apiVersion: pingcap.com/v1alpha1
kind: Restore
metadata:
  name: rt-20tikv-1tb
  namespace: tidb-cluster
spec:
  backupType: full
  restoreMode: volume-snapshot
  serviceAccount: tidb-backup-manager
  toolImage: gozssky/br:v20221127-560cadc
  br:
    cluster: basic
    clusterNamespace: tidb-cluster
    sendCredToTikv: false
    options:
    - --volume-iops=7000
  s3:
    provider: aws
    region: us-west-2
    bucket: ebs-west-2
    prefix: snap_20tikv-1tb
```

### EBS 卷快照恢复耗时

基于以上配置，EBS 卷快照恢复大致恢复时间如下：

| 总数据量 | 单卷数据量 | TiKV 个数 | 创建集群耗时 | 卷恢复耗时 | TiKV 启动 | 数据恢复耗时 | TiDB 启动 | 总恢复耗时 |
| :-----: | :------: | :------: | :--------: | :------: | :-------: | :--------: | :------: | :-------: |
| 21 TB   | 1 TB     | 20       | 60s        | 6s       | 190s      | 786       | 60s      | 18m16s    |

> **注意：**
>
> - 以上测试，为节省成本和测试最大能力上限，没有在加负载的情况下备份和恢复。根据我们的测试有负载的场景恢复时间会多花 15 分钟左右，因 TiKV 启动过程中需要恢复 rocksdb 的数据。
