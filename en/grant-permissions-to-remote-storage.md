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

### Grant permissions by AccessKey and SecretKey

To grant permissions to S3-compatible storage using AccessKey and SecretKey, perform the following steps:

1. Create an IAM user by following [Create an IAM user in your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) and grant the required permissions. Because backup and restore operations require access to AWS S3 storage, grant the `AmazonS3FullAccess` permission to the IAM user.

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

1. Follow the [IAM role creation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html) document to create an IAM role in your AWS account and grant it the `AmazonS3FullAccess` policy.

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

1. Follow the [IAM role creation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html) document to create an IAM role in your AWS account and grant it the `AmazonS3FullAccess` policy.

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
