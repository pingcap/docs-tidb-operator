---
title: 使用 BR 备份 TiDB 集群数据到兼容 S3 的存储
summary: 介绍如何使用 BR 备份 TiDB 集群数据到兼容 Amazon S3 的存储。
---

<!-- markdownlint-disable MD007 -->

# 使用 BR 备份 TiDB 集群数据到兼容 S3 的存储

本文介绍如何将运行在 AWS Kubernetes 环境中的 TiDB 集群数据备份到 AWS 的存储上。

本文使用的备份方式基于 TiDB Operator 的 Custom Resource Definition(CRD) 实现，底层使用 [BR](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 获取集群数据，然后再将数据上传到 AWS 的存储上。BR 全称为 Backup & Restore，是 TiDB 分布式备份恢复的命令行工具，用于对 TiDB 集群进行数据备份和恢复。

## 使用场景

如果你对数据备份有以下要求，可考虑使用 BR 将 TiDB 集群数据以 [Ad-hoc 备份](#ad-hoc-备份)或[定时全量备份](#定时全量备份)的方式备份至兼容 S3 的存储上：

- 需要备份的数据量较大，而且要求备份速度较快
- 需要直接备份数据的 SST 文件（键值对）

如有其他备份需求，请参考[备份与恢复简介](backup-restore-overview.md)选择合适的备份方式。

> **注意：**
>
> - BR 只支持 TiDB v3.1 及以上版本。
> - 使用 BR 备份出的数据只能恢复到 TiDB 数据库中，无法恢复到其他数据库中。

## Ad-hoc 备份

Ad-hoc 备份支持全量备份与增量备份。

要进行 Ad-hoc 备份，你需要创建一个自定义的 `Backup` custom resource (CR) 对象来描述本次备份。创建好 `Backup` 对象后，TiDB Operator 根据这个对象自动完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

本文假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份。下面是具体的操作过程。

### 第 1 步：准备 Ad-hoc 备份环境

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/v1.3.2/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 授予远程存储访问权限。

    - 如果使用 Amazon S3 来备份集群，可以使用三种方式授予权限，可参考文档 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权)。
    - 如果使用其他兼容 S3 的存储来备份集群，例如 Ceph、MinIO，可以使用 AccessKey 和 SecretKey 授权的方式，可参考文档[通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-accesskey-和-secretkey-授权)。

3. 如果你使用的 TiDB 版本低于 v4.0.8，你还需要完成以下步骤。如果你使用的 TiDB 为 v4.0.8 及以上版本，请跳过这些步骤。

    1. 确保你拥有备份数据库 `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限，用于备份前后调整 GC 时间。

    2. 创建 `backup-demo1-tidb-secret` secret 用于存放访问 TiDB 集群的用户所对应的密码。

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
        ```

### 第 2 步：备份数据到兼容 S3 的存储

根据上一步选择的远程存储访问授权方式，你需要使用下面对应的方法将数据导出到兼容 S3 的存储上：

+ 方法 1：如果通过了 accessKey 和 secretKey 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    `backup-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      backupType: full
      br:
        cluster: demo1
        clusterNamespace: test1
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # sendCredToTikv: true
        # options:
        # - --lastbackupts=420134118382108673
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 2：如果通过了 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    `backup-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      backupType: full
      br:
        cluster: demo1
        sendCredToTikv: false
        clusterNamespace: test1
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # options:
        # - --lastbackupts=420134118382108673
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 方法 3：如果通过了 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `Backup` CR 备份集群数据:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    `backup-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      backupType: full
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo1
        sendCredToTikv: false
        clusterNamespace: test1
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # options:
        # - --lastbackupts=420134118382108673
      # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

在配置 `backup-aws-s3.yaml` 文件时，请参考以下信息：

- 自 TiDB Operator v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考[使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。
- Amazon S3 的 `acl`、`endpoint`、`storageClass` 配置项均可以省略。兼容 S3 的存储相关配置，请参考 [S3 存储字段介绍](backup-restore-cr.md#s3-存储字段介绍)。
- `.spec.br` 中的一些参数是可选的，例如 `logLevel`、`statusAddr` 等。完整的 `.spec.br` 字段的详细解释，请参考 [BR 字段介绍](backup-restore-cr.md#br-字段介绍)。
- 如果你使用的 TiDB 为 v4.0.8 及以上版本, BR 会自动调整 `tikv_gc_life_time` 参数，不需要配置 `spec.tikvGCLifeTime` 和 `spec.from` 字段。
- 更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

创建好 `Backup` CR 后，TiDB Operator 会根据 `Backup` CR 自动开始备份。你可以通过如下命令查看备份状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -n test1 -o wide
```

### 备份示例

<details>
<summary>备份全部集群数据</summary>

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

<details>
<summary>备份单个数据库的数据</summary>

以下示例中，备份 `db1` 数据库的数据。

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.*"
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

<details>
<summary>备份单张表的数据</summary>

以下示例中，备份 `db1.table1` 表的数据。

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.table1"
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

<details>
<summary>使用表库过滤功能备份多张表的数据</summary>

以下示例中，备份 `db1.table1` 表 和  `db1.table2` 表的数据。

```yaml
---
apiVersion: pingcap.com/v1alpha1
kind: Backup
metadata:
  name: demo1-backup-s3
  namespace: test1
spec:
  backupType: full
  serviceAccount: tidb-backup-manager
  tableFilter:
  - "db1.table1"
  - "db1.table2"
  # ...
  br:
    cluster: demo1
    sendCredToTikv: false
    clusterNamespace: test1
  # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
  # from:
    # host: ${tidb_host}
    # port: ${tidb_port}
    # user: ${tidb_user}
    # secretName: backup-demo1-tidb-secret
  s3:
    provider: aws
    region: us-west-1
    bucket: my-bucket
    prefix: my-folder
```

</details>

## 定时全量备份

你可以通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。

### 第 1 步：准备定时全量备份环境

同[准备 Ad-hoc 备份环境](#第-1-步准备-ad-hoc-备份环境)。

### 第 2 步：定时备份数据到兼容 S3 的存储

依据准备 Ad-hoc 备份环境时所选择的远程存储访问授权方式，你需要使用下面对应的方法将数据定时备份到 Amazon S3 存储上：

+ 方法 1：如果通过了 accessKey 和 secretKey 的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时全量备份：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-scheduler-aws-s3.yaml
    ```

    `backup-scheduler-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-s3
      namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        backupType: full
        br:
          cluster: demo1
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status_addr}
          # concurrency: 4
          # rateLimit: 0
          # timeAgo: ${time}
          # checksum: true
          # sendCredToTikv: true
        # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        s3:
          provider: aws
          secretName: s3-secret
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder
    ```

+ 方法 2：如果通过了 IAM 绑定 Pod 的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时全量备份：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-scheduler-aws-s3.yaml
    ```

    `backup-scheduler-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-s3
      namespace: test1
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        backupType: full
        br:
          cluster: demo1
          sendCredToTikv: false
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status_addr}
          # concurrency: 4
          # rateLimit: 0
          # timeAgo: ${time}
          # checksum: true
        # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        s3:
          provider: aws
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder
    ```

+ 方法 3：如果通过了 IAM 绑定 ServiceAccount 的方式授权，你可以按照以下说明创建 `BackupSchedule` CR，开启 TiDB 集群定时全量备份：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-scheduler-aws-s3.yaml
    ```

    `backup-scheduler-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-s3
      namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      serviceAccount: tidb-backup-manager
      backupTemplate:
        backupType: full
        br:
          cluster: demo1
          sendCredToTikv: false
          clusterNamespace: test1
          # logLevel: info
          # statusAddr: ${status_addr}
          # concurrency: 4
          # rateLimit: 0
          # timeAgo: ${time}
          # checksum: true
        # Only needed for TiDB Operator < v1.1.10 or TiDB < v4.0.8
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        s3:
          provider: aws
          region: us-west-1
          bucket: my-bucket
          prefix: my-folder
    ```

从以上 `backup-scheduler-aws-s3.yaml` 文件配置示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。

- 关于 `backupSchedule` 独有的配置项具体介绍，请参考 [BackupSchedule CR 字段介绍](backup-restore-cr.md#backupschedule-cr-字段介绍)。
- `backupTemplate` 用于指定集群及远程存储相关的配置，字段和 Backup CR 中的 `spec` 一样，详细介绍可参考 [Backup CR 字段介绍](backup-restore-cr.md#backup-cr-字段介绍)。

定时全量备份创建完成后，可以通过以下命令查看定时全量备份的状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bks -n test1 -o wide
```

查看定时全量备份下面所有的备份条目：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-s3 -n test1
```

## 删除备份的 Backup CR

如果你不再需要已备份的 Backup CR，请参考[删除备份的 Backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
