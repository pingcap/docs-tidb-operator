---
title: 基于 EBS 快照备份恢复的常见问题
summary: 介绍卷快照备份恢复上的 TiDB 集群常见问题以及解决方案。
---

# 基于 EBS 快照备份恢复的常见问题

本文介绍基于 EBS 快照备份恢复的常见问题以及解决方案。

## 备份问题

使用基于 EBS 快照备份，你可能遇到以下问题：

### 备份无法启动或者启动后立即失败

相关的问题：[#4781](https://github.com/pingcap/tidb-operator/issues/4781)

现象一：应用备份 CRD yaml 文件后，pod/job 并没有创建。备份无法启动。

* 通过以下命令查看 TiDB Operator pod 信息

    ```shell
    kubectl get po -n ${namespace}
    ```

* 查看 TiDB Operator controller manager pod 的 log 信息

    ```shell
    kubectl -n ${namespace} logs ${tidb-controller-manager}
    ```

* 检查 log 信息是否包含以下错误

    ```shell
    metadata.annotations: Too long: must have at most 262144 bytes, spec.template.annotations: Too long: must have at most 262144 bytes
    ```
    
原因：因为我们使用 annotation 来传递 PVC/PV 的配置信息，每个备份 job 的 annotation 最大的限制是 256K，当 TiKV 集群规模较大时，PVC/PV 的信息会大于256K导致 Kubernetes API 调用失败。

现象二：应用备份 CRD yaml 文件后，pod/job 创建成功。备份立即失败

通过现象一类似的方法查看 backup job 的 log 信息，得到以下错误：

    ```shell
    exec /entrypoint.sh: argument list too long
    ```

原因：TiDB Operator 使用环境变量的方式，在 backup pod 启动前，把 PVC/PV 的信息注入到 backup pod 环境变量中，并启动备份任务。因操作系统环境变量限制在 1MB 左右，当 PVC/PV 配置信息大于 1MB 时，backup pod 无法取得环境变量导致失败。
问题发生的场景：大量的 TiKV 节点 （40+) 或者卷的配置较多的集群，使用了 TiDB Operator 版本 v1.4.0-beta.2 或者更早的版本
解决方案：升级 TiDB Operator 到最新版本

### 备份失败后，备份 CR 无法删除。

相关的问题：[#4778](https://github.com/pingcap/tidb-operator/issues/4778)
现象：删除备份 CR 卡住。
问题发生的场景：使用了 TiDB Operator 版本 v1.4.0-beta.2 或者更早的版本。
解决方案：升级 TiDB Operator 到最新版本。

### 备份发起后，立即失败

相关的问题：[#13838](https://github.com/tikv/tikv/issues/13838)
现象：应用备份 CRD yaml 文件后，pod/job 创建成功。备份立即失败
* 检查备份 log 信息是否包含以下错误

    ```shell
    GC safepoint 437271276493996032 exceed TS 437270540511608835
    ```

问题发生的场景：在大集群 （20+ tikv）中，集群使用 BR 进行大规模数据恢复后。再发起卷备份操作。

解决方案：打开 grafana ${cluster-name}-TiKV-Details 面板，检查 Resolved-TS，确认是否有数值较大的 Max Resolved TS gap. 找到对应的 TiKV 重启。

## 恢复问题

### 恢复集群失败 keepalive watchdog timeout

现象：BR 数据恢复子任务失败，第一个 BR 恢复子任务恢复成功 （volume complete)，第二个子任务失败。打印失败任务 log 发现以下 log 信息：

    ```shell
    error="rpc error: code = Unavailable desc = keepalive watchdog timeout"
    ```

问题发生的场景：数据规模较大且使用的 TiDB Cluster v6.3.0 的版本
解决方案：
1. 升级 TiDB Cluster 到 v6.4.0 或者更高的版本

2. 编辑 TiDB Cluster 配置，调大 TiKV keepalive 参数：

    ```shell
    config: |
      [server]
        grpc-keepalive-time = "500s"
        grpc-keepalive-timeout = "10s"
    ```

## 恢复时间太长 （大于 2 小时）

问题发生的场景：使用 TiDB Cluster v6.3.0 的版本，或者 v6.4.0 版本
解决方案：
1. 升级 TiDB Cluster v6.3.0 的版本至 v6.5.0

2. 在 BR spec 中，临时提升卷性能进行恢复，待恢复完成后，再手动降低卷性能参数。通过指定参数 `--volume-iops=8000`，以及 `--volume-throughput=600` 来获得更高的恢复卷配置。

    ```yaml
    spec:
      backupType: full
      restoreMode: volume-snapshot
      serviceAccount: tidb-backup-manager
      toolImage: pingcap/br:v6.5.0
      br:
        cluster: basic
        clusterNamespace: tidb-cluster
        sendCredToTikv: false
    options:
    - --volume-type=gp3
    - --volume-iops=8000
    - --volume-throughput=600
    ```