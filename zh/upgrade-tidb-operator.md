---
title: 升级 TiDB Operator
summary: 介绍如何升级 TiDB Operator。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/upgrade-tidb-operator/']
---

# 升级 TiDB Operator

本文介绍如何升级 TiDB Operator 到指定版本。你可以选择[在线升级](#在线升级)或[离线升级](#离线升级)。

## 在线升级

如果服务器可以访问外网，你可以按照以下步骤在线升级 TiDB Operator：

1. 升级 TiDB Operator 前，确保 Helm repo 包含你需要升级的 TiDB Operator 版本。通过以下命令查看 Helm repo 包含的 TiDB Operator 版本：

    ```bash
    helm search repo -l tidb-operator
    ```

    如果输出中未包含你需要的新版本，可以使用 `helm repo update` 命令更新 repo。详情请参考[配置 Helm repo](tidb-toolkit.md#配置-helm-repo)。

2. 更新 Kubernetes 的 CustomResourceDefinition (CRD)。关于 CRD 的更多信息，请参阅 [CustomResourceDefinition](https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/)。

    * 如果 Kubernetes 版本大于等于 1.16:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl replace -f https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd.yaml && \
        kubectl get crd tidbclusters.pingcap.com
        ```

    * 如果 Kubernetes 版本小于 1.16:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl replace -f https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd_v1beta1.yaml && \
        kubectl get crd tidbclusters.pingcap.com
        ```

    本文以 TiDB Operator v1.2.6 为例，你需要替换 `${operator_version}` 为你要升级到的 TiDB Operator 版本。

3. 获取你要升级的 `tidb-operator` chart 中的 `values.yaml` 文件：

    {{< copyable "shell-regular" >}}

    ```shell
    mkdir -p ${HOME}/tidb-operator/v1.2.6 && \
    helm inspect values pingcap/tidb-operator --version=v1.2.6 > ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
    ```

4. 修改 `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` 中 `operatorImage` 镜像版本为要升级到的版本。

5. 如果你在旧版本 `values.yaml` 中设置了自定义配置，将自定义配置合并到 `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` 中。

6. 执行升级：

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade tidb-operator pingcap/tidb-operator --version=v1.2.6 -f ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
    ```

7. Pod 全部正常启动之后，运行以下命令确认 TiDB Operator 镜像版本：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get po -n tidb-admin -l app.kubernetes.io/instance=tidb-operator -o yaml | grep 'image:.*operator:'
    ```

    如果输出类似下方的结果，则表示升级成功。其中，`v1.2.6` 表示已升级到的版本号。

    ```
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    ```

    > **注意：**
    >
    > TiDB Operator 升级之后，所有 TiDB 集群中的 `discovery` Deployment 都会自动升级到对应的 TiDB Operator 版本。

## 离线升级

如果服务器没有连接外网，你可以按照以下步骤离线升级 TiDB Operator：

1. 使用有外网的机器，下载升级所需的文件和镜像。

    1. 下载 TiDB Operator 需要的 `crd.yaml` 文件。关于 CRD 的更多信息，请参阅 [CustomResourceDefinition](https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/)。

        * 如果 Kubernetes 版本大于等于 1.16:

            {{< copyable "shell-regular" >}}

            ```shell
            wget -O crd.yaml https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd.yaml
            ```

        * 如果 Kubernetes 版本小于 1.16:

            {{< copyable "shell-regular" >}}

            ```shell
            wget -O crd.yaml https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd_v1beta1.yaml
            ```

        本文以 TiDB Operator v1.2.6 为例，你需要替换 `${operator_version}` 为你要升级到的 TiDB Operator 版本。

    2. 下载 `tidb-operator` chart 包文件：

        {{< copyable "shell-regular" >}}

        ```shell
        wget http://charts.pingcap.org/tidb-operator-v1.2.6.tgz
        ```

    3. 下载 TiDB Operator 升级所需的 Docker 镜像:

        {{< copyable "shell-regular" >}}

        ```shell
        docker pull pingcap/tidb-operator:v1.2.6
        docker pull pingcap/tidb-backup-manager:v1.2.6

        docker save -o tidb-operator-v1.2.6.tar pingcap/tidb-operator:v1.2.6
        docker save -o tidb-backup-manager-v1.2.6.tar pingcap/tidb-backup-manager:v1.2.6
        ```

2. 将下载的文件和镜像上传到需要升级的服务器上，在服务器上按照以下步骤进行安装：

    1. 安装 TiDB Operator 需要的 `crd.yaml` 文件：

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl replace -f ./crd.yaml
        ```

    2. 解压 `tidb-operator` chart 包文件，并拷贝 `values.yaml` 文件到升级目录：

        {{< copyable "shell-regular" >}}

        ```shell
        tar zxvf tidb-operator-v1.2.6.tgz && \
        mkdir -p ${HOME}/tidb-operator/v1.2.6 && \
        cp tidb-operator/values.yaml ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
        ```

    3. 安装 Docker 镜像到服务器上：

        {{< copyable "shell-regular" >}}

        ```shell
        docker load -i tidb-operator-v1.2.6.tar && \
        docker load -i tidb-backup-manager-v1.2.6.tar
        ```

3. 修改 `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` 中 `operatorImage` 镜像版本为要升级到的版本。

4. 如果你在旧版本 `values.yaml` 中设置了自定义配置，将自定义配置合并到 `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` 中。

5. 执行升级：

    {{< copyable "shell-regular" >}}

    ```shell
    helm upgrade tidb-operator ./tidb-operator --version=v1.2.6 -f ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
    ```

6. Pod 全部正常启动之后，运行以下命令确认 TiDB Operator 镜像版本：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get po -n tidb-admin -l app.kubernetes.io/instance=tidb-operator -o yaml | grep 'image:.*operator:'
    ```

    如果输出类似下方的结果，则表示升级成功。其中，`v1.2.6` 表示已升级到的版本号。

    ```
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    ```

    > **注意：**
    >
    > TiDB Operator 升级之后，所有 TiDB 集群中的 `discovery` Deployment 都会自动升级到对应的 TiDB Operator 版本。
