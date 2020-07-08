---
title: Back up Data to S3-Compatible Storage Using Mydumper
summary: Learn how to back up the TiDB cluster to the S3-compatible storage.
category: how-to
aliases: ['/docs/tidb-in-kubernetes/stable/backup-to-s3/','/docs/tidb-in-kubernetes/v1.1/backup-to-s3/']
---

# Back up Data to S3-Compatible Storage Using Mydumper

This document describes how to back up the data of the TiDB cluster in Kubernetes to the S3-compatible storage. "Backup" in this document refers to full backup (ad-hoc full backup and scheduled full backup). For the underlying implementation, [`mydumper`](https://pingcap.com/docs/stable/mydumper-overview/) is used to get the logic backup of the TiDB cluster, and then this backup data is sent to the S3-compatible storage.

The backup method described in this document is implemented based on CustomResourceDefinition (CRD) in TiDB Operator v1.1 or later versions. For the backup method implemented based on Helm Charts, refer to [Back up and Restore TiDB Cluster Data Based on Helm Charts](backup-and-restore-using-helm-charts.md).

## Ad-hoc full backup to S3-compatible storage

Ad-hoc full backup describes the backup by creating a `Backup` custom resource (CR) object. TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry and you need to handle this error manually.

For the current S3-compatible storage types, Ceph and Amazon S3 work normally as tested. Therefore, this document shows examples in which the data of the `demo1` TiDB cluster in the `test1` Kubernetes namespace is backed up to Ceph and Amazon S3 respectively.

### Three methods to grant permissions of AWS account

- If you use Amazon S3 to back up and restore the cluster, you have three methods to grant permissions. For details, refer to [Back up TiDB Cluster Data to AWS Using BR](backup-to-aws-s3-using-br.md#three-methods-to-grant-aws-account-permissions).
- If Ceph is used as backend storage in backup and restore test, the permission is granted by importing AccessKey and SecretKey.

### Prerequisites for ad-hoc backup

Refer to [Ad-hoc full backup prerequisites](backup-to-aws-s3-using-br.md#prerequisites-for-ad-hoc-full-backup).

### Ad-hoc backup process

> **Note:**
>
> Because of the `rclone` [issue](https://rclone.org/s3/#key-management-system-kms), if the backup data is stored in Amazon S3 and the `AWS-KMS` encryption is enabled, you need to add the following `spec.s3.options` configuration to the YAML file in the examples of this section:
>
> ```yaml
> spec:
>   ...
>   s3:
>     ...
>     options:
>     - --ignore-checksum
> ```

**Examples:**

+ Create the `Backup` CR, and back up cluster data to Amazon S3 by importing AccessKey and SecretKey to grant permissions:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-s3.yaml
    ```

    The content of `backup-s3.yaml` is as follows:

    {{< copyable "" >}}

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
    # mydumper:
    #  options:
    #  - --tidb-force-priority=LOW_PRIORITY
    #  - --long-query-guard=3600
    #  - --threads=16
    #  - --rows=10000
    #  - --skip-tz-utc
    #  - --verbose=3
    #  tableRegex: "^test"
      storageClassName: local-storage
      storageSize: 10Gi
    ```

+ Create the `Backup` CR, and back up data to Ceph by importing AccessKay and SecretKey to grant permissions:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-s3.yaml
    ```

    The content of `backup-s3.yaml` is as follows:

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
    # mydumper:
    #  options:
    #  - --tidb-force-priority=LOW_PRIORITY
    #  - --long-query-guard=3600
    #  - --threads=16
    #  - --rows=10000
    #  - --skip-tz-utc
    #  - --verbose=3
    #  tableRegex: "^test"
      storageClassName: local-storage
      storageSize: 10Gi
    ```

+ Create the `Backup` CR, and back up data to Amazon S3 by binding IAM with Pod to grant permissions:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-s3.yaml
    ```

    The content of `backup-s3.yaml` is as follows:

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
    # mydumper:
    #  options:
    #  - --tidb-force-priority=LOW_PRIORITY
    #  - --long-query-guard=3600
    #  - --threads=16
    #  - --rows=10000
    #  - --skip-tz-utc
    #  - --verbose=3
    #  tableRegex: "^test"
      storageClassName: local-storage
      storageSize: 10Gi
    ```

+ Create the `Backup` CR, and back up data to Amazon S3 by binding IAM with ServiceAccount to grant permissions:

    {{< copyable "shell-regular" >}}

    ```yaml
    kubectl apply -f backup-s3.yaml
    ```

    The content of `backup-s3.yaml` is as follows:

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
    # mydumper:
    #  options:
    #  - --tidb-force-priority=LOW_PRIORITY
    #  - --long-query-guard=3600
    #  - --threads=16
    #  - --rows=10000
    #  - --skip-tz-utc
    #  - --verbose=3
    #  tableRegex: "^test"
      storageClassName: local-storage
      storageSize: 10Gi
    ```

In the examples above, all data of the TiDB cluster is exported and backed up to Amazon S3 and Ceph respectively. You can ignore the `acl`, `endpoint`, and `storageClass` configuration items in the Amazon S3 configuration. S3-compatible storage types other than Amazon S3 can also use configuration similar to that of Amazon S3. You can also leave the configuration item fields empty if you do not need to configure these items as shown in the above Ceph configuration.

Amazon S3 supports the following access-control list (ACL) polices:

* `private`
* `public-read`
* `public-read-write`
* `authenticated-read`
* `bucket-owner-read`
* `bucket-owner-full-control`

If the ACL policy is not configured, the `private` policy is used by default. For the detailed description of these access control policies, refer to [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html).

Amazon S3 supports the following `storageClass` types:

* `STANDARD`
* `REDUCED_REDUNDANCY`
* `STANDARD_IA`
* `ONEZONE_IA`
* `GLACIER`
* `DEEP_ARCHIVE`

If `storageClass` is not configured, `STANDARD_IA` is used by default. For the detailed description of these storage types, refer to [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html).

After creating the `Backup` CR, you can use the following command to check the backup status:

{{< copyable "shell-regular" >}}

 ```shell
 kubectl get bk -n test1 -owide
 ```

More `Backup` CRs are described as follows:

* `.spec.metadata.namespace`: the namespace where the `Backup` CR is located.
* `.spec.from.host`: the address of the TiDB cluster to be backed up.
* `.spec.from.port`: the port of the TiDB cluster to be backed up.
* `.spec.from.user`: the accessing user of the TiDB cluster to be backed up.
* `.spec.from.secretName`：the secret contains the password of the `.spec.from.user`.
* `spec.s3.region`: configures the Region where Amazon S3 is located if you want to use Amazon S3 for backup storage.
* `.spec.s3.bucket`: the name of the bucket compatible with S3 storage.
* `.spec.s3.prefix`: this field can be ignored. If you set this field, it will be used to make up the remote storage path `s3://${.spec.s3.bucket}/${.spec.s3.prefix}/backupName`.
* `.spec.mydumper`: Mydumper-related configurations, with two major fields. One is the [`options`](https://pingcap.com/docs/stable/reference/tools/mydumper/) field, which specifies some parameters needed by Mydumper, and the other is the `tableRegex` field, which allows Mydumper to back up a table that matches this regular expression. These configurations of Mydumper can be ignored by default. When not specified, the values of `options` and `tableRegex` (by default) is as follows:

    ```
    options:
    --tidb-force-priority=LOW_PRIORITY
    --long-query-guard=3600
    --threads=16
    --rows=10000
    --skip-tz-utc
    --verbose=3
   tableRegex: "^(?!(mysql|test|INFORMATION_SCHEMA|PERFORMANCE_SCHEMA|METRICS_SCHEMA|INSPECTION_SCHEMA))"
   ```

* `.spec.storageClassName`: the persistent volume (PV) type specified for the backup operation.
* `.spec.storageSize`: the PV size specified for the backup operation. This value must be greater than the backup data size of the TiDB cluster.

More S3-compatible `provider`s are described as follows:

* `alibaba`: Alibaba Cloud Object Storage System (OSS) formerly Aliyun
* `digitalocean`: Digital Ocean Spaces
* `dreamhost`: Dreamhost DreamObjects
* `ibmcos`: IBM COS S3
* `minio`: Minio Object Storage
* `netease`: Netease Object Storage (NOS)
* `wasabi`: Wasabi Object Storage
* `other`: Any other S3 compatible provider

## Scheduled full backup to S3-compatible storage

You can set a backup policy to perform scheduled backups of the TiDB cluster, and set a backup retention policy to avoid excessive backup items. A scheduled full backup is described by a custom `BackupSchedule` CR object. A full backup is triggered at each backup time point. Its underlying implementation is the ad-hoc full backup.

### Prerequisites for scheduled backup

The prerequisites for the scheduled backup is the same as the [prerequisites for ad-hoc backup](#prerequisites-for-ad-hoc-backup).

### Scheduled backup process

> **Note:**
>
> Because of the `rclone` [issue](https://rclone.org/s3/#key-management-system-kms), if the backup data is stored in Amazon S3 and the `AWS-KMS` encryption is enabled, you need to add the following `spec.backupTemplate.s3.options` configuration to the YAML file in the examples of this section:
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

**Examples:**

+ Create the `BackupSchedule` CR to enable the scheduled full backup to Amazon S3 by importing AccessKey and SecretKey to grant permissions:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    The content of `backup-schedule-s3.yaml` is as follows:

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
      # mydumper:
      #  options:
      #  - --tidb-force-priority=LOW_PRIORITY
      #  - --long-query-guard=3600
      #  - --threads=16
      #  - --rows=10000
      #  - --skip-tz-utc
      #  - --verbose=3
      #  tableRegex: "^test"
        storageClassName: local-storage
        storageSize: 10Gi
    ```

+ Create the `BackupSchedule` CR to enable the scheduled full backup to Ceph by importing AccessKey and SecretKey to grant permissions:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    The content of `backup-schedule-s3.yaml` is as follows:

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
      # mydumper:
      #  options:
      #  - --tidb-force-priority=LOW_PRIORITY
      #  - --long-query-guard=3600
      #  - --threads=16
      #  - --rows=10000
      #  - --skip-tz-utc
      #  - --verbose=3
      #  tableRegex: "^test"
        storageClassName: local-storage
        storageSize: 10Gi
    ```

+ Create the `BackupSchedule` CR to enable the scheduled full backup, and back up the cluster data to Amazon S3 by binding IAM with Pod to grant permissions:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    The content of `backup-schedule-s3.yaml` is as follows:

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
      # mydumper:
      #  options:
      #  - --tidb-force-priority=LOW_PRIORITY
      #  - --long-query-guard=3600
      #  - --threads=16
      #  - --rows=10000
      #  - --skip-tz-utc
      #  - --verbose=3
      #  tableRegex: "^test"
        storageClassName: local-storage
        storageSize: 10Gi
    ```

+ Create the `BackupSchedule` CR to enable the scheduled full backup, and back up the cluster data to Amazon S3 by binding IAM with ServiceAccount to grant permissions:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-schedule-s3.yaml
    ```

    The content of `backup-schedule-s3.yaml` is as follows:

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
      # mydumper:
      #  options:
      #  - --tidb-force-priority=LOW_PRIORITY
      #  - --long-query-guard=3600
      #  - --threads=16
      #  - --rows=10000
      #  - --skip-tz-utc
      #  - --verbose=3
      #  tableRegex: "^test"
        storageClassName: local-storage
        storageSize: 10Gi
    ```

After creating the scheduled full backup, you can use the following command to check the backup status:

{{< copyable "shell-regular" >}}

```shell
kubectl get bks -n test1 -owide
```

You can use the following command to check all the backup items:

{{< copyable "shell-regular" >}}

```shell
kubectl get bk -l tidb.pingcap.com/backup-schedule=demo1-backup-schedule-s3 -n test1
```

From the examples above, you can see that the `backupSchedule` configuration consists of two parts. One is the unique configuration of `backupSchedule`, and the other is `backupTemplate`. `backupTemple` specifies the configuration related to the S3-compatible storage, which is the same as the configuration of the ad-hoc full backup to the S3-compatible storage (refer to [Ad-hoc backup process](#ad-hoc-backup-process) for details). The following are the unique configuration items of `backupSchedule`:

+ `.spec.maxBackups`: A backup retention policy, which determines the maximum number of backup items to be retained. When this value is exceeded, the outdated backup items will be deleted. If you set this configuration item to `0`, all backup items are retained.
+ `.spec.maxReservedTime`: A backup retention policy based on time. For example, if you set the value of this configuration to `24h`, only backup items within the recent 24 hours are retained. All backup items out of this time are deleted. For the time format, refer to [`func ParseDuration`](https://golang.org/pkg/time/#ParseDuration). If you have set the maximum number of backup items and the longest retention time of backup items at the same time, the latter setting takes effect.
+ `.spec.schedule`: The time scheduling format of Cron. Refer to [Cron](https://en.wikipedia.org/wiki/Cron) for details.
+ `.spec.pause`: `false` by default. If this parameter is set to `true`, the scheduled scheduling is paused. In this situation, the backup operation will not be performed even if the scheduling time is reached. During this pause, the backup [Garbage Collection](https://pingcap.com/docs/stable/garbage-collection-overview/) (GC) runs normally. If you change `true` to `false`, the full backup process is restarted.

> **Note:**
>
> TiDB Operator creates a PVC. This PVC is used for both ad-hoc full backup and scheduled full backup. The backup data is stored in PV first, and then uploaded to remote storage. If you want to delete this PVC after the backup is completed, you can refer to [Delete Resource](cheat-sheet.md#delete-resources) to delete the backup Pod first, and then delete the PVC.
