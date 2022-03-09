---
title: 备份与恢复 CR 介绍
summary: 介绍用于备份与恢复的 Custom Resource (CR) 资源的各字段。
---

# 备份与恢复 CR 介绍

本文档介绍用于备份与恢复的 `Backup`、`Restore` 及 `BackupSchedule` Custom Resource (CR) 资源的各字段，确保更好地对 Kubernetes 上的 TiDB 集群进行数据备份和数据恢复。

## Backup CR 字段介绍

为了对 Kubernetes 上的 TiDB 集群进行数据备份，用户可以通过创建一个自定义的 `Backup` CR 对象来描述一次备份，具体备份过程可参考[数据备份](backup-restore-overview.md#数据备份)中列出的文档。以下介绍 Backup CR 各个字段的具体含义。

### 通用字段介绍

* `.spec.metadata.namespace`：`Backup` CR 所在的 namespace。
* `.spec.toolImage`：用于指定 `Backup` 使用的工具镜像。TiDB Operator 从 v1.1.9 起支持这项配置。

    - 使用 BR 备份时，可以用该字段指定 BR 的版本:
        - 如果未指定或者为空，默认使用镜像 `pingcap/br:${tikv_version}` 进行备份。
        - 如果指定了 BR 的版本，例如 `.spec.toolImage: pingcap/br:v5.3.0`，那么使用指定的版本镜像进行备份。
        - 如果指定了镜像但未指定版本，例如 `.spec.toolImage: private/registry/br`，那么使用镜像 `private/registry/br:${tikv_version}` 进行备份。
    - 使用 Dumpling 备份时，可以用该字段指定 Dumpling 的版本：
        - 如果指定了 Dumpling 的版本，例如 `spec.toolImage: pingcap/dumpling:v5.3.0`，那么使用指定的版本镜像进行备份。
        - 如果未指定，默认使用 [Backup Manager Dockerfile](https://github.com/pingcap/tidb-operator/blob/master/images/tidb-backup-manager/Dockerfile) 文件中 `TOOLKIT_VERSION` 指定的 Dumpling 版本进行备份。

* `.spec.backupType`：指定 Backup 类型，目前支持以下三种类型：
    * `full`：对 TiDB 集群所有的 database 数据执行备份。
    * `db`：对 TiDB 集群一个 database 的数据执行备份。
    * `table`：对 TiDB 集群一张表的数据执行备份。

* `.spec.tikvGCLifeTime`：备份中的临时 `tikv_gc_life_time` 时间设置，默认为 72h。

    在备份开始之前，若 TiDB 集群的 `tikv_gc_life_time` 小于用户设置的 `spec.tikvGCLifeTime`，为了保证备份的数据不被 TiKV GC 掉，TiDB Operator 会在备份前[调节 `tikv_gc_life_time`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview#导出大规模数据时的-tidb-gc-设置) 为 `spec.tikvGCLifeTime`。

    备份结束后，不论成功或者失败，如果旧的 `tikv_gc_life_time` 小于设置的 `.spec.tikvGCLifeTime`，TiDB Operator 会尝试恢复 `tikv_gc_life_time` 为备份前的旧值。在极端情况下，如果 TiDB Operator 访问数据库失败，TiDB Operator 将无法自动恢复 `tikv_gc_life_time` 并认为备份失败。

    此时，可以通过下述语句查看当前 TiDB 集群的 `tikv_gc_life_time`：

    ```sql
    select VARIABLE_NAME, VARIABLE_VALUE from mysql.tidb where VARIABLE_NAME like "tikv_gc_life_time";
    ```

    如果发现 `tikv_gc_life_time` 值过大（通常为 10m），则需要按照[调节 `tikv_gc_life_time`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview#导出大规模数据时的-tidb-gc-设置) 将 `tikv_gc_life_time` 调回原样。

* `.spec.cleanPolicy`：备份集群后删除 Backup CR 时的备份文件清理策略。目前支持三种清理策略：

    * `Retain`：任何情况下，删除 Backup CR 时会保留备份出的文件。
    * `Delete`：任何情况下，删除 Backup CR 时会删除备份出的文件。
    * `OnFailure`：如果备份中失败，删除 Backup CR 时会删除备份出的文件。

    如果不配置该字段，或者配置该字段的值为上述三种以外的值，均会保留备份出的文件。值得注意的是，在 v1.1.2 以及之前版本不存在该字段，且默认在删除 CR 的同时删除备份的文件。若 v1.1.3 及之后版本的用户希望保持该行为，需要设置该字段为 `Delete`。
* `.spec.cleanOption`：备份集群后删除 Backup CR 时的备份文件清理行为, 在 v1.2.4 及之后版本可以使用，更多说明请参阅[清理备份文件](backup-restore-overview.md#清理备份文件)
* `.spec.from.host`：待备份 TiDB 集群的访问地址，为需要导出的 TiDB 的 service name，例如 `basic-tidb`。
* `.spec.from.port`：待备份 TiDB 集群的访问端口。
* `.spec.from.user`：待备份 TiDB 集群的访问用户。
* `.spec.from.secretName`：存储 `.spec.from.user` 用户的密码的 Secret。
* `.spec.from.tlsClientSecretName`：指定备份使用的存储证书的 Secret。

    如果 TiDB 集群开启了 [TLS](enable-tls-between-components.md)，但是不想使用[文档](enable-tls-between-components.md)中创建的 `${cluster_name}-cluster-client-secret` 进行备份，可以通过这个参数为备份指定一个 Secret，可以通过如下命令生成：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${namespace} --from-file=tls.crt=${cert_path} --from-file=tls.key=${key_path} --from-file=ca.crt=${ca_path}
    ```

* `.spec.storageClassName`：备份时所需的 persistent volume (PV) 类型。
* `.spec.storageSize`：备份时指定所需的 PV 大小，默认为 100 GiB。该值应大于备份 TiDB 集群数据的大小。一个 TiDB 集群的 Backup CR 对应的 PVC 名字是确定的，如果集群命名空间中已存在该 PVC 并且其大小小于 `.spec.storageSize`，这时需要先删除该 PVC 再运行 Backup job。
* `.spec.resources`：指定运行备份任务的 Pod 的资源请求与上限值。
* `.spec.env`：指定运行备份任务的 Pod 的环境变量信息。
* `.spec.affinity`：指定运行备份任务的 Pod 亲和性配置，关于 affinity 的使用说明，请参阅 [Affinity & AntiAffinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)。
* `.spec.tolerations`：指定运行备份任务的 Pod 能够调度到带有与之匹配的[污点](https://kubernetes.io/docs/reference/glossary/?all=true#term-taint) (Taint) 的节点上。关于污点与容忍度的更多说明，请参阅 [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)。
* `.spec.podSecurityContext`：指定运行备份任务的 Pod 的安全上下文配置，允许 Pod 以非 root 用户的方式运行，关于 podSecurityContext 的更多说明，请参阅[以非 root 用户运行容器](containers-run-as-non-root-user.md)。
* `.spec.priorityClassName`：指定运行备份任务的 Pod 的 priorityClass 的名称，以设置运行优先级，关于 priorityClass 的更多说明，请参阅 [Pod Priority and Preemption](https://kubernetes.io/zh/docs/concepts/scheduling-eviction/pod-priority-preemption/)。
* `.spec.imagePullSecrets`：指定运行备份任务的 Pod 的 [imagePullSecrets](https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod)
* `.spec.serviceAccount`：备份时指定所使用的 ServiceAccount 名称。
* `.spec.useKMS`：备份时指定是否使用 AWS-KMS 解密备份使用的 S3 存储密钥。
* `.spec.tableFilter`：备份时指定让 Dumpling 或者 BR 备份符合 [table-filter 规则](https://docs.pingcap.com/zh/tidb/stable/table-filter/)的表。默认情况下该字段可以不用配置。

    当不配置时，如果使用 Dumpling 备份，`tableFilter` 字段的默认值如下：

    ```bash
    tableFilter:
    - "*.*"
    - "!/^(mysql|test|INFORMATION_SCHEMA|PERFORMANCE_SCHEMA|METRICS_SCHEMA|INSPECTION_SCHEMA)$/.*"
    ```

    当不配置时，如果使用 BR 备份，BR 会备份除系统库以外的所有数据库。

    > **注意：**
    >
    > 如果要使用排除规则 `"!db.table"` 导出除 `db.table` 的所有表，那么在 `"!db.table"` 前必须先添加 `*.*` 规则。如下面例子所示：
    >
    > ```
    > tableFilter:
    > - "*.*"
    > - "!db.table"
    > ```

### BR 字段介绍

* `.spec.br.cluster`：代表需要备份的集群名字。
* `.spec.br.clusterNamespace`：代表需要备份的集群所在的 `namespace`。
* `.spec.br.logLevel`：代表日志的级别。默认为 `info`。
* `.spec.br.statusAddr`：为 BR 进程监听一个进程状态的 HTTP 端口，方便用户调试。如果不填，则默认不监听。
* `.spec.br.concurrency`：备份时每一个 TiKV 进程使用的线程数。备份时默认为 4，恢复时默认为 128。
* `.spec.br.rateLimit`：是否对流量进行限制。单位为 MB/s，例如设置为 `4` 代表限速 4 MB/s，默认不限速。
* `.spec.br.checksum`：是否在备份结束之后对文件进行验证。默认为 `true`。
* `.spec.br.timeAgo`：备份 timeAgo 以前的数据，默认为空（备份当前数据），[支持](https://golang.org/pkg/time/#ParseDuration) "1.5h"，"2h45m" 等数据。
* `.spec.br.sendCredToTikv`：BR 进程是否将自己的 AWS 权限 或者 GCP 权限传输给 TiKV 进程。默认为 `true`。
* `.spec.br.onLine`：restore 时是否启用[在线恢复功能](https://docs.pingcap.com/zh/tidb/stable/use-br-command-line-tool#在线恢复实验性功能)。
* `.spec.br.options`：BR 工具支持的额外参数，需要以字符串数组的形式传入。自 v1.1.6 版本起支持该参数。可用于指定 `lastbackupts` 以进行增量备份。

### S3 存储字段介绍

* `.spec.s3.provider`：支持的兼容 S3 的 `provider`。

    更多支持的兼容 S3 的 `provider` 如下：

    * `alibaba`：Alibaba Cloud Object Storage System (OSS)，formerly Aliyun
    * `digitalocean`：Digital Ocean Spaces
    * `dreamhost`：Dreamhost DreamObjects
    * `ibmcos`：IBM COS S3
    * `minio`：Minio Object Storage
    * `netease`：Netease Object Storage (NOS)
    * `wasabi`：Wasabi Object Storage
    * `other`：Any other S3 compatible provider

* `.spec.s3.region`：使用 Amazon S3 存储备份，需要配置 Amazon S3 所在的 region。
* `.spec.s3.bucket`：兼容 S3 存储的 bucket 名字。
* `.spec.s3.prefix`：如果设置了这个字段，则会使用这个字段来拼接在远端存储的存储路径 `s3://${.spec.s3.bucket}/${.spec.s3.prefix}/backupName`。
* `.spec.s3.path`：指定备份文件在远端存储的存储路径，例如 `s3://test1-demo1/backup-2019-12-11T04:32:12Z.tgz`。
* `.spec.s3.endpoint`：兼容 S3 的存储服务 endpoint，例如 `http://minio.minio.svc.cluster.local:9000`。
* `.spec.s3.secretName`：访问兼容 S3 存储的密钥信息（包含 access key 和 secret key）的 Secret 名称。
* `.spec.s3.sse`：指定 S3 的服务端加密方式，例如 `aws:kms`。
* `.spec.s3.acl`：支持的 access-control list (ACL) 策略。

    Amazon S3 支持以下几种 access-control list (ACL) 策略：

    * `private`
    * `public-read`
    * `public-read-write`
    * `authenticated-read`
    * `bucket-owner-read`
    * `bucket-owner-full-control`

    如果不设置 ACL 策略，则默认使用 `private` 策略。ACL 策略的详细介绍，参考 [AWS 官方文档](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html)。

* `.spec.s3.storageClass`：支持的 `storageClass` 类型。

    Amazon S3 支持以下几种 `storageClass` 类型：

    * `STANDARD`
    * `REDUCED_REDUNDANCY`
    * `STANDARD_IA`
    * `ONEZONE_IA`
    * `GLACIER`
    * `DEEP_ARCHIVE`

    如果不设置 `storageClass`，则默认使用 `STANDARD_IA`。`storageClass` 的详细介绍，参考 [AWS 官方文档](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html)。

### GCS 存储字段介绍

* `.spec.gcs.projectId`：代表 GCP 上用户项目的唯一标识。具体获取该标识的方法可参考 [GCP 官方文档](https://cloud.google.com/resource-manager/docs/creating-managing-projects)。
* `.spec.gcs.location`：指定 GCS bucket 所在的区域，例如 `us-west2`。
* `.spec.gcs.path`：指定备份文件在远端存储的存储路径，例如 `gcs://test1-demo1/backup-2019-11-11T16:06:05Z.tgz`。
* `.spec.gcs.secretName`：指定存储 GCS 用户账号认证信息的 Secret 名称。
* `.spec.gcs.bucket`：存储数据的 bucket 名字。
* `.spec.gcs.prefix`：如果设置了这个字段，则会使用这个字段来拼接在远端存储的存储路径 `gcs://${.spec.gcs.bucket}/${.spec.gcs.prefix}/backupName`。
* `.spec.gcs.storageClass`：GCS 支持以下几种 `storageClass` 类型：

    * `MULTI_REGIONAL`
    * `REGIONAL`
    * `NEARLINE`
    * `COLDLINE`
    * `DURABLE_REDUCED_AVAILABILITY`

    如果不设置 `storageClass`，则默认使用 `COLDLINE`。这几种存储类型的详细介绍可参考 [GCS 官方文档](https://cloud.google.com/storage/docs/storage-classes)。

* `.spec.gcs.objectAcl`：设置 object access-control list (ACL) 策略。

    GCS 支持以下几种 ACL 策略：

    * `authenticatedRead`
    * `bucketOwnerFullControl`
    * `bucketOwnerRead`
    * `private`
    * `projectPrivate`
    * `publicRead`

    如果不设置 object ACL 策略，则默认使用 `private` 策略。ACL 策略的详细介绍，参考 [GCS 官方文档](https://cloud.google.com/storage/docs/access-control/lists)。

* `.spec.gcs.bucketAcl`：设置 bucket access-control list (ACL) 策略。

    GCS 支持以下几种 bucket ACL 策略：

    * `authenticatedRead`
    * `private`
    * `projectPrivate`
    * `publicRead`
    * `publicReadWrite`

    如果不设置 bucket ACL 策略，则默认策略为 `private`。ACL 策略的详细介绍，参考 [GCS 官方文档](https://cloud.google.com/storage/docs/access-control/lists)。

### Local 存储字段介绍

* `.spec.local.prefix`：持久卷存储目录。如果设置了这个字段，则会使用这个字段来拼接在持久卷的存储路径 `local://${.spec.local.volumeMount.mountPath}/${.spec.local.prefix}/`。
* `.spec.local.volume`：持久卷配置。
* `.spec.local.volumeMount`：持久卷挂载配置。

## Restore CR 字段介绍

为了对 Kubernetes 上的 TiDB 集群进行数据恢复，用户可以通过创建一个自定义的 `Restore` CR 对象来描述一次恢复，具体恢复过程可参考[备份与恢复简介](backup-restore-overview.md#数据恢复)中列出的文档。以下介绍 Restore CR 各个字段的具体含义。

* `.spec.metadata.namespace`：`Restore` CR 所在的 namespace。
* `.spec.backupType`：指定 Restore 类型，目前支持以下三种类型：
    * `full`：对 TiDB 集群所有的 database 数据执行备份。
    * `db`：对 TiDB 集群一个 database 的数据执行备份。
    * `table`：对 TiDB 集群一张表的数据执行备份。

* `.spec.toolImage`：用于指定 `Restore` 使用的工具镜像。TiDB Operator 从 v1.1.9 版本起支持这项配置。
    - 使用 BR 恢复时，可以用该字段指定 BR 的版本。例如，`spec.toolImage: pingcap/br:v5.3.0`。如果不指定，默认使用 `pingcap/br:${tikv_version}` 进行恢复。
    - 使用 Lightning 恢复时，可以用该字段指定 Lightning 的版本，例如`spec.toolImage: pingcap/lightning:v5.3.0`。如果不指定，默认使用 [Backup Manager Dockerfile](https://github.com/pingcap/tidb-operator/blob/master/images/tidb-backup-manager/Dockerfile) 文件中 `TOOLKIT_VERSION` 指定的 Lightning 版本进行恢复。
* `.spec.to.host`：待恢复 TiDB 集群的访问地址。
* `.spec.to.port`：待恢复 TiDB 集群的访问端口。
* `.spec.to.user`：待恢复 TiDB 集群的访问用户。
* `.spec.to.secretName`：存储 `.spec.to.user` 用户的密码的 secret。
* `.spec.to.tlsClientSecretName`：指定恢复备份使用的存储证书的 Secret。

    如果 TiDB 集群开启了 [TLS](enable-tls-between-components.md)，但是不想使用[文档](enable-tls-between-components.md)中创建的 `${cluster_name}-cluster-client-secret` 恢复备份，可以通过这个参数为恢复备份指定一个 Secret，可以通过如下命令生成：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${namespace} --from-file=tls.crt=${cert_path} --from-file=tls.key=${key_path} --from-file=ca.crt=${ca_path}
    ```

* `.spec.resources`：指定运行恢复任务的 Pod 的资源请求与上限值。
* `.spec.env`：指定运行恢复任务的 Pod 的环境变量信息。
* `.spec.affinity`：指定运行恢复任务的 Pod 亲和性配置，关于 affinity 的使用说明，请参阅 [Affinity & AntiAffinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)。
* `.spec.tolerations`：指定运行恢复任务的 Pod 能够调度到带有与之匹配的[污点](https://kubernetes.io/docs/reference/glossary/?all=true#term-taint) (Taint) 的节点上。关于污点与容忍度的更多说明，请参阅 [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)。
* `.spec.podSecurityContext`：指定运行恢复任务的 Pod 的安全上下文配置，允许 Pod 以非 root 用户的方式运行，关于 podSecurityContext 的更多说明，请参阅[以非 root 用户运行容器](containers-run-as-non-root-user.md)。
* `.spec.priorityClassName`：指定运行恢复任务的 Pod 的 priorityClass 的名称，以设置运行优先级，关于 priorityClass 的更多说明，请参阅 [Pod Priority and Preemption](https://kubernetes.io/zh/docs/concepts/scheduling-eviction/pod-priority-preemption/)。
* `.spec.imagePullSecrets`：指定运行恢复任务的 Pod 的 [imagePullSecrets](https://kubernetes.io/docs/concepts/containers/images/#specifying-imagepullsecrets-on-a-pod)
* `.spec.serviceAccount`：指定恢复时所使用的 ServiceAccount 名称。
* `.spec.useKMS`：指定恢复时是否使用 AWS-KMS 解密备份使用的 S3 存储密钥。
* `.spec.storageClassName`：指定恢复时所需的 PV 类型。
* `.spec.storageSize`：指定恢复集群时所需的 PV 大小。该值应大于 TiDB 集群备份的数据大小。
* `.spec.tableFilter`：恢复时指定让 BR 恢复符合 [table-filter 规则](https://docs.pingcap.com/zh/tidb/stable/table-filter/) 的表。默认情况下该字段可以不用配置。

    当不配置时，如果使用 TiDB Lightning 恢复，`tableFilter` 字段的默认值如下：

    ```bash
    tableFilter:
    - "*.*"
    - "!/^(mysql|test|INFORMATION_SCHEMA|PERFORMANCE_SCHEMA|METRICS_SCHEMA|INSPECTION_SCHEMA)$/.*"
    ```

    当不配置时，如果使用 BR 恢复，BR 会恢复备份文件中的所有数据库。

    > **注意：**
    >
    > 如果要使用排除规则 `"!db.table"` 导出除 `db.table` 的所有表，那么在 `"!db.table"` 前必须先添加 `*.*` 规则。如下面例子所示：
    >
    > ```
    > tableFilter:
    > - "*.*"
    > - "!db.table"
    > ```

* `.spec.br`：BR 相关配置，具体介绍参考 [BR 字段介绍](#br-字段介绍)。
* `.spec.s3`：S3 兼容存储相关配置，具体介绍参考 [S3 字段介绍](#s3-存储字段介绍)。
* `.spec.gcs`：GCS 存储相关配置，具体介绍参考 [GCS 字段介绍](#gcs-存储字段介绍)。
* `.spec.local`：持久卷存储相关配置，具体介绍参考 [Local 字段介绍](#local-存储字段介绍)。

## BackupSchedule CR 字段介绍

`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定集群及远程存储相关的配置，字段和 Backup CR 中的 `spec` 一样，详细介绍可参考 [Backup CR 字段介绍](#backup-cr-字段介绍)。下面介绍 `backupSchedule` 独有的配置项：

+ `.spec.maxBackups`：一种备份保留策略，决定定时备份最多可保留的备份个数。超过该数目，就会将过时的备份删除。如果将该项设置为 `0`，则表示保留所有备份。
+ `.spec.maxReservedTime`：一种备份保留策略，按时间保留备份。例如将该参数设置为 `24h`，表示只保留最近 24 小时内的备份条目。超过这个时间的备份都会被清除。时间设置格式参考 [`func ParseDuration`](https://golang.org/pkg/time/#ParseDuration)。如果同时设置 `.spec.maxBackups` 和 `.spec.maxReservedTime`，则以 `.spec.maxReservedTime` 为准。
+ `.spec.schedule`：Cron 的时间调度格式。具体格式可参考 [Cron](https://en.wikipedia.org/wiki/Cron)。
+ `.spec.pause`：是否暂停定时备份，默认为 `false`。如果将该值设置为 `true`，表示暂停定时备份，此时即使到了指定时间点，也不会进行备份。在定时备份暂停期间，备份 Garbage Collection (GC) 仍然正常进行。如需重新开启定时全量备份，将 `true` 改为 `false`。
