---
title: Upgrade TiDB Operator
summary: Learn how to upgrade TiDB Operator to a specific version.
---

# Upgrade TiDB Operator

This document describes how to upgrade TiDB Operator to a specific version.

## Before you begin

It is not supported to upgrade TiDB Operator from v1.x to v2.x.

## Upgrade CRDs

To upgrade the Custom Resource Definitions (CRDs) for TiDB Operator, run the following command. Replace `${version}` with your target TiDB Operator version, such as `v2.0.0-alpha.3`:

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/${version}/tidb-operator.crds.yaml --server-side
```

## Upgrade TiDB Operator components

You can upgrade TiDB Operator components using one of the following methods:

* [Method 1: use `kubectl apply`](#method-1-upgrade-using-kubectl-apply)
* [Method 2: use Helm](#method-2-upgrade-using-helm)

### Method 1: Upgrade using `kubectl apply`

To upgrade TiDB Operator components, run the following command:

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/${version}/tidb-operator.yaml --server-side
```

This command upgrades TiDB Operator deployed in the `tidb-admin` namespace. To verify that the upgrade is successful, run the following command:

```shell
kubectl get pods -n tidb-admin
```

Example output:

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

### Method 2: Upgrade using Helm

If you deploy TiDB Operator using Helm, you can upgrade it using the `helm upgrade` command.

To upgrade TiDB Operator, run the following command:

```shell
helm upgrade tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator --version=${version} --namespace=tidb-admin
```

In the preceding command:

* `tidb-operator`: the Helm release name for TiDB Operator. Replace it if you use a different name.
* `${version}`: the target TiDB Operator version, such as `v2.0.0-alpha.3`.
* `--namespace=tidb-admin`: the namespace where TiDB Operator is deployed. Replace it with your actual namespace if different.

After the upgrade is complete, you can check the Pod status with the following command to verify that the upgrade is successful:

```shell
kubectl get pods -n tidb-admin
```

#### Upgrade with a custom configuration

If you previously used a custom configuration during deployment or previous upgrades (that is, you modified the `values.yaml` file), make sure to use these custom configurations during this upgrade. Perform the following steps:

1. Export the `values.yaml` file used by the current deployment:

    ```shell
    helm get values tidb-operator -n tidb-admin > values.yaml
    ```

2. Get the default configuration file `values-new.yaml` for the target version:

    ```shell
    helm show values oci://ghcr.io/pingcap/charts/tidb-operator --version=${version} > values-new.yaml
    ```

3. Compare the `values.yaml` and `values-new.yaml` files and merge your custom configuration items into `values-new.yaml`.

4. Use the updated `values-new.yaml` file to perform the upgrade:

    ```shell
    helm upgrade tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator --version=${version} -f values-new.yaml --namespace=tidb-admin
    ```
