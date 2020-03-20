---
title: Back up TiDB Cluster Data to AWS Using BR
summary:
category: how-to
---

# Back up TiDB Cluster Data to AWS Using BR

This document describes how to back up the data of a TiDB cluster in AWS Kubernetes to AWS storage using Helm charts. "Backup" in this document refers to full backup (ad-hoc full backup and scheduled full backup). [`BR`](https://pingcap.com/docs/v3.1/reference/tools/br/br) is used to get the logic backup of the TiDB cluster, and then this backup data is sent to the AWS storage.

The backup method described in this document is implemented using Custom Resource Definition (CRD) in TiDB Operator v1.1 or later versions.

## Three methods to get AWS account authorization

In the AWS cloud environment, different types of Kubernetes clusters provide different methods to get AWS account authorization. This document describes the following three methods:

1. Import the AccessKey and SecretKey of the AWS account:

    - The AWS client supports reading `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the process environment variables to get privileges of the associated user or role.

2. Bind [IAM](https://aws.amazon.com/cn/iam/) with Pod:

    - By binding the IAM role of the user with the running Pod resources, the process that runs in Pod gets the privileges owned by the role. 
    - This authorization method is provided by [`kube2iam`](https://github.com/jtblin/kube2iam).

    > **Note:**
    >
    > - When you use this method, refer to [`kube2iam` Usage] for instructions on how to create the `kube2iam` environment in the Kubernetes cluster and deploy TiDB Operator and TiDB cluster.
    > - This method does not apply to [`hostNetwork`](https://kubernetes.io/docs/concepts/policy/pod-security-policy). Please make sure that the `spec.tikv.hostNetwork` parameter is set to `false`.

3. Bind [IAM](https://aws.amazon.com/cn/iam/) with ServiceAccount:

    - By binding the IAM role of the user with the [`serviceAccount`](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#serviceaccount) resources in Kubernetes, the Pods of this ServiceAccount get the privileges owned by the role.
    - This method is provided by [`EKS Pod Identity Webhook`](https://github.com/aws/amazon-eks-pod-identity-webhook).

> **Note:**
>
> When you use this method, refer to [AWS Documentation] for instructions on how to create a EKS cluster and deploy TiDB Operator and TiDB cluster.

## Ad-hoc full backup

Ad-hoc full backup describes the backup by creating a `Backup` Custom Resource (CR) object. TiDB Operator performs the specific backup operation based on this `Backup` object. If an error occurs during the backup process, TiDB Operator does not retry, and you need to handle this error manually.

Currently, the above three authorization methods are supported in ad-hoc full backup. Therefore, this document shows examples in which the data of the `demo1` TiDB cluster in the `test1` Kubernetes namespace is backed up to AWS storage.

### Prerequisites for ad-hoc backup

#### Get authorization by AccessKey and SecretKey

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test1` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. Create the `s3-secret` secret which stores the credential used to access the S3-compatible storage:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic s3-secret --from-literal=access_key=xxx --from-literal=secret_key=yyy --namespace=test1
    ```

3. Create the `backup-demo1-tidb-secret` secret which stores the account and password needed to access the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
    ```

#### Get authorization by binding IAM with Pod

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test1` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test1
    ```

2. Create the `backup-demo1-tidb-secret` secret which stores the account and password needed to access the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
    ```

3. Create the IAM role:

    - To create a IAM role for the account, refer to [Create an IAM User](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html).
    - Give the IAM role you created the permission it needs. Because `Backup` needs to access AWS S3 storage, IAM is given the `AmazonS3FullAccess` permission.

4. Bind IAM to TiKV Pod:

    - In the process of backup using BR, both TiKV Pod and BR Pod need to read and write S3 storage. Therefore, you need to add annotation to TiKV Pod to bind it with the IAM role:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc demo1 -n test1
    ```

    - Find `spec.tikv.annotations`, append the `arn:aws:iam::123456789012:role/user` annotation, and then exit. After TiKV Pod is restarted, check whether the annotation is added to TiKV Pod.

    > **Note:**
    >
    > `arn:aws:iam::123456789012:role/user` is the IAM role created in Step 4.

#### Get authorization by binding IAM with ServiceAccount

1. Download [backup-rbac.yaml](https://github.com/pingcap/tidb-operator/blob/master/manifests/backup/backup-rbac.yaml), and execute the following command to create the role-based access control (RBAC) resources in the `test1` namespace:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-rbac.yaml -n test2
    ```

2. Create the `backup-demo1-tidb-secret` secret which stores the account and password needed to access the TiDB cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic backup-demo1-tidb-secret --from-literal=password=<password> --namespace=test1
    ```

3. Enable the IAM role for the service account on the cluster:

    - To enable the IAM role on your EKS cluster, refer to [Amazon EKS Documentation](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)

4. Create a IAM role:

    - Create a IAM role and give the `AmazonS3FullAccess` permission to the role. Modify `Trust relationships` of the role. For details, refer to [Creating an IAM Role and Policy](https://docs.aws.amazon.com/eks/latest/userguide/create-service-account-iam-policy-and-role.html).

5. Bind IAM to the ServiceAccount resources:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate sa tidb-backup-manager -n eks.amazonaws.com/role-arn=arn:aws:iam::123456789012:role/user --namespace=test1
    ```

6. Bind ServiceAccount to TiKV Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl edit tc demo1 -n test1
    ```

    Set `spec.tikv.serviceAccount` to tidb-backup-manager. After TiKV Pod is restarted, check whether the `serviceAccountName` of TiKV Pod has changed.

    > **Note:**
    >
    > `arn:aws:iam::123456789012:role/user` is the IAM role created in Step 4.

### Back up data to Amazon S3

- Create the `Backup` CR, and back up cluster data by way of accessKey and secretKey authorization:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    The content of `backup-aws-s3.yaml` is as follows:

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
        # enableTLSClient: false
        # logLevel: info
        # statusAddr: <status-addr>
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: <time>
        # checksum: true
        # sendCredToTikv: true
      from:
        host: <tidb-host-ip>
        port: <tidb-port>
        user: <tidb-user>
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        secretName: s3-secret
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

- Create the `Backup` CR, and back up cluster data by way of binding IAM with Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    The content of `backup-aws-s3.yaml` is as follows:

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
        # enableTLSClient: false
        # logLevel: info
        # statusAddr: <status-addr>
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: <time>
        # checksum: true
      from:
        host: <tidb-host-ip>
        port: <tidb-port>
        user: <tidb-user>
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

- Create the `Backup` CR, and back up cluster data by way of binding IAM with ServiceAccount:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f backup-aws-s3.yaml
    ```

    The content of `backup-aws-s3.yaml` is as follows:

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
        # enableTLSClient: false
        # logLevel: info
        # statusAddr: <status-addr>
        # concurrency: 4
        # rateLimit: 0
        # timeAgo: <time>
        # checksum: true
      from:
        host: <tidb-host-ip>
        port: <tidb-port>
        user: <tidb-user>
        secretName: backup-demo1-tidb-secret
      s3:
        provider: aws
        region: us-west-1
        bucket: my-bucket
        prefix: my-folder
    ```

The above three examples uses three methods of authorization to back up data to Amazon S3 storage. The `acl`, `endpoint`, `storageClass` configuration items of Amazon S3 can be ignored.

Amazon S3 supports the following access-control list (ACL) policies:

- `private`
- `public-read`
- `public-read-write`
- `authenticated-read`
- `bucket-owner-read`
- `bucket-owner-full-control`

If the ACL policy is not configured, the `private` policy is used by default. For the detailed description of these access control policies, refer to [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html).

Amazon S3 supports the following `storageClass` types:

- `STANDARD`
- `REDUCED_REDUNDANCY`
- `STANDARD_IA`
- `ONEZONE_IA`
- `GLACIER`
- `DEEP_ARCHIVE`

If `storageClass` is not configured, `STANDARD_IA` is used by default. For the detailed description of these storage types, refer to [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html).

After creating the `Backup` CR, you can use the following command to check the backup status:

{{< copyable "shell-regular" >}}

 ```shell
 kubectl get bk -n test1 -o wide
 ```

More `Backup` CR fields are described as follows:

- `.spec.metadata.namespace`: the namespace where the `Backup` CR is located.
- `.spec.from.host`: the address of the TiDB cluster to be backed up.
- `.spec.from.port`: the port of the TiDB cluster to be backed up.
- `.spec.from.user`: the accessing user of the TiDB cluster to be backed up.
- `.spec.from.tidbSecretName`: the secret of the credential needed by the `.spec.from.user` TiDB cluster to be backed up.

More S3-compatible `provider`s are described as follows:

- `alibaba`：Alibaba Cloud Object Storage System (OSS) formerly Aliyun
- `digitalocean`：Digital Ocean Spaces
- `dreamhost`：Dreamhost DreamObjects
- `ibmcos`：IBM COS S3
- `minio`：Minio Object Storage
- `netease`：Netease Object Storage (NOS)
- `wasabi`：Wasabi Object Storage
- `other`：Any other S3 compatible provider

## Scheduled full backup
