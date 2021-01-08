---
title: 使用兼容 S3 的存储备份与恢复 TiDB 集群数据
summary: 介绍如何使用兼容 S3 的存储备份与恢复 TiDB 集群数据。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/backup-to-s3/', '/docs-cn/tidb-in-kubernetes/dev/restore-from-s3/', '/docs-cn/tidb-in-kubernetes/dev/backup-to-aws-s3-using-br/', '/docs-cn/tidb-in-kubernetes/dev/restore-from-aws-s3-using-br/']
---

# 使用兼容 S3 的存储备份与恢复 TiDB 集群数据

本文档详细描述了如何使用 Dumpling 、BR 将 Kubernetes 上的 TiDB 集群数据备份到兼容 S3 的远程存储，以及如何使用 TiDB Lightning 、BR 将存储在兼容 S3 的远程存储的备份数据恢复到 TiDB 集群。

本文使用的备份方式基于 TiDB Operator 新版（v1.1 及以上）的 CustomResourceDefinition (CRD) 实现。

## 使用 Dumpling 备份 TiDB 集群到兼容 S3 的存储

以下示例将使用 Dumpling 备份 TiDB 集群数据到兼容 S3 的远程存储。本节中的“备份”，均是指全量备份（Ad-hoc 全量备份和定时全量备份），底层通过使用 [`Dumpling`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview) 获取集群的逻辑备份，然后再将备份数据上传到远程存储。

### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：备份前后，backup CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间
* SELECT
* RELOAD
* LOCK TABLES
* REPLICATION CLIENT

### Ad-hoc 全量备份

Ad-hoc 全量备份通过创建一个自定义的 `Backup` custom resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

目前兼容 S3 的存储中，Ceph 和 Amazon S3 经测试可正常工作。下文对 Ceph 和 Amazon S3 这两种存储的使用进行描述。本文档提供如下备份示例。示例假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

#### Ad-hoc 全量备份到 S3 环境准备

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 存储访问授权

    如果使用 Amazon S3 来备份集群，可以使用三种权限授予方式授予权限，参考 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权) 授权访问兼容 S3 的远程存储；使用 Ceph 作为后端存储测试备份时，是通过 AccessKey 和 SecretKey 模式授权，设置方式可参考 [通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-accesskey-和-secretkey-授权)。
    
3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的用户所对应的密码。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

#### 备份数据到兼容 S3 的存储

> **注意：**
>
> 由于 `rclone` 存在 [问题](https://rclone.org/s3/#key-management-system-kms)，如果使用 Amazon S3 存储备份，并且 Amazon S3 开启了 `AWS-KMS` 加密，需要在本节示例中的 yaml 文件里添加如下 `spec.s3.options` 配置以保证备份成功：
>
> ```yaml
> spec:
>   ...
>   s3:
>     ...
>     options:
>     - --ignore-checksum
> ```

+ 创建 `Backup` CR，通过 AccessKey 和 SecretKey 授权的方式将数据备份到 Amazon S3：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-s3.yaml
    ```

    `backup-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        secretName: s3-secret
        region: ${region}
        bucket: ${bucket}
        # prefix: ${prefix}
        # storageClass: STANDARD_IA
        # acl: private
        # endpoint:
    # dumpling:
    #  options:
    #  - --threads=16
    #  - --rows=10000
    #  tableFilter:
    #  - "test.*"
      # storageClassName: local-storage
      storageSize: 10Gi
    ```

+ 创建 `Backup` CR，通过 AccessKey 和 SecretKey 授权的方式将数据备份到 Ceph：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-s3.yaml
    ```

    `backup-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: demo1-backup-s3
      namespace: test1
    spec:
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      s3:
        provider: ceph
        secretName: s3-secret
        endpoint: ${endpoint}
        # prefix: ${prefix}
        bucket: ${bucket}
    # dumpling:
    #  options:
    #  - --threads=16
    #  - --rows=10000
    #  tableFilter:
    #  - "test.*"
      # storageClassName: local-storage
      storageSize: 10Gi
    ```

+ 创建 `Backup` CR，通过 IAM 绑定 Pod 授权的方式将数据备份到 Amazon S3：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-s3.yaml
    ```

    `backup-s3.yaml` 文件内容如下：

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
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        region: ${region}
        bucket: ${bucket}
        # prefix: ${prefix}
        # storageClass: STANDARD_IA
        # acl: private
        # endpoint:
    # dumpling:
    #  options:
    #  - --threads=16
    #  - --rows=10000
    #  tableFilter:
    #  - "test.*"
      # storageClassName: local-storage
      storageSize: 10Gi
    ```

+ 创建 `Backup` CR，通过 IAM 绑定 ServiceAccount 授权的方式将数据备份到 Amazon S3：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-s3.yaml
    ```

    `backup-s3.yaml` 文件内容如下：

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
      from:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        region: ${region}
        bucket: ${bucket}
        # prefix: ${prefix}
        # storageClass: STANDARD_IA
        # acl: private
        # endpoint:
    # dumpling:
    #  options:
    #  - --threads=16
    #  - --rows=10000
    #  tableFilter:
    #  - "test.*"
      # storageClassName: local-storage
      storageSize: 10Gi
    ```

上述示例将 TiDB 集群的数据全量导出备份到 Amazon S3 和 Ceph 上。Amazon S3 的 `acl`、`endpoint`、`storageClass` 配置项均可以省略。其余非 Amazon S3 的但是兼容 S3 的存储均可使用和 Amazon S3 类似的配置。可参考上面例子中 Ceph 的配置，省略不需要配置的字段。

Amazon S3 支持以下几种 access-control list (ACL) 策略：

* `private`
* `public-read`
* `public-read-write`
* `authenticated-read`
* `bucket-owner-read`
* `bucket-owner-full-control`

如果不设置 ACL 策略，则默认使用 `private` 策略。这几种访问控制策略的详细介绍参考 [AWS 官方文档](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html)。

Amazon S3 支持以下几种 `storageClass` 类型：

* `STANDARD`
* `REDUCED_REDUNDANCY`
* `STANDARD_IA`
* `ONEZONE_IA`
* `GLACIER`
* `DEEP_ARCHIVE`

如果不设置 `storageClass`，则默认使用 `STANDARD_IA`。这几种存储类型的详细介绍参考 [AWS 官方文档](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html)。

创建好 `Backup` CR 后，可通过如下命令查看备份状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -n test1 -owide
```

以上配置项中，`.spec.dumpling` 指定 Dumpling 相关的配置，可以在 `options` 字段指定 Dumpling 的运行参数，详情见 [Dumpling 使用文档](https://docs.pingcap.com/zh/tidb/dev/dumpling-overview#dumpling-主要参数表)；默认情况下该字段可以不用配置。当不指定 Dumpling 的配置时，`options` 字段的默认值如下：

```
options:
- --threads=16
- --rows=10000
```

兼容 S3 的存储相关配置参考 [S3 存储字段介绍](backup-restore-overview.md#s3-存储字段介绍)，更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

### 定时全量备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。下面是创建定时全量备份的具体步骤：

#### 定时全量备份环境准备

同 [Ad-hoc 全量备份到 S3 环境准备](#ad-hoc-全量备份到-s3-环境准备)。

#### 定时全量备份到 S3 兼容存储

> **注意：**
>
> 由于 `rclone` 存在[问题](https://rclone.org/s3/#key-management-system-kms)，如果使用 Amazon S3 存储备份，并且 Amazon S3 开启了 `AWS-KMS` 加密，需要在本节示例中的 yaml 文件里添加如下 `spec.backupTemplate.s3.options` 配置以保证备份成功：
>
> ```yaml
> spec:
>   ...
>   backupTemplate:
>     ...
>     s3:
>       ...
>       options:
>       - --ignore-checksum
> ```

+ 创建 `BackupSchedule` CR 开启 TiDB 集群的定时全量备份，通过 AccessKey 和 SecretKey 授权的方式将数据备份到 Amazon S3：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    `backup-schedule-s3.yaml` 文件内容如下：

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
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        s3:
          provider: aws
          secretName: s3-secret
          region: ${region}
          bucket: ${bucket}
          # prefix: ${prefix}
          # storageClass: STANDARD_IA
          # acl: private
          # endpoint:
      # dumpling:
      #  options:
      #  - --threads=16
      #  - --rows=10000
      #  tableFilter:
      #  - "test.*"
        # storageClassName: local-storage
        storageSize: 10Gi
    ```

+ 创建 `BackupSchedule` CR 开启 TiDB 集群的定时全量备份，通过 AccessKey 和 SecretKey 授权的方式将数据备份到 Ceph：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    `backup-schedule-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: BackupSchedule
    metadata:
      name: demo1-backup-schedule-ceph
      namespace: test1
    spec:
      #maxBackups: 5
      #pause: true
      maxReservedTime: "3h"
      schedule: "*/2 * * * *"
      backupTemplate:
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        s3:
          provider: ceph
          secretName: s3-secret
          endpoint: ${endpoint}
          bucket: ${bucket}
          # prefix: ${prefix}
      # dumpling:
      #  options:
      #  - --threads=16
      #  - --rows=10000
      #  tableFilter:
      #  - "test.*"
        # storageClassName: local-storage
        storageSize: 10Gi
    ```

+ 创建 `BackupSchedule` CR 开启 TiDB 集群的定时全量备份，通过 IAM 绑定 Pod 授权的方式将数据备份到 Amazon S3：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    `backup-schedule-s3.yaml` 文件内容如下：

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
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        s3:
          provider: aws
          region: ${region}
          bucket: ${bucket}
          # prefix: ${prefix}
          # storageClass: STANDARD_IA
          # acl: private
          # endpoint:
      # dumpling:
      #  options:
      #  - --threads=16
      #  - --rows=10000
      #  tableFilter:
      #  - "test.*"
        # storageClassName: local-storage
        storageSize: 10Gi
    ```

+ 创建 `BackupSchedule` CR 开启 TiDB 集群的定时全量备份，通过 IAM 绑定 ServiceAccount 授权的方式将数据备份到 Amazon S3：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    `backup-schedule-s3.yaml` 文件内容如下：

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
        from:
          host: ${tidb_host}
          port: ${tidb_port}
          user: ${tidb_user}
          secretName: backup-demo1-tidb-secret
        s3:
          provider: aws
          region: ${region}
          bucket: ${bucket}
          # prefix: ${prefix}
          # storageClass: STANDARD_IA
          # acl: private
          # endpoint:
      # dumpling:
      #  options:
      #  - --threads=16
      #  - --rows=10000
      #  tableFilter:
      #  - "test.*"
        # storageClassName: local-storage
        storageSize: 10Gi
    ```

定时全量备份创建完成后，可以通过以下命令查看定时全量备份的状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bks -n test1 -owide
```

查看定时全量备份下面所有的备份条目：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-s3 -n test1
```

从以上示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定 S3 兼容存储相关的配置，该配置与 Ad-hoc 全量备份到兼容 S3 的存储配置完全一样，可参考[备份数据到兼容 S3 的存储](#备份数据到兼容-s3-的存储)。`backupSchedule` 独有的配置项可参考 [BackupSchedule CR 字段介绍](backup-restore-overview.md#backupschedule-cr-字段介绍)。

> **注意：**
>
> TiDB Operator 会创建一个 PVC，这个 PVC 同时用于 Ad-hoc 全量备份和定时全量备份，备份数据会先存储到 PV，然后再上传到远端存储。如果备份完成后想要删掉这个 PVC，可以参考[删除资源](cheat-sheet.md#删除资源)先把备份 Pod 删掉，然后再把 PVC 删掉。
>
> 假如备份并上传到远端存储成功，TiDB Operator 会自动删除本地的备份文件。如果上传失败，则本地备份文件将被保留。

### 删除备份的 backup CR

删除备份的 backup CR 可参考 [删除备份的 backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 使用 TiDB Lightning 恢复兼容 S3 的存储上的备份数据

以下示例使用 TiDB Lightning 将兼容 S3 的存储（指定路径）上的备份数据恢复到 TiDB 集群，底层通过使用 [TiDB Lightning](https://pingcap.com/docs/stable/how-to/get-started/tidb-lightning/#tidb-lightning-tutorial) 来进行集群恢复。

### 环境准备

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 存储访问授权

    如果使用 Amazon S3 来恢复集群，可以使用三种权限授予方式授予权限，参考 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权) 授权访问兼容 S3 的远程存储；使用 Ceph 作为后端存储测试恢复时，是通过 AccessKey 和 SecretKey 模式授权，设置方式可参考 [通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-accesskey-和-secretkey-授权)。

3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的用户所对应的密码。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

### 数据库账户权限

| 权限 | 作用域 |
|:----|:------|
| SELECT | Tables |
| INSERT | Tables |
| UPDATE | Tables |
| DELETE | Tables |
| CREATE | Databases, tables |
| DROP | Databases, tables |
| ALTER | Tables |

### 将指定备份数据恢复到 TiDB 集群

> **注意：**
>
> 由于 `rclone` 存在[问题](https://rclone.org/s3/#key-management-system-kms)，如果使用 Amazon S3 存储备份，并且 Amazon S3 开启了 `AWS-KMS` 加密，需要在本节示例中的 yaml 文件里添加如下 `spec.s3.options` 配置以保证备份恢复成功：
>
> ```yaml
> spec:
>   ...
>   s3:
>     ...
>     options:
>     - --ignore-checksum
> ```

1. 创建 Restore customer resource (CR)，将制定备份数据恢复至 TiDB 集群

    + 创建 Restore custom resource (CR)，通过 AccessKey 和 SecretKey 授权的方式将指定的备份数据由 Ceph 恢复至 TiDB 集群：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl apply -f restore.yaml
        ```

        `restore.yaml` 文件内容如下：

        ```yaml
        ---
        apiVersion: pingcap.com/v1alpha1
        kind: Restore
        metadata:
          name: demo2-restore
          namespace: test2
        spec:
          backupType: full
          to:
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: ceph
            endpoint: ${endpoint}
            secretName: s3-secret
            path: s3://${backup_path}
          # storageClassName: local-storage
          storageSize: 1Gi
        ```

    + 创建 Restore custom resource (CR)，通过 AccessKey 和 SecretKey 授权的方式将指定的备份数据由 Amazon S3 恢复至 TiDB 集群：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl apply -f restore.yaml
        ```

        `restore.yaml` 文件内容如下：

        ```yaml
        ---
        apiVersion: pingcap.com/v1alpha1
        kind: Restore
        metadata:
          name: demo2-restore
          namespace: test2
        spec:
          backupType: full
          to:
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: aws
            region: ${region}
            secretName: s3-secret
            path: s3://${backup_path}
          # storageClassName: local-storage
          storageSize: 1Gi
        ```

    + 创建 Restore custom resource (CR)，通过 IAM 绑定 Pod 授权的方式将指定的备份数据恢复至 TiDB 集群：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl apply -f restore.yaml
        ```

        `restore.yaml` 文件内容如下：

        ```yaml
        ---
        apiVersion: pingcap.com/v1alpha1
        kind: Restore
        metadata:
          name: demo2-restore
          namespace: test2
          annotations:
            iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
        spec:
          backupType: full
          to:
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: aws
            region: ${region}
            path: s3://${backup_path}
          # storageClassName: local-storage
          storageSize: 1Gi
        ```

    + 创建 Restore custom resource (CR)，通过 IAM 绑定 ServiceAccount 授权的方式将指定的备份数据恢复至 TiDB 集群：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl apply -f restore.yaml
        ```

        `restore.yaml` 文件内容如下：

        ```yaml
        ---
        apiVersion: pingcap.com/v1alpha1
        kind: Restore
        metadata:
          name: demo2-restore
          namespace: test2
        spec:
          backupType: full
          serviceAccount: tidb-backup-manager
          to:
            host: ${tidb_host}
            port: ${tidb_port}
            user: ${tidb_user}
            secretName: restore-demo2-tidb-secret
          s3:
            provider: aws
            region: ${region}
            path: s3://${backup_path}
          # storageClassName: local-storage
          storageSize: 1Gi
        ```

2. 创建好 `Restore` CR 后，可通过以下命令查看恢复的状态：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get rt -n test2 -owide
    ```

以上示例将兼容 S3 的存储（`spec.s3.path` 路径下）中的备份数据恢复到 TiDB 集群 (`spec.to.host`)。有关兼容 S3 的存储的配置项，可以参考 [备份数据到兼容 S3 的存储](#备份数据到兼容-s3-的存储)。

兼容 S3 的存储相关配置参考 [S3 存储字段介绍](backup-restore-overview.md#s3-存储字段介绍)，更多 `Restore` CR 字段的详细解释参考 [Restore CR 字段介绍](backup-restore-overview.md#restore-cr-字段介绍)。

> **注意：**
>
> TiDB Operator 会创建一个 PVC，用于数据恢复，备份数据会先从远端存储下载到 PV，然后再进行恢复。如果恢复完成后想要删掉这个 PVC，可以参考[删除资源](cheat-sheet.md#删除资源)先把恢复 Pod 删掉，然后再把 PVC 删掉。

## 使用 BR 备份 TiDB 集群到兼容 S3 的存储

以下示例将使用 BR 备份 TiDB 集群数据到兼容 S3 的存储。[`BR`](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 会在底层获取集群的逻辑备份，然后再将备份数据上传到远程存储。

### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：备份前后，backup CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

### Ad-hoc 备份

Ad-hoc 备份支持全量备份与增量备份。Ad-hoc 备份通过创建一个自定义的 `Backup` Custom Resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

目前 Ad-hoc 备份已经兼容以上三种授权模式，本文档提供如下备份示例。示例假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

#### Ad-hoc 备份到 S3 环境准备

> **注意：**
>
> 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，可以省略以下创建 `backup-demo1-tidb-secret` secret 的步骤，并且不需要在 Backup CR 中配置 `spec. tikvGCLifeTime` 和 `spec.from` 字段。

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 存储访问授权

    如果使用 Amazon S3 来备份集群，可以使用三种权限授予方式授予权限，参考 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权) 授权访问兼容 S3 的远程存储。使用 Ceph 作为后端存储测试备份时，是通过 AccessKey 和 SecretKey 模式授权，设置方式可参考 [通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-accesskey-和-secretkey-授权)。

3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的用户所对应的密码。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

#### 使用 BR 备份数据到 Amazon S3 的存储

+ 创建 `Backup` CR，通过 accessKey 和 secretKey 授权的方式备份集群:

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
      # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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

+ 创建 `Backup` CR，通过 IAM 绑定 Pod 授权的方式备份集群:

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
      # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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

+ 创建 `Backup` CR，通过 IAM 绑定 ServiceAccount 授权的方式备份集群:

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
      # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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

以上三个示例分别使用三种授权模式将数据导出到 Amazon S3 存储上。Amazon S3 的 `acl`、`endpoint`、`storageClass` 配置项均可以省略。

Amazon S3 支持以下几种 access-control list (ACL) 策略：

* `private`
* `public-read`
* `public-read-write`
* `authenticated-read`
* `bucket-owner-read`
* `bucket-owner-full-control`

如果不设置 ACL 策略，则默认使用 `private` 策略。这几种访问控制策略的详细介绍参考 [AWS 官方文档](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html)。

Amazon S3 支持以下几种 `storageClass` 类型：

* `STANDARD`
* `REDUCED_REDUNDANCY`
* `STANDARD_IA`
* `ONEZONE_IA`
* `GLACIER`
* `DEEP_ARCHIVE`

如果不设置 `storageClass`，则默认使用 `STANDARD_IA`。这几种存储类型的详细介绍参考 [AWS 官方文档](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html)。

创建好 `Backup` CR 后，可通过如下命令查看备份状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -n test1 -o wide
```

> **注意：**
>
> 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, 并且使用 BR 备份恢复。BR 会自动调整 `tikv_gc_life_time` 参数，无需配置 `spec.tikvGCLifeTime`.

以上示例中，`.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释参考 `Backup` CR 中的 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。

自 v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考 [使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。

兼容 S3 的存储相关配置参考 [S3 存储字段介绍](backup-restore-overview.md#s3-存储字段介绍)，更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

### 定时全量备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。下面是创建定时全量备份的具体步骤：

#### 定时全量备份环境准备

同 [Ad-hoc 备份环境准备](#ad-hoc-备份到-s3-环境准备)。

#### 使用 BR 定时备份数据到 S3 兼容存储

+ 创建 `BackupSchedule` CR，开启 TiDB 集群定时全量备份，通过 accessKey 和 secretKey 授权的方式备份集群：

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
        # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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

+ 创建 `BackupSchedule` CR，开启 TiDB 集群定时全量备份，通过 IAM 绑定 Pod 授权的方式备份集群：

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
        # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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

+ 创建 `BackupSchedule` CR，开启 TiDB 集群定时全量备份， 通过 IAM 绑定 ServiceAccount 授权的方式备份集群：

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
        # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
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

从以上两个示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定 S3 兼容存储相关的配置，该配置与 Ad-hoc 备份到兼容 S3 的存储配置完全一样，可参考[使用 BR 备份数据到 Amazon S3 的存储](#使用-br-备份数据到-amazon-s3-的存储)。`backupSchedule` 独有的配置项可参考 [BackupSchedule CR 字段介绍](backup-restore-overview.md#backupschedule-cr-字段介绍)。

### 删除备份的 backup CR

删除备份的 backup CR 可参考 [删除备份的 backup CR](backup-restore-overview.md#删除备份的-backup-cr)。

## 使用 BR 恢复兼容 S3 的存储上的备份数据

以下示例将兼容 S3 的存储（指定路径）上的备份数据恢复到 TiDB 集群，底层通过使用 [`BR`](https://docs.pingcap.com/zh/tidb/dev/backup-and-restore-tool) 来进行集群恢复。

### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：恢复前后，restore CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

### 环境准备

> **注意：**
>
> 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，以下创建 `backup-demo1-tidb-secret` secret 的步骤可以省略。

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test2` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 存储访问授权

    如果使用 Amazon S3 来恢复集群，可以使用三种权限授予方式授予权限，参考 [AWS 账号授权](grant-permissions-to-remote-storage.md#aws-账号授权) 授权访问兼容 S3 的远程存储。使用 Ceph 作为后端存储测试恢复时，是通过 AccessKey 和 SecretKey 模式授权，设置方式可参考 [通过 AccessKey 和 SecretKey 授权](grant-permissions-to-remote-storage.md#通过-accesskey-和-secretkey-授权)。

3. 创建 `restore-demo2-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的 root 账号和密钥。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic restore-demo2-tidb-secret --from-literal=password=${password} --namespace=test2
    ```

### 将指定备份数据恢复到 TiDB 集群

+ 创建 `Restore` CR，通过 accessKey 和 secretKey 授权的方式恢复集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f resotre-aws-s3.yaml
    ```

    `restore-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
    spec:
      br:
        cluster: demo2
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
        # sendCredToTikv: true
      # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 创建 `Restore` CR，通过 IAM 绑定 Pod 授权的方式备份集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    `restore-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
      annotations:
        iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    spec:
      br:
        cluster: demo2
        sendCredToTikv: false
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

+ 创建 `Restore` CR，通过 IAM 绑定 ServiceAccount 授权的方式备份集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f restore-aws-s3.yaml
    ```

    `restore-aws-s3.yaml` 文件内容如下：

    ```yaml
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: demo2-restore-s3
      namespace: test2
    spec:
      serviceAccount: tidb-backup-manager
      br:
        cluster: demo2
        sendCredToTikv: false
        clusterNamespace: test2
        # logLevel: info
        # statusAddr: ${status_addr}
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: ${time}
        # checksum: true
      # Only needed for TiDB Operator < v1.1.7 or TiDB < v4.0.8
      to:
        host: ${tidb_host}
        port: ${tidb_port}
        user: ${tidb_user}
        secretName: restore-demo2-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

创建好 `Restore` CR 后，可通过以下命令查看恢复的状态：

{{< copyable "shell-regular" >}}

```shell
kubectl get rt -n test2 -o wide
```

> **注意：**
>
> 如果使用 TiDB Operator >= v1.1.7 && TiDB >= v4.0.8, BR 会自动调整 `tikv_gc_life_time` 参数，无需配置 `spec.to`.

以上示例中，`.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。更多 `.spec.br` 字段的详细解释参考 `Backup` CR 中的 [BR 字段介绍](backup-restore-overview.md#br-字段介绍)。

兼容 S3 的存储相关配置参考 [S3 存储字段介绍](backup-restore-overview.md#s3-存储字段介绍)，更多 `Backup` CR 字段的详细解释参考 [Backup CR 字段介绍](backup-restore-overview.md#backup-cr-字段介绍)。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。