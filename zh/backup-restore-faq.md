---
title: 基于 EBS 快照备份恢复的常见问题
summary: 介绍卷快照备份恢复中的常见问题以及解决方案。
---

# 基于 EBS 快照备份恢复的常见问题

本文介绍基于 EBS 快照备份恢复的常见问题以及解决方案。

## 备份问题

使用基于 EBS 快照备份，你可能遇到以下问题：

- [升级后备份无法工作](#升级后备份无法工作)
- [备份无法启动或者启动后立即失败](#备份无法启动或者启动后立即失败)
- [备份失败后，备份 CR 无法删除](#备份失败后备份-cr-无法删除)
- [备份失败](#备份失败)

### 升级后备份无法工作

从低版本的集群升级到 v6.5.0+ 后，进行卷快照备份，备份可能会失败，错误信息如下：

```shell
error="min resolved ts not enabled"
```

原因是 PD 配置 `min-resolved-ts-persistence-interval` 值为 0，即关闭了 PD 全局一致性 min-resolved-ts 服务。EBS 卷快照需要此服务获取集群全局一致性时时间戳。可通过 SQL 语句或 pd-ctl 检查配置：

- 使用 SQL 语句检查 PD `min-resolved-ts-persistence-interval` 配置：

    ```sql
    SHOW CONFIG WHERE type='pd' AND name LIKE '%min-resolved%'
    ```

    如果全局一致性 min-resolved-ts 服务关闭，则输出显示如下：

    ```sql
    +------+------------------------------------------------+------------------------------------------------+-------+
    | Type | Instance                                       | Name                                           | Value |
    +------+------------------------------------------------+------------------------------------------------+-------+
    | pd   | basic-pd-0.basic-pd-peer.tidb-cluster.svc:2379 | pd-server.min-resolved-ts-persistence-interval | 0s    |
    +------+------------------------------------------------+------------------------------------------------+-------+
    1 row in set (0.03 sec)
    ```

    如果全局一致性 min-resolved-ts 服务打开，则输出显示如下：

    ```sql
    +------+------------------------------------------------+------------------------------------------------+-------+
    | Type | Instance                                       | Name                                           | Value |
    +------+------------------------------------------------+------------------------------------------------+-------+
    | pd   | basic-pd-0.basic-pd-peer.tidb-cluster.svc:2379 | pd-server.min-resolved-ts-persistence-interval | 1s    |
    +------+------------------------------------------------+------------------------------------------------+-------+
    1 row in set (0.03 sec)
    ```

- 使用 pd-ctl 工具检查 PD `min-resolved-ts-persistence-interval` 配置：

    ```shell
    kubectl -n ${namespace} exec -it ${pd-pod-name} -- /pd-ctl min-resolved-ts
    ```

    如果全局一致性 min-resolved-ts 服务关闭，则输出显示如下：

    ```json
    {
      "min_resolved_ts": 439357537983660033,
      "persist_interval": "0s"
    }
    ```

    如果全局一致性 min-resolved-ts 服务打开，则输出显示如下：

    ```json
    {
      "is_real_time": true,
      "min_resolved_ts": 439357519607365634,
      "persist_interval": "1s"
    }
    ```

解决方案（二选一）：

- 使用 SQL 语句更新 PD `min-resolved-ts-persistence-interval` 配置：

    ```sql
    SET CONFIG pd `pd-server.min-resolved-ts-persistence-interval` = "1s"
    ```

- 使用 pd-ctl 工具更新 PD `min-resolved-ts-persistence-interval` 配置：

    ```shell
    kubectl -n ${namespace} exec -it ${pd-pod-name} -- /pd-ctl config set min-resolved-ts-persistence-interval 1s
    ```

### 备份无法启动或者启动后立即失败

issue 链接：[#4781](https://github.com/pingcap/tidb-operator/issues/4781)

- 现象一：应用备份 CRD yaml 文件后，pod/job 并没有创建。备份无法启动。

    1. 通过以下命令查看 TiDB Operator pod 信息：

        ```shell
        kubectl get po -n ${namespace}
        ```

    2. 查看 TiDB Operator controller manager pod 的 log 信息：

        ```shell
        kubectl -n ${namespace} logs ${tidb-controller-manager}
        ```

    3. 检查 log 信息是否包含以下错误：

        ```shell
        metadata.annotations: Too long: must have at most 262144 bytes, spec.template.annotations: Too long: must have  at most 262144 bytes
        ```

    原因：因为 TiDB 使用 annotation 来传递 PVC 或 PV 的配置信息，每个备份 job 的 annotation 最大的限制是 256 KB，当 TiKV 集群规模较大时，PVC 或 PV 的信息会大于 256 KB 导致 Kubernetes API 调用失败。

- 现象二：应用备份 CRD yaml 文件后，pod/job 创建成功。备份立即失败。

    通过现象一类似的方法查看 backup job 的 log 信息，得到以下错误：

    ```shell
    exec /entrypoint.sh: argument list too long
    ```

    原因：TiDB Operator 使用环境变量的方式，在 backup pod 启动前，把 PVC 或 PV 的信息注入 backup pod 环境变量中，并启动备份任务。因操作系统环境变量限制在 1 MB 左右，当 PVC 或 PV 配置信息大于 1 MB 时，backup pod 无法取得环境变量，导致备份失败。

    问题场景：集群包含大量的 TiKV 节点 (40+) 或者配置了较多卷，且使用了 TiDB Operator v1.4.0-beta.2 或者更早的版本。

解决方案：升级 TiDB Operator 到最新版本。

### 备份失败后，备份 CR 无法删除

issue 链接：[#4778](https://github.com/pingcap/tidb-operator/issues/4778)

现象：删除备份 CR 卡住。

问题场景：使用了 TiDB Operator 版本 v1.4.0-beta.2 或者更早的版本。

解决方案：升级 TiDB Operator 到最新版本。

### 备份失败

相关的问题：[#13838](https://github.com/tikv/tikv/issues/13838)

现象：应用备份 CRD yaml 文件后，pod/job 创建成功。备份立即失败。

检查备份 log 信息是否包含以下错误：

```shell
GC safepoint 437271276493996032 exceed TS 437270540511608835
```

问题场景：在大集群 (20+ tikv) 中，集群使用 BR 进行大规模数据恢复后，再发起卷备份操作。

解决方案：打开 grafana `${cluster-name}`-TiKV-Details 监控页面，展开 Resolved-TS，检查 Max Resolved TS gap 面板。确认是否有数值较大（大于 1 min) 的 Max Resolved TS，找到对应的 TiKV 重启。

> **注意：**
>
> 备份失败可能产生中间残留文件，如 `clustermeta` 或 `backup.lock`。需要将它们清理后，才能使用相同的备份目录再次进行备份。

## 恢复问题

使用基于 EBS 快照恢复，你可能遇到以下问题：

- [恢复集群失败，报错 `keepalive watchdog timeout`](#恢复集群失败报错-keepalive-watchdog-timeout)
- [恢复时间太长 （大于 2 小时）](#恢复时间太长大于-2-小时)

### 恢复集群失败，报错 `keepalive watchdog timeout`

现象：BR 数据恢复子任务失败，第一个 BR 恢复子任务恢复成功 (volume complete)，第二个子任务失败。打印失败任务 log，发现以下 log 信息：

```shell
error="rpc error: code = Unavailable desc = keepalive watchdog timeout"
```

问题场景：数据规模较大且使用的 v6.3.0 版本的 TiDB 集群。

解决方案：

1. 升级 TiDB 集群到 v6.4.0 或者更高的版本。

2. 编辑 TiDB 集群配置，调大 TiKV `keepalive` 参数：

    ```yaml
    config: |
      [server]
        grpc-keepalive-time = "500s"
        grpc-keepalive-timeout = "10s"
    ```

### 恢复时间太长（大于 2 小时）

问题场景：使用 TiDB v6.3.0 的版本，或者 v6.4.0 版本。

解决方案：

1. 升级 TiDB 集群版本至 v6.5.0+。

2. 在 BR spec 中，临时提升卷性能进行恢复，待恢复完成后，再手动降低卷性能参数。通过指定参数来获得更高的恢复卷配置, 例如指定 `--volume-iops=8000`，以及 `--volume-throughput=600` 或者更高配置。

    ```yaml
    spec:
      backupType: full
      restoreMode: volume-snapshot
      serviceAccount: tidb-backup-manager
      toolImage: pingcap/br:v8.0.0
      br:
        cluster: basic
        clusterNamespace: tidb-cluster
        sendCredToTikv: false
    options:
    - --volume-type=gp3
    - --volume-iops=8000
    - --volume-throughput=600
    ```
