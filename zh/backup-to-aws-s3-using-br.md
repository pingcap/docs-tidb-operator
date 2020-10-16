---
title: 使用 BR 工具备份 TiDB 集群数据到兼容 S3 的存储
summary: 介绍如何使用 BR 工具备份 TiDB 集群数据到兼容 Amazon S3 的存储。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/backup-to-aws-s3-using-br/']
---

<!-- markdownlint-disable MD007 -->

# 使用 BR 工具备份 TiDB 集群数据到兼容 S3 的存储

本文详细描述了如何将运行在 AWS Kubernetes 环境中的 TiDB 集群数据备份到 AWS 的存储上。[`BR`](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool) 会在底层获取集群的逻辑备份，然后再将备份数据上传到 AWS 的存储上。

本文使用的备份方式基于 TiDB Operator v1.1 及以上版本的 Custom Resource Definition(CRD) 实现。

## AWS 账号权限授予的三种方式

在 AWS 云环境中，不同的类型的 Kubernetes 集群提供了不同的权限授予方式。本文测试了以下三种权限授予方式:

* 通过传入 AWS 账号的 AccessKey 和 SecretKey 进行授权:

    AWS 的客户端支持读取进程环境变量中的 `AWS_ACCESS_KEY_ID` 以及 `AWS_SECRET_ACCESS_KEY` 来获取与之相关联的用户或者角色的权限。

* 通过将 [IAM](https://aws.amazon.com/cn/iam/) 绑定 Pod 进行授权:

    通过将用户的 IAM 角色与所运行的 Pod 资源进行绑定，使 Pod 中运行的进程获得角色所拥有的权限，这种授权方式是由 [`kube2iam`](https://github.com/jtblin/kube2iam) 提供。

    > **注意：**
    >
    > - 使用该授权模式时，可以参考[`kube2iam 文档`](https://github.com/jtblin/kube2iam#usage) 在 Kubernetes 集群中创建 kube2iam 环境， 并且部署 TiDB Operator 以及 TiDB 集群。
    > - 该模式不适用于 [`hostNetwork`](https://kubernetes.io/docs/concepts/policy/pod-security-policy) 网络模式，请确保参数 `spec.tikv.hostNetwork` 的值为 `false`。

* 通过将 [IAM](https://aws.amazon.com/cn/iam/) 绑定 ServiceAccount 进行授权:

    通过将用户的 IAM 角色与 Kubeneters 中的 [`serviceAccount`](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#serviceaccount) 资源进行绑定， 从而使得使用该 ServiceAccount 账号的 Pod 都拥有该角色所拥有的权限，这种授权方式由 [`EKS Pod Identity Webhook`](https://github.com/aws/amazon-eks-pod-identity-webhook) 服务提供。

    使用该授权模式时，可以参考 [AWS 官方文档](https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/create-cluster.html) 创建 EKS 集群， 并且部署 TiDB Operator 以及 TiDB 集群。

## Ad-hoc 备份

Ad-hoc 备份支持全量备份与增量备份。Ad-hoc 备份通过创建一个自定义的 `Backup` Custom Resource (CR) 对象来描述一次备份。TiDB Operator 根据这个 `Backup` 对象来完成具体的备份过程。如果备份过程中出现错误，程序不会自动重试，此时需要手动处理。

目前 Ad-hoc 备份已经兼容以上三种授权模式，本文档提供如下备份示例。示例假设对部署在 Kubernetes `test1` 这个 namespace 中的 TiDB 集群 `demo1` 进行数据备份，下面是具体操作过程。

### Ad-hoc 备份环境准备

#### 通过 AccessKey 和 SecretKey 授权

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 创建 `s3-secret` secret。该 secret 存放用于访问 S3 兼容存储的凭证。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic s3-secret --from-literal=access_key=xxx --from-literal=secret_key=yyy --namespace=test1
    ```

3. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的用户所对应的密码。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

#### 通过 IAM 绑定 Pod 授权

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的用户所对应的密码：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

3. 创建 IAM 角色：

    可以参考 [AWS 官方文档](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)来为账号创建一个 IAM 角色，并且通过 [AWS 官方文档](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html) 为 IAM 角色赋予需要的权限。由于 `Backup` 需要访问 AWS 的 S3 存储，所以这里给 IAM 赋予了 `AmazonS3FullAccess` 的权限。

4. 绑定 IAM 到 TiKV Pod：

    在使用 BR 备份的过程中，TiKV Pod 和 BR Pod 一样需要对 S3 存储进行读写操作，所以这里需要给 TiKV Pod 打上 annotation 来绑定 IAM 角色。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc demo1 -n test1
    ```

    找到 `spec.tikv.annotations`，增加 annotation `iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user`，然后退出编辑，等到 TiKV Pod 重启后，查看 Pod 是否加上了这个 annotation。

> **注意：**
>
> `arn:aws:iam::123456789012:role/user` 为步骤 4 中创建的 IAM 角色。

#### 通过 IAM 绑定 ServiceAccount 授权

1. 下载文件 [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml)，并执行以下命令在 `test1` 这个 namespace 中创建备份需要的 RBAC 相关资源：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. 创建 `backup-demo1-tidb-secret` secret。该 secret 存放用于访问 TiDB 集群的 root 账号和密钥：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=${password} --namespace=test1
    ```

3. 在集群上为服务帐户启用 IAM 角色：

    可以参考 [AWS 官方文档](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html) 开启所在的 EKS 集群的 IAM 角色授权。

4. 创建 IAM 角色：

    可以参考 [AWS 官方文档](https://docs.aws.amazon.com/eks/latest/userguide/create-service-account-iam-policy-and-role.html)创建一个 IAM 角色，为角色赋予 `AmazonS3FullAccess` 的权限，并且编辑角色的 `Trust relationships`。

5. 绑定 IAM 到 ServiceAccount 资源上：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate sa tidb-backup-manager -n eks.amazonaws.com/role-arn=arn:aws:iam::123456789012:role/user --namespace=test1
    ```

6. 将 ServiceAccount 绑定到 TiKV Pod：
    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc demo1 -n test1
    ```

    将 `spec.tikv.serviceAccount` 修改为 tidb-backup-manager，等到 TiKV Pod 重启后，查看 Pod 的 `serviceAccountName` 是否有变化。

> **注意：**
>
> `arn:aws:iam::123456789012:role/user` 为步骤 4 中创建的 IAM 角色。

### 数据库账户权限

* `mysql.tidb` 表的 `SELECT` 和 `UPDATE` 权限：备份前后，backup CR 需要一个拥有该权限的数据库账户，用于调整 GC 时间

### 使用 BR 备份数据到 Amazon S3 的存储

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

更多 `Backup` CR 字段的详细解释:

* `.spec.metadata.namespace`：`Backup` CR 所在的 namespace。
* `.spec.tikvGCLifeTime`：备份中的临时 `tikv_gc_lifetime` 时间设置，默认为 72h。

    在备份开始之前，若 TiDB 集群的 `tikv_gc_lifetime` 小于用户设置的 `spec.tikvGCLifeTime`，为了保证备份的数据不被 TiKV GC 掉，TiDB Operator 会在备份前[调节 `tikv_gc_lifetime`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview#导出大规模数据时的-tidb-gc-设置) 为 `spec.tikvGCLifeTime`。

    备份结束后不论成功或者失败，只要老的 `tikv_gc_lifetime` 比设置的 `.spec.tikvGCLifeTime` 小，TiDB Operator 都会尝试恢复 `tikv_gc_lifetime` 为备份前的值。在极端情况下，TiDB Operator 访问数据库失败会导致 TiDB Operator 无法自动恢复 `tikv_gc_lifetime` 并认为备份失败。

    此时，可以通过下述语句查看当前 TiDB 集群的 `tikv_gc_lifetime`：

    ```sql
    select VARIABLE_NAME, VARIABLE_VALUE from mysql.tidb where VARIABLE_NAME like "tikv_gc_life_time";
    ```

    如果发现 `tikv_gc_lifetime` 值过大（通常为 10m），则需要按照[调节 `tikv_gc_lifetime`](https://docs.pingcap.com/zh/tidb/stable/dumpling-overview#导出大规模数据时的-tidb-gc-设置) 将 `tikv_gc_lifetime` 调回原样。

* `.spec.cleanPolicy`：备份集群后删除备份 CR 时的备份文件清理策略。目前支持三种清理策略：

    * `Retain`：任何情况下，删除备份 CR 时会保留备份出的文件
    * `Delete`：任何情况下，删除备份 CR 时会删除备份出的文件
    * `OnFailure`：如果备份中失败，删除备份 CR 时会删除备份出的文件

    如果不配置该字段，或者配置该字段的值为上述三种以外的值，均会保留备份出的文件。值得注意的是，在 v1.1.2 以及之前版本不存在该字段，且默认在删除 CR 的同时删除备份的文件。若 v1.1.3 及之后版本的用户希望保持该行为，需要设置该字段为 `Delete`。

* `.spec.from.host`：待备份 TiDB 集群的访问地址，为需要导出的 TiDB 的 service name，例如 `basic-tidb`。
* `.spec.from.port`：待备份 TiDB 集群的访问端口。
* `.spec.from.user`：待备份 TiDB 集群的访问用户。
* `.spec.from.tidbSecretName`：待备份 TiDB 集群 `.spec.from.user` 用户的密码所对应的 secret。
* `.spec.from.tlsClientSecretName`：指定备份使用的存储证书的 Secret。

    如果 TiDB 集群开启了 [TLS](enable-tls-between-components.md)，但是不想使用[文档](enable-tls-between-components.md)中创建的 `${cluster_name}-cluster-client-secret` 进行备份，可以通过这个参数为备份指定一个 Secret，可以通过如下命令生成：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${secret_name} --namespace=${namespace} --from-file=tls.crt=${cert_path} --from-file=tls.key=${key_path} --from-file=ca.crt=${ca_path}
    ```

* `.spec.tableFilter`：备份时指定让 BR 备份符合 [table-filter 规则](https://docs.pingcap.com/zh/tidb/stable/table-filter/) 的表。默认情况下该字段可以不用配置。当不配置时，BR 会备份除系统库以外的所有数据库：

    > **注意：**
    >
    > `tableFilter` 如果要写排除规则导出除 `db.table` 的所有表，`"!db.table"` 前必须先添加 `*.*` 规则来导出所有表，如下面例子所示：

    ```
    tableFilter:
    - "*.*"
    - "!db.table"
    ```

以上示例中，`.spec.br` 中的一些参数项均可省略，如 `logLevel`、`statusAddr`、`concurrency`、`rateLimit`、`checksum`、`timeAgo`、`sendCredToTikv`。

自 v1.1.6 版本起，如果需要增量备份，只需要在 `spec.br.options` 中指定上一次的备份时间戳 `--lastbackupts` 即可。有关增量备份的限制，可参考 [使用 BR 进行备份与恢复](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-tool#增量备份)。

* `.spec.br.cluster`：代表需要备份的集群名字。
* `.spec.br.clusterNamespace`：代表需要备份的集群所在的 `namespace`。
* `.spec.br.logLevel`：代表日志的级别。默认为 `info`。
* `.spec.br.statusAddr`：为 BR 进程监听一个进程状态的 HTTP 端口，方便用户调试。如果不填，则默认不监听。
* `.spec.br.concurrency`：备份时每一个 TiKV 进程使用的线程数。备份时默认为 4，恢复时默认为 128。
* `.spec.br.rateLimit`：是否对流量进行限制。单位为 MB/s，例如设置为 `4` 代表限速 4 MB/s，默认不限速。
* `.spec.br.checksum`：是否在备份结束之后对文件进行验证。默认为 `true`。
* `.spec.br.timeAgo`：备份 timeAgo 以前的数据，默认为空（备份当前数据），[支持](https://golang.org/pkg/time/#ParseDuration) "1.5h", "2h45m" 等数据。
* `.spec.br.sendCredToTikv`：BR 进程是否将自己的 AWS 权限传输给 TiKV 进程。默认为 `true`。
* `.spec.br.options`：BR 工具支持的额外参数，需要以字符串数组的形式传入。自 v1.1.6 版本起支持该参数。可用于指定 `lastbackupts` 以进行增量备份。

更多支持的兼容 S3 的 `provider` 如下：

* `alibaba`：Alibaba Cloud Object Storage System (OSS) formerly Aliyun
* `digitalocean`：Digital Ocean Spaces
* `dreamhost`：Dreamhost DreamObjects
* `ibmcos`：IBM COS S3
* `minio`：Minio Object Storage
* `netease`：Netease Object Storage (NOS)
* `wasabi`：Wasabi Object Storage
* `other`：Any other S3 compatible provider

## 定时全量备份

用户通过设置备份策略来对 TiDB 集群进行定时备份，同时设置备份的保留策略以避免产生过多的备份。定时全量备份通过自定义的 `BackupSchedule` CR 对象来描述。每到备份时间点会触发一次全量备份，定时全量备份底层通过 Ad-hoc 全量备份来实现。下面是创建定时全量备份的具体步骤：

### 定时全量备份环境准备

同 [Ad-hoc 备份环境准备](#ad-hoc-备份环境准备)。

### 使用 BR 定时备份数据到 Amazon S3 的存储

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

从以上两个示例可知，`backupSchedule` 的配置由两部分组成。一部分是 `backupSchedule` 独有的配置，另一部分是 `backupTemplate`。`backupTemplate` 指定 S3 兼容存储相关的配置，该配置与 Ad-hoc 备份到兼容 S3 的存储配置完全一样，可参考[使用 BR 备份数据到 Amazon S3 的存储](#使用-br-备份数据到-amazon-s3-的存储)。下面介绍 `backupSchedule` 独有的配置项：

+ `.spec.maxBackups`：一种备份保留策略，决定定时备份最多可保留的备份个数。超过该数目，就会将过时的备份删除。如果将该项设置为 `0`，则表示保留所有备份。
+ `.spec.maxReservedTime`：一种备份保留策略，按时间保留备份。例如将该参数设置为 `24h`，表示只保留最近 24 小时内的备份条目。超过这个时间的备份都会被清除。时间设置格式参考 [`func ParseDuration`](https://golang.org/pkg/time/#ParseDuration)。如果同时设置最大备份保留个数和最长备份保留时间，则以最长备份保留时间为准。
+ `.spec.schedule`：Cron 的时间调度格式。具体格式可参考 [Cron](https://en.wikipedia.org/wiki/Cron)。
+ `.spec.pause`：该值默认为 `false`。如果将该值设置为 `true`，表示暂停定时调度。此时即使到了调度时间点，也不会进行备份。在定时备份暂停期间，备份 Garbage Collection (GC) 仍然正常进行。将 `true` 改为 `false` 则重新开启定时全量备份。

## 删除备份的 backup CR

用户可以通过下述语句来删除对应的备份 CR 或定时全量备份 CR。

{{< copyable "shell-regular" >}}

```shell
kubectl delete backup ${name} -n ${namespace}
kubectl delete backupschedule ${name} -n ${namespace}
```

如果你使用 v1.1.2 及以前版本，或使用 v1.1.3 及以后版本并将 `spec.cleanPolicy` 设置为 `Delete` 时，TiDB Operator 在删除 CR 时会同时删除备份文件。

在满足上述条件时，如果需要删除 namespace，建议首先删除所有的 Backup/BackupSchedule CR，再删除 namespace。

如果直接删除存在 Backup/BackupSchedule CR 的 namespace，TiDB Operator 会持续尝试创建 Job 清理备份的数据，但因为 namespace 处于 `Terminating` 状态而创建失败，从而导致 namespace 卡在该状态。

这时需要通过下述命令删除 `finalizers`：

{{< copyable "shell-regular" >}}

```shell
kubectl edit backup ${name} -n ${namespace}
```

删除 `metadata.finalizers` 配置，即可正常删除 CR。

## 故障诊断

在使用过程中如果遇到问题，可以参考[故障诊断](deploy-failures.md)。
