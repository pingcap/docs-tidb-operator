---
title: 远程存储访问授权
summary: 介绍如何授权访问远程存储从而实现 TiDB 集群的备份和恢复。
---

# 远程存储访问授权

本文详细描述了如何授权访问远程存储，以实现备份 TiDB 集群数据到远程存储或从远程存储恢复备份数据到 TiDB 集群。

## AWS 账号授权

在 AWS 云环境中，不同类型的 Kubernetes 集群支持不同的权限授予方式。本文介绍以下三种授权方式：

- [通过 AccessKey 和 SecretKey 授权](#通过-accesskey-和-secretkey-授权)：适用于自建 Kubernetes 集群和 AWS EKS 集群。
- [通过 IAM 绑定 Pod 授权](#通过-iam-绑定-pod-授权)：适用于自建 Kubernetes 集群。
- [通过 IAM 绑定 ServiceAccount 授权](#通过-iam-绑定-serviceaccount-授权)：只适用于 AWS EKS 集群。

### 创建存储桶级 IAM 策略

在使用任一 AWS 授权方式之前，请创建一个仅允许访问备份和恢复所用 S3 存储桶的客户托管 IAM 策略。不要附加账号级 AWS 托管 S3 策略，因为此类策略允许访问账号中的所有 S3 存储桶。

以下策略包含备份和恢复所需的最小 S3 权限。请将 `<bucket-name>` 替换为备份存储桶的名称，然后将该策略附加到 TiDB 使用的 IAM 用户或角色：

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

使用此策略时，请注意以下情况：

- 如果 Backup 和 Restore 资源通过同一个 IAM 用户或角色访问不同的存储桶，请将每个所需存储桶的存储桶 ARN 和对象 ARN 添加到对应的 `Resource` 元素中。不要将其替换为允许访问无关存储桶的通配符。
- 对于 AWS 中国区域或 AWS GovCloud (US) 区域中的存储桶，请分别将两个 ARN 中的 `aws` 分区替换为 `aws-cn` 或 `aws-us-gov`。
- 如果 Backup 资源设置了 `.spec.s3.acl`，且没有其他策略授予相应权限，请将 `s3:PutObjectAcl` 添加到对象操作中。
- 如果存储桶使用客户托管 AWS KMS 密钥进行服务端加密，请为 IAM 用户或角色授予该密钥的 `kms:GenerateDataKey` 和 `kms:Decrypt` 权限，以用于备份或会写入检查点元数据的恢复版本（包括 BR v8.0.0）。对于只读恢复，请授予 `kms:Decrypt` 权限。还需确保 KMS 密钥策略直接允许这些主体执行所需操作，或者允许通过 IAM 策略授予这些权限。

恢复所需的权限取决于 BR 版本。使用 BR v8.0.0 时，请保留 `s3:ListBucket`、`s3:GetObject`、`s3:PutObject` 和 `s3:DeleteObject` 权限，因为恢复过程会在 S3 中写入和删除检查点元数据。对于其他 BR 版本，请遵循对应版本文档中的权限要求。有关更多信息，请参阅[备份存储](https://docs.pingcap.com/zh/tidb/stable/backup-and-restore-storages#认证)。

### 通过 AccessKey 和 SecretKey 授权

按照以下步骤配置 AccessKey 和 SecretKey，以授权访问兼容 S3 的存储服务：

1. 参考[在 AWS 账户中创建 IAM 用户](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)，创建一个 IAM 用户，并附加[存储桶级 IAM 策略](#创建存储桶级-iam-策略)。

2. 参考[为自己创建访问密钥（控制台）](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-key-self-managed.html#Using_CreateAccessKey)，为 IAM 用户创建访问密钥 (Access Key)。完成后，你将获得 AccessKey 和 SecretKey。

3. 使用以下命令创建一个名为 `s3-secret` 的 Kubernetes Secret，并填入上一步中获取的 AccessKey 和 SecretKey。该 Secret 用于存储访问 S3 兼容存储服务所需的凭证。

    ```shell
    kubectl create secret generic s3-secret --from-literal=access_key=<your-access-key> --from-literal=secret_key=<your-secret-key> --namespace=<your-namespace>
    ```

4. AWS 客户端支持通过进程环境变量 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY` 获取与之相关联的用户权限。因此，可以通过为 Pod 设置相应的环境变量，使其具备访问兼容 S3 的存储服务的权限。

    以下示例展示如何通过 [Overlay](overlay.md) 方式为 TiKVGroup 配置环境变量（TiFlashGroup 的配置方式相同）：

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

    以下是为 Backup 配置环境变量的示例：

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

    以下是为 Restore 配置环境变量的示例：

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

### 通过 IAM 绑定 Pod 授权

通过 IAM 绑定 Pod 的授权方式由开源工具 [kube2iam](https://github.com/jtblin/kube2iam) 提供，通过将 [IAM 角色](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) 绑定到 Pod，实现 Pod 中的进程继承 IAM 角色的访问权限。

> **注意：**
>
> - kube2iam 仅适用于运行在 AWS EC2 实例上的 Kubernetes 集群，不支持其他类型的节点。
> - 使用该授权模式时，可以参考 [kube2iam 文档](https://github.com/jtblin/kube2iam#usage)在 Kubernetes 集群中创建 kube2iam 环境，并且部署 TiDB Operator 以及 TiDB 集群。
> - 该模式不适用于使用 [`hostNetwork`](https://kubernetes.io/zh-cn/docs/concepts/policy/pod-security-policy) 网络模式的 Pod。

通过 IAM 绑定 Pod 授权的步骤如下：

1. 参考 [IAM 角色创建](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html)，为你的 AWS 账号创建一个 IAM 角色，并附加[存储桶级 IAM 策略](#创建存储桶级-iam-策略)。

2. 通过 [Overlay](overlay.md) 方式为目标组件（TiKV 或 TiFlash）绑定 IAM 角色。以下示例展示如何为 TiKVGroup 添加绑定：

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

    > **注意：**
    >
    > 你需要将 `arn:aws:iam::123456789012:role/user` 替换为步骤 1 中创建的 IAM 角色的实际 ARN。

### 通过 IAM 绑定 ServiceAccount 授权

通过将用户的 [IAM](https://aws.amazon.com/cn/iam/) 角色与 Kubernetes 中的 [`ServiceAccount`](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/admission-controllers/#serviceaccount) 资源绑定，使用该 ServiceAccount 的 Pod 将继承该角色的权限。

通过 IAM 绑定 ServiceAccount 授权的步骤如下：

1. 参考 [IAM 角色创建](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html)，为你的 AWS 账号创建一个 IAM 角色，并附加[存储桶级 IAM 策略](#创建存储桶级-iam-策略)。

2. 参考[为集群创建 IAM OIDC 提供商](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)，为 EKS 集群创建一个 IAM OIDC 提供商。

3. 创建一个名为 `br-s3` 的 Kubernetes ServiceAccount，并参考[为 Kubernetes 服务账户分配 IAM 角色](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html)将创建的 IAM 角色分配给该 ServiceAccount。

4. 通过 [Overlay](overlay.md) 方式，将 ServiceAccount 绑定到 TiKVGroup 或 TiFlashGroup 的 Pod，以 TiKVGroup 为例：

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

5. 在 Backup 或 Restore 中指定 `serviceAccount`，以 Backup 为例：

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: backup-s3
    spec:
      serviceAccount: br-s3
    ```

## Google Cloud 账号授权

### 通过服务账号密钥授权

通过 Google Cloud 服务账号密钥授权的步骤如下：

1. 参考[创建服务账号](https://cloud.google.com/iam/docs/service-accounts-create)，创建一个服务账号，并生成服务账号密钥文件，保存为 `google-credentials.json`。

2. 使用以下命令创建一个名为 `gcp-secret` 的 Kubernetes Secret，用于存放 Google Cloud Storage 的访问凭证：

    ```shell
    kubectl create secret generic gcp-secret --from-file=credentials=./google-credentials.json -n <your-namespace>
    ```

3. 参考[将主账号添加到存储桶级层政策中](https://cloud.google.com/storage/docs/access-control/using-iam-permissions#bucket-add)，授予第 1 步中创建的服务账号对目标存储桶的访问权限，同时授予 `roles/storage.objectUser` 角色。

4. 为 Pod 设置环境变量，以 TiKVGroup 为例：

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

    下面是给 Backup 配置使用该 Secret 的示例：

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Backup
    metadata:
      name: backup-gcp
    spec:
      gcs:
        secretName: gcp-secret
    ```

    下面是给 Restore 配置使用该 Secret 的示例：

    ```yaml
    apiVersion: br.pingcap.com/v1alpha1
    kind: Restore
    metadata:
      name: restore-gcp
    spec:
      gcs:
        secretName: gcp-secret
    ```

## Azure 账号授权

在 Azure 云环境中，不同类型的 Kubernetes 集群可以通过不同方式授权访问 Azure Blob Storage。本文介绍以下两种常用的权限授予方式：

- [通过访问密钥授权](#通过访问密钥授权)：适用于所有类型的 Kubernetes 集群。
- [通过 Azure AD 授权](#通过-azure-ad-授权)：适用于需要更细粒度权限控制和密钥轮换的场景。

### 通过访问密钥授权

Azure 客户端支持从进程环境变量 `AZURE_STORAGE_ACCOUNT` 和 `AZURE_STORAGE_KEY` 中读取访问凭证。你可以通过以下步骤授权：

1. 使用以下命令创建一个名为 `azblob-secret` 的 Kubernetes Secret，将存储账户名称和密钥写入 Secret：

    ```shell
    kubectl create secret generic azblob-secret \
      --from-literal=AZURE_STORAGE_ACCOUNT=<your-storage-account> \
      --from-literal=AZURE_STORAGE_KEY=<your-storage-key> \
      --namespace=<your-namespace>
    ```

2. 通过 [Overlay](overlay.md) 方式，将该 Secret 绑定到 TiKVGroup 或 TiFlashGroup Pod 的环境变量，以 TiKVGroup 为例：

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

### 通过 Azure AD 授权

Azure 客户端支持通过环境变量 `AZURE_STORAGE_ACCOUNT`、`AZURE_CLIENT_ID`、`AZURE_TENANT_ID` 和 `AZURE_CLIENT_SECRET` 获取与之相关联的用户或角色的权限。此方式适合需要更高安全性及自动密钥轮换的场景。

1. 创建一个名为 `azblob-secret-ad` 的 Kubernetes Secret，存放用于访问 Azure Blob Storage 的凭证：

    ```shell
    kubectl create secret generic azblob-secret-ad \
      --from-literal=AZURE_STORAGE_ACCOUNT=<your-storage-account> \
      --from-literal=AZURE_CLIENT_ID=<your-client-id> \
      --from-literal=AZURE_TENANT_ID=<your-tenant-id> \
      --from-literal=AZURE_CLIENT_SECRET=<your-client-secret> \
      --namespace=<your-namespace>
    ```

2. 通过 [Overlay](overlay.md) 方式，将该 Secret 绑定到 TiKVGroup 或 TiFlashGroup Pod 的环境变量，以 TiKVGroup 为例：

    > **注意：**
    >
    > - 通过 Azure AD 授权时，需确保服务主体已被授予目标存储账户的访问权限。
    > - 修改 Secret 后，需重启相关 Pod 以加载更新的环境变量。

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
