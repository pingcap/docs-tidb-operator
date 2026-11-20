---
title: Grant Permissions to Remote Storage
summary: Learn how to grant permissions to remote storage to enable backup and restore for TiDB clusters.
---

# Grant Permissions to Remote Storage

This document describes how to grant permissions to access remote storage for backup and restore. During the backup process, TiDB cluster data is backed up to the remote storage. During the restore process, the backup data is restored from the remote storage to the TiDB cluster.

## Grant permissions to an AWS account

Amazon Web Services (AWS) provides different methods to grant permissions for different types of Kubernetes clusters. This document introduces the following three methods:

- [Grant permissions by AccessKey and SecretKey](#grant-permissions-by-accesskey-and-secretkey): applicable to self-managed Kubernetes clusters and AWS EKS clusters.
- [Grant permissions by associating IAM with Pod](#grant-permissions-by-associating-iam-with-pod): applicable to self-managed Kubernetes clusters.
- [Grant permissions by associating IAM with ServiceAccount](#grant-permissions-by-associating-iam-with-serviceaccount): applicable only to AWS EKS clusters.

### Create least-privilege IAM policies

Before using any of the AWS authorization methods, create a customer-managed IAM policy for the S3 location used by your `Backup` or `Restore` CR. Do not attach an account-wide AWS managed S3 policy such as `AmazonS3FullAccess`, because it grants access to every S3 bucket in the account.

Scope the policy according to the `s3` fields in the CR:

- Use `.spec.s3.bucket` for the bucket ARN.
- If `.spec.s3.prefix` is empty, grant access to the whole bucket.
- If `.spec.s3.prefix` is set, scope object access to `arn:aws:s3:::<bucket-name>/<prefix>/*`. The read-only restore example also restricts `s3:ListBucket` with an `s3:prefix` condition; backup requires an unconditional `s3:ListBucket` grant, as explained below.

Replace `<bucket-name>` with the bucket name and `<prefix>` with `.spec.s3.prefix` without leading or trailing slashes. For example, for a prefix of `backup/`, use `backup`. For these policy examples, use a prefix that does not contain `*` or `?`, because IAM interprets these characters as wildcards and can grant access outside the intended prefix.

For point-in-time recovery (PITR), also grant read access to the snapshot backup location specified by `.spec.pitrFullBackupStorageProvider.s3`. Add separate policy statements if the snapshot and log backups use different buckets or prefixes.

The following examples show the minimum S3 permissions for a `Backup` CR and for a read-only `Restore` CR.

#### Bucket-scoped policy for a `Backup` CR

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBackupBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::<bucket-name>"
    },
    {
      "Sid": "AccessBackupObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:AbortMultipartUpload"
      ],
      "Resource": "arn:aws:s3:::<bucket-name>/*"
    }
  ]
}
```

#### Prefix-scoped policy for a `Backup` CR

This policy restricts object access to the backup prefix but allows listing all object keys in the bucket. BR checks whether `backupmeta` exists before starting a backup. Without an unconditional `s3:ListBucket` grant, S3 can return `403 Forbidden` for a missing object, causing the backup to fail. Use a dedicated backup bucket if other object keys must remain hidden.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBackupBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::<bucket-name>"
    },
    {
      "Sid": "AccessBackupObjectsInPrefix",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:AbortMultipartUpload"
      ],
      "Resource": "arn:aws:s3:::<bucket-name>/<prefix>/*"
    }
  ]
}
```

#### Bucket-scoped policy for a read-only `Restore` CR

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBackupBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::<bucket-name>"
    },
    {
      "Sid": "ReadBackupObjects",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::<bucket-name>/*"
    }
  ]
}
```

#### Prefix-scoped policy for a read-only `Restore` CR

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBackupPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::<bucket-name>",
      "Condition": {
        "StringLike": {
          "s3:prefix": "<prefix>/*"
        }
      }
    },
    {
      "Sid": "ReadBackupObjectsInPrefix",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::<bucket-name>/<prefix>/*"
    }
  ]
}
```

When you use these policies, note the following conditions:

- If Backup and Restore resources use different buckets with the same IAM user or role, add the bucket and object ARNs for every required bucket to the corresponding `Resource` elements. Do not replace them with a wildcard that grants access to unrelated buckets.
- For buckets in AWS China Regions or AWS GovCloud (US) Regions, replace the `aws` partition in both ARNs with `aws-cn` or `aws-us-gov`, respectively.
- If a Backup resource, or a Restore resource that writes restore metadata to S3, sets `.spec.s3.acl`, add `s3:PutObjectAcl` to the object actions unless another policy already grants it.
- If bucket default encryption or a Backup or Restore resource selects a customer-managed AWS KMS key, grant the IAM user or role `kms:GenerateDataKey` and `kms:Decrypt` on the key used to write backup objects or restore metadata. For a read-only restore, grant `kms:Decrypt` on every key that encrypted the backup objects, including an older key if the bucket's default KMS key has changed since the backup was created. Make sure that each KMS key policy also permits these principals to use the required actions, either directly or through IAM policies.

The permissions required for restore depend on whether BR writes restore metadata to S3. If BR writes checkpoint metadata to S3, grant `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` for the checkpoint storage location. When `--checkpoint-storage` points to a different bucket or prefix, add policy statements for that location instead of adding write permissions to the backup location. Keep `s3:ListBucket` unconditional on the checkpoint bucket so that checks for missing checkpoint objects can succeed.

Starting from BR v8.5.5, if the target cluster does not contain `mysql.tidb_pitr_id_map` and `--checkpoint-storage` is not specified, PITR writes the ID map to the log backup directory. If that directory is in S3, add `s3:PutObject` for the log backup location and keep `s3:ListBucket` unconditional on that bucket so that BR can check whether the ID map exists.

For PITR into a target cluster with an existing S3 log backup task, BR also writes a table ID blocklist to that task's storage. This location can differ from both the source backup and checkpoint locations. Grant `s3:PutObject` and `s3:GetObject` to the credentials BR uses for the target task's storage, scoped to the `v1/log_restore_tables_blocklists/` directory under that task's S3 prefix. BR uses `HeadObject` to confirm the write, which requires `s3:GetObject`. Without these permissions, BR can report failure after restoring the data.

If the same IAM user or role is shared by both Backup and Restore resources, you can combine the required actions into a single policy. For more information, see [Checkpoint Restore](https://docs.pingcap.com/tidb/stable/br-checkpoint-restore) and [Backup storages](https://docs.pingcap.com/tidb/stable/backup-and-restore-storages#authentication).

### Grant permissions by AccessKey and SecretKey

To grant permissions to Amazon S3 using AccessKey and SecretKey, perform the following steps. For Ceph, MinIO, or another S3-compatible storage service, obtain credentials from that service and grant bucket permissions through its access-control mechanism. AWS IAM users and policies might not be recognized by other storage services.

1. Create an IAM user by following [Create an IAM user in your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html), and attach the [least-privilege IAM policies](#create-least-privilege-iam-policies).

2. Create an access key by following [Create an access key for yourself (console)](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-key-self-managed.html#Using_CreateAccessKey). After completion, you can obtain the AccessKey and SecretKey.

3. Create a Kubernetes Secret named `s3-secret` using the following command and enter the AccessKey and SecretKey obtained in the previous step. This Secret stores the credentials required to access S3-compatible storage services.

    ```shell
    kubectl create secret generic s3-secret --from-literal=access_key=<your-access-key> --from-literal=secret_key=<your-secret-key> --namespace=<your-namespace>
    ```

4. AWS clients support obtaining associated user permissions through the process environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. Therefore, you can grant pods access to S3-compatible storage services by setting the corresponding environment variables.

    The following example shows how to configure environment variables for TiKVGroup using [Overlay](overlay.md) (the configuration method for TiFlashGroup is the same):

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
      labels:
        pingcap.com/group: tikv
        pingcap.com/component: tikv
        pingcap.com/cluster: demo
    spec:
      template:
        spec:
          overlay:
            pod:
              spec:
                containers:
                  - name: tikv
                    env:
                      - name: "AWS_ACCESS_KEY_ID"
                        valueFrom:
                          secretKeyRef:
                            name: "s3-secret"
                            key: "access_key"
                      - name: "AWS_SECRET_ACCESS_KEY"
                        valueFrom:
                          secretKeyRef:
                            name: "s3-secret"
                            key: "secret_key"
    ```

    The following example shows how to configure environment variables for the Backup resource:

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: backup-s3
    spec:
      env:
        - name: "AWS_ACCESS_KEY_ID"
          valueFrom:
            secretKeyRef:
              name: "s3-secret"
              key: "access_key"
        - name: "AWS_SECRET_ACCESS_KEY"
          valueFrom:
            secretKeyRef:
              name: "s3-secret"
              key: "secret_key"
    ```

    The following example shows how to configure environment variables for the Restore resource:

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: restore-s3
    spec:
      env:
        - name: "AWS_ACCESS_KEY_ID"
          valueFrom:
            secretKeyRef:
              name: "s3-secret"
              key: "access_key"
        - name: "AWS_SECRET_ACCESS_KEY"
          valueFrom:
            secretKeyRef:
              name: "s3-secret"
              key: "secret_key"
    ```

### Grant permissions by associating IAM with Pod

The method of granting permissions by associating IAM with a Pod is supported by the open-source tool [kube2iam](https://github.com/jtblin/kube2iam). It enables processes within a Pod to inherit the permissions of an [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) by associating the role with the Pod.

> **Note:**
>
> - kube2iam is only applicable to Kubernetes clusters running on AWS EC2 instances. It does not support other types of nodes.
> - To use this authorization method, see the [kube2iam documentation](https://github.com/jtblin/kube2iam#usage) to set up the kube2iam environment in your Kubernetes cluster, and deploy TiDB Operator and the TiDB cluster.
> - This method is not compatible with Pods that use the [`hostNetwork`](https://kubernetes.io/docs/concepts/policy/pod-security-policy) network mode.

To grant permissions by associating IAM with a Pod, perform the following steps:

1. Follow the [IAM role creation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html) document to create an IAM role in your AWS account, and attach the [least-privilege IAM policies](#create-least-privilege-iam-policies).

2. Use the [Overlay](overlay.md) feature to associate the IAM role with the target component (TiKV or TiFlash). The following example shows how to associate the role with a TiKVGroup:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
    spec:
      template:
        spec:
          overlay:
            pod:
              annotations:
                iam.amazonaws.com/role: arn:aws:iam::123456789012:role/user
    ```

    > **Note:**
    >
    > Replace `arn:aws:iam::123456789012:role/user` with the actual ARN of the IAM role you created in step 1.

### Grant permissions by associating IAM with ServiceAccount

By associating a user's [IAM](https://aws.amazon.com/iam/) role with a [`ServiceAccount`](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#serviceaccount) resource in Kubernetes, any Pod using that ServiceAccount will inherit the permissions of the IAM role.

To grant permissions by associating IAM with a ServiceAccount, perform the following steps:

1. Follow the [IAM role creation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html) document to create an IAM role in your AWS account, and attach the [least-privilege IAM policies](#create-least-privilege-iam-policies).

2. Follow the instructions in [Create an IAM OIDC provider for your cluster](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html) to create an IAM OIDC provider for your EKS cluster.

3. Create a Kubernetes ServiceAccount named `br-s3`, and assign the IAM role to it as described in [Assign IAM roles to Kubernetes service accounts](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html).

4. Use the [Overlay](overlay.md) feature to associate the ServiceAccount with the Pod in the TiKVGroup or TiFlashGroup. The following example shows how to associate it in a TiKVGroup:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
    spec:
      template:
        spec:
          overlay:
            pod:
              spec:
                serviceAccountName: br-s3
    ```

5. Specify the `serviceAccount` in the backup or restore configuration. The following example shows how to specify it in a Backup resource:

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: backup-s3
    spec:
      serviceAccount: br-s3
    ```

## Grant permissions to a Google Cloud account

### Grant permissions by the service account

To grant permissions using a Google Cloud service account key, perform the following steps:

1. Follow the [Create service accounts](https://cloud.google.com/iam/docs/service-accounts-create) document to create a service account and generate a service account key file. Save the file as `google-credentials.json`.

2. Create a Kubernetes Secret named `gcp-secret` to store the credentials for accessing Google Cloud Storage:

    ```shell
    kubectl create secret generic gcp-secret --from-file=credentials=./google-credentials.json -n <your-namespace>
    ```

3. Follow the instructions in [Add a principal to a bucket-level policy](https://cloud.google.com/storage/docs/access-control/using-iam-permissions#bucket-add) to grant the service account created in step 1 access to the target storage bucket, and assign the `roles/storage.objectUser` role.

4. Set environment variables for the Pod. The following example shows how to configure it for a TiKVGroup:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
    spec:
      template:
        spec:
          overlay:
            pod:
              spec:
                containers:
                  - name: tikv
                    env:
                      - name: "GOOGLE_APPLICATION_CREDENTIALS"
                        valueFrom:
                          secretKeyRef:
                            name: "gcp-secret"
                            key: "credentials"
    ```

   The following example shows how to configure the Backup resource to use the Secret:

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: backup-gcp
    spec:
      gcs:
        secretName: gcp-secret
    ```

   The following example shows how to configure the Restore resource to use the Secret:

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: restore-gcp
    spec:
      gcs:
        secretName: gcp-secret
    ```

## Grant permissions to an Azure account

Azure Blob Storage provides different methods to grant permissions for different types of Kubernetes clusters. This document introduces the following two methods:

- [Grant permissions by access key](#grant-permissions-by-access-key): applicable to all types of Kubernetes clusters.
- [Grant permissions by Azure AD](#grant-permissions-by-azure-ad): suitable for scenarios requiring fine-grained access control and key rotation.

### Grant permissions by access key

Azure clients can read credentials from the environment variables `AZURE_STORAGE_ACCOUNT` and `AZURE_STORAGE_KEY`. To grant permissions using this method, perform the following steps:

1. Create a Kubernetes Secret named `azblob-secret` that stores the storage account name and key:

    ```shell
    kubectl create secret generic azblob-secret \
      --from-literal=AZURE_STORAGE_ACCOUNT=<your-storage-account> \
      --from-literal=AZURE_STORAGE_KEY=<your-storage-key> \
      --namespace=<your-namespace>
    ```

2. Use the [Overlay](overlay.md) feature to inject the Secret as environment variables into the TiKVGroup or TiFlashGroup Pod. The following example shows how to configure it for a TiKVGroup:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
    spec:
      template:
        spec:
          overlay:
            pod:
              spec:
                containers:
                  - name: tikv
                    env:
                      - name: "AZURE_STORAGE_ACCOUNT"
                        valueFrom:
                          secretKeyRef:
                            name: "azblob-secret"
                            key: "AZURE_STORAGE_ACCOUNT"
                      - name: "AZURE_STORAGE_KEY"
                        valueFrom:
                          secretKeyRef:
                            name: "azblob-secret"
                            key: "AZURE_STORAGE_KEY"
    ```

### Grant permissions by Azure AD

Azure clients can obtain access through the environment variables `AZURE_STORAGE_ACCOUNT`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET`. This method is ideal for higher security and automatic key rotation.

1. Create a Kubernetes Secret named `azblob-secret-ad` to store credentials for accessing Azure Blob Storage:

    ```shell
    kubectl create secret generic azblob-secret-ad \
      --from-literal=AZURE_STORAGE_ACCOUNT=<your-storage-account> \
      --from-literal=AZURE_CLIENT_ID=<your-client-id> \
      --from-literal=AZURE_TENANT_ID=<your-tenant-id> \
      --from-literal=AZURE_CLIENT_SECRET=<your-client-secret> \
      --namespace=<your-namespace>
    ```

2. Use the [Overlay](overlay.md) feature to inject the Secret as environment variables into the TiKVGroup or TiFlashGroup Pod. The following example shows how to configure it for a TiKVGroup:

    > **Note:**
    >
    > - When granting permissions by Azure AD, ensure the service principal has access to the target storage account.
    > - Restart the Pods after modifying the Secret to apply updated environment variables.

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiKVGroup
    metadata:
      name: tikv
    spec:
      template:
        spec:
          overlay:
            pod:
              spec:
                containers:
                  - name: tikv
                    envFrom:
                      secretRef:
                        name: "azblob-secret-ad"
    ```
