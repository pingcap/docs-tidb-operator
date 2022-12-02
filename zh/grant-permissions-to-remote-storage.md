---
title: 远程存储访问授权
summary: 介绍如何授权访问远程存储。
---

# 远程存储访问授权

本文详细描述了如何授权访问远程存储，以实现备份 TiDB 集群数据到远程存储或从远程存储恢复备份数据到 TiDB 集群。

## AWS 账号授权

在 AWS 云环境中，不同的类型的 Kubernetes 集群提供了不同的权限授予方式。本文分别介绍以下三种权限授予配置方式。

### 通过 AccessKey 和 SecretKey 授权

AWS 的客户端支持读取进程环境变量中的 `AWS_ACCESS_KEY_ID` 以及 `AWS_SECRET_ACCESS_KEY` 来获取与之相关联的用户或者角色的权限。

创建 `s3-secret` secret，在以下命令中使用 AWS 账号的 AccessKey 和 SecretKey 进行授权。该 secret 存放用于访问 S3 兼容存储的凭证。

{{< copyable "shell-regular" >}}

```shell
kubectl create secret generic s3-secret --from-literal=access_key=xxx --from-literal=secret_key=yyy --namespace=test1
```

### 通过 IAM 绑定 Pod 授权

通过将用户的 [IAM](https://aws.amazon.com/cn/iam/) 角色与所运行的 Pod 资源进行绑定，使 Pod 中运行的进程获得角色所拥有的权限，这种授权方式是由 [`kube2iam`](https://github.com/jtblin/kube2iam) 提供。

> **注意：**
>
> - 使用该授权模式时，可以参考 [kube2iam 文档](https://github.com/jtblin/kube2iam#usage)在 Kubernetes 集群中创建 kube2iam 环境，并且部署 TiDB Operator 以及 TiDB 集群。
> - 该模式不适用于 [`hostNetwork`](https://kubernetes.io/docs/concepts/policy/pod-security-policy) 网络模式，请确保参数 `spec.tikv.hostNetwork` 的值为 `false`。

1. 创建 IAM 角色：

    可以参考 [AWS 官方文档](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)来为账号创建一个 IAM 角色，并且通过 [AWS 官方文档](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html)为 IAM 角色赋予需要的权限。由于 `Backup` 需要访问 AWS 的 S3 存储，所以这里给 IAM 赋予了 `AmazonS3FullAccess` 的权限。

    如果是进行基于 AWS Elastic Block Store (EBS) 快照的备份和恢复，除完整的 S3 权限 `AmazonS3FullAccess` 外，还需要以下权限：
    
    ```json
            {
            "Effect": "Allow",
            "Action": [
                "ec2:AttachVolume",
                "ec2:CreateSnapshot",
                "ec2:CreateTags",
                "ec2:CreateVolume",
                "ec2:DeleteSnapshot",
                "ec2:DeleteTags",
                "ec2:DeleteVolume",
                "ec2:DescribeInstances",
                "ec2:DescribeSnapshots",
                "ec2:DescribeTags",
                "ec2:DescribeVolumes",
                "ec2:DetachVolume"
            ],
            "Resource": "*"
        }
    ```

2. 绑定 IAM 到 TiKV Pod：

    在使用 BR 备份的过程中，TiKV Pod 和 BR Pod 一样需要对 S3 存储进行读写操作，所以这里需要给 TiKV Pod 打上 annotation 来绑定 IAM 角色。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc demo1 -n test1 --type merge -p '{"spec":{"tikv":{"annotations":{"iam.amazonaws.com/role":"arn:aws:iam::123456789012:role/user"}}}}'
    ```

    等到 TiKV Pod 重启后，查看 Pod 是否加上了这个 annotation。

> **注意：**
>
> `arn:aws:iam::123456789012:role/user` 为步骤 1 中创建的 IAM 角色。

### 通过 IAM 绑定 ServiceAccount 授权

通过将用户的 [IAM](https://aws.amazon.com/cn/iam/) 角色与 Kubeneters 中的 [`serviceAccount`](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#serviceaccount) 资源进行绑定， 从而使得使用该 ServiceAccount 账号的 Pod 都拥有该角色所拥有的权限，这种授权方式由 [`EKS Pod Identity Webhook`](https://github.com/aws/amazon-eks-pod-identity-webhook) 服务提供。

使用该授权模式时，可以参考 [AWS 官方文档](https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/create-cluster.html)创建 EKS 集群，并且部署 TiDB Operator 以及 TiDB 集群。

1. 在集群上为服务帐户启用 IAM 角色：

    可以参考 [AWS 官方文档](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)开启所在的 EKS 集群的 IAM 角色授权。

2. 创建 IAM 角色：

    可以参考 [AWS 官方文档](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html)创建一个 IAM 角色，为角色赋予 `AmazonS3FullAccess` 的权限，并且编辑角色的 `Trust relationships`，

    如果是进行基于 AWS EBS 快照的备份和恢复，除完整的 S3 权限 `AmazonS3FullAccess` 外，还需要以下权限：

    {{< copyable "shell-regular" >}}

    ```json
            {
            "Effect": "Allow",
            "Action": [
                "ec2:AttachVolume",
                "ec2:CreateSnapshot",
                "ec2:CreateTags",
                "ec2:CreateVolume",
                "ec2:DeleteSnapshot",
                "ec2:DeleteTags",
                "ec2:DeleteVolume",
                "ec2:DescribeInstances",
                "ec2:DescribeSnapshots",
                "ec2:DescribeTags",
                "ec2:DescribeVolumes",
                "ec2:DetachVolume"
            ],
            "Resource": "*"
        }
    ```

3. 绑定 IAM 到 ServiceAccount 资源上：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate sa tidb-backup-manager -n eks.amazonaws.com/role-arn=arn:aws:iam::123456789012:role/user --namespace=test1
    ```

4. 将 ServiceAccount 绑定到 TiKV Pod：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc demo1 -n test1 --type merge -p '{"spec":{"tikv":{"serviceAccount": "tidb-backup-manager"}}}'
    ```

    将 `spec.tikv.serviceAccount` 修改为 tidb-backup-manager，等到 TiKV Pod 重启后，查看 Pod 的 `serviceAccountName` 是否有变化。

> **注意：**
>
> `arn:aws:iam::123456789012:role/user` 为步骤 2 中创建的 IAM 角色。

## GCS 账号授权

### 通过服务账号密钥授权

创建 `gcs-secret` secret。该 secret 存放用于访问 GCS 的凭证。`google-credentials.json` 文件存放用户从 GCP console 上下载的 service account key。具体操作参考 [GCP 官方文档](https://cloud.google.com/docs/authentication/getting-started)。

{{< copyable "shell-regular" >}}

```shell
kubectl create secret generic gcs-secret --from-file=credentials=./google-credentials.json -n test1
```

## Azure 账号授权

在 Azure 云环境中，不同的类型的 Kubernetes 集群提供了不同的权限授予方式。本文分别介绍以下两种权限授予配置方式。

### 通过访问密钥授权

Azure 的客户端支持读取进程环境变量中的 `AZURE_STORAGE_ACCOUNT` 以及 `AZURE_STORAGE_KEY` 来获取与之相关联的用户或者角色的权限。

创建 `azblob-secret` secret，在以下命令中使用 Azure 账号的访问密钥进行授权。该 secret 存放用于访问 Azure Blob Storage 的凭证。

{{< copyable "shell-regular" >}}

```shell
kubectl create secret generic azblob-secret --from-literal=AZURE_STORAGE_ACCOUNT=xxx --from-literal=AZURE_STORAGE_KEY=yyy --namespace=test1
```

### 通过 Azure AD 授权

Azure 的客户端支持读取进程环境变量中的 `AZURE_STORAGE_ACCOUNT`、`AZURE_CLIENT_ID`、`AZURE_TENANT_ID`、`AZURE_CLIENT_SECRET` 来获取与之相关联的用户或者角色的权限。

1. 创建 `azblob-secret-ad` secret，在以下命令中使用 Azure 账号的 AD 进行授权。该 secret 存放用于访问 Azure Blob Storage 的凭证。

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic azblob-secret-ad --from-literal=AZURE_STORAGE_ACCOUNT=xxx --from-literal=AZURE_CLIENT_ID=yyy --from-    literal=AZURE_TENANT_ID=zzz --from-literal=AZURE_CLIENT_SECRET=aaa --namespace=test1
    ```

2. 绑定 secret 到 TiKV Pod:

    在使用 BR 备份的过程中，TiKV Pod 和 BR Pod 一样需要对 Azure Blob Storage 进行读写操作，所以这里需要给 TiKV Pod 绑定 secret。

     {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc demo1 -n test1 --type merge -p '{"spec":{"tikv":{"envFrom":[{"secretRef":{"name":"azblob-secret-ad"}}]}}}'
    ```

    等到 TiKV Pod 重启后，查看 Pod 是否加上了这些环境变量。
