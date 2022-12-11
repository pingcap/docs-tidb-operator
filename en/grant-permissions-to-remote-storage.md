---
title: Grant Permissions to Remote Storage
summary: Learn how to grant permissions to access remote storage for backup and restore.
---

# Grant Permissions to Remote Storage

This document describes how to grant permissions to access remote storage for backup and restore. During the backup process, TiDB cluster data is backed up to the remote storage. During the restore process, the backup data is restored from the remote storage to the TiDB cluster.

## AWS account permissions

Amazon Web Service (AWS) provides different methods to grant permissions for different types of Kubernetes clusters. This document describes the following three methods.

### Grant permissions by AccessKey and SecretKey

The AWS client can read `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from the process environment variables to obtain the associated user or role permissions.

Create the `s3-secret` secret by running the following command. Use the AWS account's AccessKey and SecretKey. The secret stores the credential used for accessing S3-compatible storage.

{{< copyable "shell-regular" >}}

```shell
kubectl create secret generic s3-secret --from-literal=access_key=xxx --from-literal=secret_key=yyy --namespace=test1
```

### Grant permissions by associating IAM with Pod

If you associate the user's [IAM](https://aws.amazon.com/cn/iam/) role with the resources of the running Pods, the processes running in the Pods can have the permissions of the role. This method is provided by [`kube2iam`](https://github.com/jtblin/kube2iam).

> **Note:**
>
> - When you use this method to grant permissions, you can [create the `kube2iam` environment](https://github.com/jtblin/kube2iam#usage) in the Kubernetes cluster and deploy TiDB Operator and the TiDB cluster.
> - This method is not applicable to the [`hostNetwork`](https://kubernetes.io/docs/concepts/policy/pod-security-policy) mode. Make sure the value of `spec.tikv.hostNetwork` is set to `false`.

1. Create an IAM role.

    First, [create an IAM User](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) for your account.

    Then, Give the required permission to the IAM role you have created. Refer to [Adding and Removing IAM Identity Permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html) for details.

    Because the `Backup` CR needs to access the Amazon S3 storage, the IAM role is granted the `AmazonS3FullAccess` permission.

    When backing up a TiDB cluster using EBS volume snapshots, besides the `AmazonS3FullAccess` permission, the following permissions are also required:

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

2. Associate IAM with the TiKV Pod:

    When you use BR to back up TiDB data, the TiKV Pod also needs to perform read and write operations on S3-compatible storage as the BR Pod does. Therefore, you need to add annotations to the TiKV Pod to associate it with the IAM role.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc demo1 -n test1 --type merge -p '{"spec":{"tikv":{"annotations":{"iam.amazonaws.com/role":"arn:aws:iam::123456789012:role/user"}}}}'
    ```

    After the TiKV Pod is restarted, check whether the Pod has the annotation.

> **Note:**
>
> `arn:aws:iam::123456789012:role/user` is the IAM role created in Step 1.

### Grant permissions by associating IAM with ServiceAccount

If you associate the user's [IAM](https://aws.amazon.com/cn/iam/) role with [`serviceAccount`](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#serviceaccount) of Kubernetes, the Pods using the `serviceAccount` can have the permissions of the role. This method is provided by [`EKS Pod Identity Webhook`](https://github.com/aws/amazon-eks-pod-identity-webhook).

When you use this method to grant permissions, you can [create the EKS cluster](https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/create-cluster.html) and deploy TiDB Operator and the TiDB cluster.

1. Enable the IAM role for the `serviceAccount` in the cluster:

    Refer to [AWS documentation](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html).

2. Create the IAM role:

    [Create an IAM role](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html) and grant the `AmazonS3FullAccess` permissions to the role. Edit the role's `Trust relationships` to grant tidb-backup-manager the access to this IAM role.

     When backing up a TiDB cluster using EBS volume snapshots, besides the `AmazonS3FullAccess` permission, the following permissions are also required:

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

    At the same time, edit the role's `Trust relationships` to grant tidb-controller-manager the access to this IAM role.

3. Associate the IAM role with the `ServiceAccount` resources.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate sa tidb-backup-manager -n eks.amazonaws.com/role-arn=arn:aws:iam::123456789012:role/user --namespace=test1
    ```

    When backing up or restoring a TiDB cluster using EBS volume snapshots, you need to associate the IAM role with the `ServiceAccount` resources of tidb-controller-manager.

     ```shell
     kubectl annotate sa tidb-controller-manager -n eks.amazonaws.com/role-arn=arn:aws:iam::123456789012:role/user --namespace=tidb-admin
     ```

4. Associate the `ServiceAccount` with the TiKV Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc demo1 -n test1 --type merge -p '{"spec":{"tikv":{"serviceAccount": "tidb-backup-manager"}}}'
    ```

    Modify the value of `spec.tikv.serviceAccount` to `tidb-backup-manager`. After the TiKV Pod is restarted, check whether the Pod's `serviceAccountName` is changed.

> **Note:**
>
> `arn:aws:iam::123456789012:role/user` is the IAM role created in Step 2.

## GCS account permissions

### Grant permissions by the service account

Create the `gcs-secret` secret which stores the credential used to access GCS. The `google-credentials.json` file stores the service account key that you have downloaded from the GCP console. Refer to [GCP documentation](https://cloud.google.com/docs/authentication/getting-started) for details.

{{< copyable "shell-regular" >}}

```shell
kubectl create secret generic gcs-secret --from-file=credentials=./google-credentials.json -n test1
```

## Azure account permissions

Azure provides different methods to grant permissions for different types of Kubernetes clusters. This document describes the following two methods.

### Grant permissions by access key

The Azure client can read `AZURE_STORAGE_ACCOUNT` and `AZURE_STORAGE_KEY` from the process environment variables to obtain the associated user or role permissions.

Run the following command to create the `azblob-secret` secret and use your Azure account access key to grant permissions. The secret stores the credential used for accessing Azure Blob Storage.

{{< copyable "shell-regular" >}}

```shell
kubectl create secret generic azblob-secret --from-literal=AZURE_STORAGE_ACCOUNT=xxx --from-literal=AZURE_STORAGE_KEY=yyy --namespace=test1
```

### Grant permissions by Azure AD

The Azure client can read `AZURE_STORAGE_ACCOUNT`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET` to obtain the associated user or role permissions.

1. Create the `azblob-secret-ad` secret by running the following command. Use the Active Directory (AD) of your Azure account. The secret stores the credential used for accessing Azure Blob Storage.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic azblob-secret-ad --from-literal=AZURE_STORAGE_ACCOUNT=xxx --from-literal=AZURE_CLIENT_ID=yyy --from-literal=AZURE_TENANT_ID=zzz --from-literal=AZURE_CLIENT_SECRET=aaa --namespace=test1
    ```

2. Associate the secret with the TiKV Pod:

    When you use BR to back up TiDB data, the TiKV Pod also needs to perform read and write operations on Azure Blob Storage as the BR Pod does. Therefore, you need to associate the TiKV Pod with the secret.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc demo1 -n test1 --type merge -p '{"spec":{"tikv":{"envFrom":[{"secretRef":{"name":"azblob-secret-ad"}}]}}}'
    ```

    After the TiKV Pod is restarted, check whether the Pod has the environment variables.
