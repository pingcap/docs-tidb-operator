---
title: Upgrade TiDB Operator
summary: Learn how to perform online upgrade and offline upgrade to TiDB Operator in the Kubernetes cluster.
aliases: ['/docs/tidb-in-kubernetes/dev/upgrade-tidb-operator/']
---

# Upgrade TiDB Operator

This document describes how to upgrade TiDB Operator to a specific version. You can choose either [online upgrade](#online-upgrade) or [offline upgrade](#offline-upgrade).

## Online upgrade

If your server has access to the internet, you can perform online upgrade by taking the following steps:

1. Before upgrading TiDB Operator, make sure that the Helm repo contains the TiDB Operator version you want to upgrade to. To check the TiDB Operator versions in the Helm repo, run the following command:

    ```bash
    helm search repo -l tidb-operator
    ```

    If the command output does not include the version you need, update the repo using the `helm repo update` command. For details, refer to [Configure the Help repo](tidb-toolkit.md#configure-the-helm-repo).

2. Update [CustomResourceDefinition](https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/) (CRD) for Kubernetes:

    * If your Kubernetes version >= v1.16:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl replace -f https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd.yaml && \
        kubectl get crd tidbclusters.pingcap.com
        ```

    * If your Kubernetes version < v1.16:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl replace -f https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd_v1beta1.yaml && \
        kubectl get crd tidbclusters.pingcap.com
        ```

    This document takes TiDB v1.2.6 as an example. You can replace `${operator_version}` with the specific version you want to upgrade to.

3. Get the `values.yaml` file of the `tidb-operator` chart:

    {{< copyable "shell-regular" >}}

    ```bash
    mkdir -p ${HOME}/tidb-operator/v1.2.6 && \
    helm inspect values pingcap/tidb-operator --version=v1.2.6 > ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
    ```

4. In the `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` file, modify the `operatorImage` version to the new TiDB Operator version.

5. If you have added customized configuration in the old `values.yaml` file, merge your customized configuration to the `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` file.

6. Perform upgrade:

    {{< copyable "shell-regular" >}}

    ```bash
    helm upgrade tidb-operator pingcap/tidb-operator --version=v1.2.6 -f ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
    ```

7. After all the Pods start normally, check the image of TiDB Operator:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl get po -n tidb-admin -l app.kubernetes.io/instance=tidb-operator -o yaml | grep 'image:.*operator:'
    ```

    If you see a similar output as follows, TiDB Operator is successfully upgraded. `v1.2.6` represents the TiDB Operator version you have upgraded to.

    ```
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    ```

    > **Note:**
    >
    > After TiDB Operator is upgraded, the `discovery` Deployment in all TiDB clusters is automatically upgraded to the corresponding version of TiDB Operator.

## offline upgrade

If your server cannot access the Internet, you can offline upgrade by taking the following steps:

1. Download the files and images required for the upgrade using a machine with Internet access:

    1. Download the `crd.yaml` file for the new TiDB Operator version. For more information about CRD, see [CustomResourceDefinition](https://kubernetes.io/docs/tasks/access-kubernetes-api/custom-resources/custom-resource-definitions/).

        * If your Kubernetes version >= v1.16:

            {{< copyable "shell-regular" >}}

            ```bash
            wget -O crd.yaml https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd.yaml
            ```

        * If your Kubernetes version < v1.16:

            {{< copyable "shell-regular" >}}

            ```bash
            wget -O crd.yaml https://raw.githubusercontent.com/pingcap/tidb-operator/${operator_version}/manifests/crd_v1beta1.yaml
            ```

        This document takes TiDB v1.2.6 as an example. You can replace `${operator_version}` with the specific version you want to upgrade to.

    2. Download the `tidb-operator` chart package file.

        {{< copyable "shell-regular" >}}

        ```bash
        wget http://charts.pingcap.org/tidb-operator-v1.2.6.tgz
        ```

    3. Download the Docker images required for the new TiDB Operator version:

        {{< copyable "shell-regular" >}}

        ```bash
        docker pull pingcap/tidb-operator:v1.2.6
        docker pull pingcap/tidb-backup-manager:v1.2.6

        docker save -o tidb-operator-v1.2.6.tar pingcap/tidb-operator:v1.2.6
        docker save -o tidb-backup-manager-v1.2.6.tar pingcap/tidb-backup-manager:v1.2.6
        ```

2. Upload the downloaded files and images to the server where TiDB Operator is deployed, and install the new TiDB Operator version:

    1. Install the `crd.yaml` file for TiDB Operator:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl replace -f ./crd.yaml
        ```

    2. Unpack the `tidb-operator` chart package file, and copy the `values.yaml` file to the directory of the new TiDB Operator:

        {{< copyable "shell-regular" >}}

        ```bash
        tar zxvf tidb-operator-v1.2.6.tgz && \
        mkdir -p ${HOME}/tidb-operator/v1.2.6 && \
        cp tidb-operator/values.yaml ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
        ```

    3. Install the Docker images on the server:

        {{< copyable "shell-regular" >}}

        ```bash
        docker load -i tidb-operator-v1.2.6.tar && \
        docker load -i tidb-backup-manager-v1.2.6.tar
        ```

3. In the `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` file, modify the `operatorImage` version to the new TiDB Operator version.

4. If you have added customized configuration in the old `values.yaml` file, merge your customized configuration to the `${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml` file.

5. Perform upgrade:

    {{< copyable "shell-regular" >}}

    ```bash
    helm upgrade tidb-operator ./tidb-operator --version=v1.2.6 -f ${HOME}/tidb-operator/v1.2.6/values-tidb-operator.yaml
    ```

6. After all the Pods start normally, check the image version of TiDB Operator:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl get po -n tidb-admin -l app.kubernetes.io/instance=tidb-operator -o yaml | grep 'image:.*operator:'
    ```

    If you see a similar output as follows, TiDB Operator is successfully upgraded. `v1.2.6` represents the TiDB Operator version you have upgraded to.

    ```
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    image: pingcap/tidb-operator:v1.2.6
    image: docker.io/pingcap/tidb-operator:v1.2.6
    ```

    > **Note:**
    >
    > After TiDB Operator is upgraded, the `discovery` Deployment in all TiDB clusters is automatically upgraded to the corresponding version of TiDB Operator.
