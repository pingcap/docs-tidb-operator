---
title: Perform a Canary Upgrade on TiDB Operator
summary: Learn how to perform a canary upgrade on TiDB Operator in Kubernetes. Canary upgrade avoids the unpredictable impact of a TiDB Operator upgrade on all TiDB clusters in the entire Kubernetes cluster.
---

# Perform a Canary Upgrade on TiDB Operator

If you want to upgrade TiDB Operator to a new version, and hope to limit the impact of the upgrade to avoid the unpredictable impact on all TiDB clusters in the entire Kubernetes cluster, you can perform a canary upgrade on TiDB Operator. After the canary upgrade, you can check the impact of the TiDB Operator upgrade on the canary cluster. After you confirm that the new version of TiDB Operator is working stably, you can then [upgrade TiDB Operator normally](upgrade-tidb-operator.md).

You can perform a canary upgrade only on two components: [`tidb-controller-manager`](architecture.md) and [`tidb-scheduler`](tidb-scheduler.md). Canary upgrades for [the advanced StatefulSet controller](advanced-statefulset.md) and [the admission controller](enable-admission-webhook.md) are not supported.

When you use TiDB Operator, `tidb-scheduler` is not mandatory. Refer to [tidb-scheduler and default-scheduler](tidb-scheduler.md#tidb-scheduler-and-default-scheduler) to confirm whether you need to deploy `tidb-scheduler`.

## Step 1: Configure selector for the current TiDB Operator and perform an upgrade

In `values.yaml` of the current TiDB Operator, add the following selector configuration:

```yaml
controllerManager:
  selector:
  - version!=canary
```

Refer to [Online upgrade](upgrade-tidb-operator.md#online-upgrade) or [Offline upgrade](upgrade-tidb-operator.md#offline-upgrade) to upgrade the current TiDB Operator:

```shell
helm upgrade tidb-operator pingcap/tidb-operator --version=${chart_version} -f ${HOME}/tidb-operator/values-tidb-operator.yaml
```

## Step 2: Deploy the canary TiDB Operator

1. Refer to Step 1~2 in [Online deployment](deploy-tidb-operator.md#online-deployment) and obtain the `values.yaml` file of the version you want to upgrade to. Add the following configuration in `values.yaml`:

    ```yaml
    controllerManager:
      selector:
      - version=canary
    appendReleaseSuffix: true
    #scheduler:
    #  create: false # If you do not need tidb-scheduler, set this value to false.
    advancedStatefulset:
      create: false
    admissionWebhook:
      create: false
    ```

    `appendReleaseSuffix` must be set to `true`.

    If you do not need to perform a canary upgrade on `tidb-scheduler`, configure `scheduler.create: false`. If you need to perform a canary upgrade on `tidb-scheduler`, configuring `scheduler.create: true` creates a scheduler named `{{ .scheduler.schedulerName }}-{{.Release.Name}}`. To use this scheduler in the canary TiDB Operator, in the `TidbCluster` CR, configure `spec.schedulerName` to the name of this scheduler.

    Because canary upgrades for the advanced StatefulSet controller and the admission controller are not supported, you need to set `advancedStatefulset.create: false` and `admissionWebhook.create: false`.

    For details on the parameters related to canary upgrade, refer to [related parameters](deploy-multiple-tidb-operator.md#related-parameters).

2. Deploy the canary TiDB Operator in **a different namespace** (such as `tidb-admin-canary`) with a **different [Helm Release name](https://helm.sh/docs/intro/using_helm/#three-big-concepts)** (such as `helm install tidb-operator-canary ...`):

    ```bash
    helm install tidb-operator-canary pingcap/tidb-operator --namespace=tidb-admin-canary --version=${operator_version} -f ${HOME}/tidb-operator/${operator_version}/values-tidb-operator.yaml
    ```

    Replace `${operator_version}` with the version of TiDB Operator you want to upgrade to.

## Step 3: Test the canary TiDB Operator (optional)

Before you upgrade TiDB Operator in a normal way, you can test whether the canary TiDB Operator works stably. You can test `tidb-controller-manager` and `tidb-scheduler`.

1. To test the canary `tidb-controller-manager`, set a label for a TiDB cluster by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} label tc ${cluster_name} version=canary
    ```

    Check the logs of the two deployed `tidb-controller-manager`s, and you can see this TiDB cluster with the `canary` label is now managed by the canary TiDB Operator. The steps to check logs are as follows:

    1. View the log of `tidb-controller-manager` of the current TiDB Operator:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl -n tidb-admin logs tidb-controller-manager-55b887bdc9-lzdwv
        ```

        Expected output:

        ```
        I0305 07:52:04.558973       1 tidb_cluster_controller.go:148] TidbCluster has been deleted tidb-cluster-1/basic1
        ```

    2. View the log of `tidb-controller-manager` of the canary TiDB Operator:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl -n tidb-admin-canary logs tidb-controller-manager-canary-6dcb9bdd95-qf4qr
        ```

        Expected output:

        ```
        I0113 03:38:43.859387       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic1] updated successfully
        ```

2. To test the canary upgrade of `tidb-scheduler`, modify `spec.schedulerName` of a TiDB cluster to `tidb-scheduler-canary` by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} edit tc ${cluster_name}
    ```

    After the modification, all components in the cluster will be rolling updated.

    Check the logs of `tidb-scheduler` of the canary TiDB Operator, and you can see this TiDB cluster is now using the canary `tidb-scheduler`:

    ```shell
    kubectl -n tidb-admin-canary logs tidb-scheduler-canary-7f7b6c7c6-j5p2j -c tidb-scheduler
    ```

3. After the tests, you can revert the changes in Step 3 and Step 4 so that the TiDB cluster is again managed by the current TiDB Operator.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} label tc ${cluster_name} version-
    ```

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} edit tc ${cluster_name}
    ```

## Step 4: Upgrade TiDB Operator normally

After you confirm that the canary TiDB Operator works stably, you can upgrade the TiDB Operator normally.

1. Delete the canary TiDB Operator:

    ```shell
    helm -n tidb-admin-canary uninstall ${release_name}
    ```

2. [Upgrade TiDB Operator](upgrade-tidb-operator.md) normally.
