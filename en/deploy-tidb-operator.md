---
title: Deploy TiDB Operator on Kubernetes
summary: Learn how to deploy TiDB Operator on Kubernetes.
---

# Deploy TiDB Operator on Kubernetes

This document describes how to deploy TiDB Operator on Kubernetes.

## Prerequisites

Before deploying TiDB Operator, make sure your environment meets the following software requirements:

- [Kubernetes >= v1.30](https://kubernetes.io/releases/)
- [kubectl >= v1.30](https://kubernetes.io/docs/tasks/tools/)
- [Helm >= v3.8](https://helm.sh/)

## Deploy a Kubernetes cluster

TiDB Operator runs in a Kubernetes cluster. You can set up a Kubernetes cluster using one of the following options:

- **Self-managed cluster**: set up a self-managed Kubernetes cluster using any method described in the [Kubernetes official documentation](https://kubernetes.io/docs/setup/).
- **Cloud provider**: use a Kubernetes service provided by a [Kubernetes certified cloud provider](https://kubernetes.io/docs/setup/production-environment/turnkey-solutions/).

Whichever option you choose, make sure your Kubernetes version is v1.30 or later. To quickly create a simple cluster for testing, see [Get Started](get-started.md).

## Deploy TiDB Operator CRDs

Run the following command to install the [Custom Resource Definitions (CRDs)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions) required by TiDB Operator:

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.6/tidb-operator.crds.yaml --server-side
```

## Deploy TiDB Operator

You can deploy TiDB Operator using either of the following methods:

- [Method 1: Deploy using `kubectl apply`](#method-1-deploy-using-kubectl-apply)
- [Method 2: Deploy using Helm](#method-2-deploy-using-helm)

### Method 1: Deploy using `kubectl apply`

All resources required to install TiDB Operator (except CRDs), including RBAC and Deployment objects, are packaged in the `tidb-operator.yaml` file. You can deploy everything with a single command:

```shell
kubectl apply -f https://github.com/pingcap/tidb-operator/releases/download/v2.0.0-alpha.6/tidb-operator.yaml --server-side
```

TiDB Operator will be deployed in the `tidb-admin` namespace. To verify the deployment, run:

```shell
kubectl get pods -n tidb-admin
```

Expected output:

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

### Method 2: Deploy using Helm

Use Helm to deploy all resources except CRDs:

```shell
helm install tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator --version v2.0.0-alpha.6 --namespace tidb-admin --create-namespace
```

TiDB Operator will be deployed in the `tidb-admin` namespace. To verify the deployment, run:

```shell
kubectl get pods -n tidb-admin
```

Expected output:

```shell
NAME                             READY   STATUS    RESTARTS   AGE
tidb-operator-6c98b57cc8-ldbnr   1/1     Running   0          2m
```

#### Customize the deployment

To customize deployment parameters, first export the default `values.yaml` file:

```shell
helm show values oci://ghcr.io/pingcap/charts/tidb-operator --version v2.0.0-alpha.6 > values.yaml
```

Edit the `values.yaml` file as needed, then install TiDB Operator with the customized settings:

```shell
helm install tidb-operator oci://ghcr.io/pingcap/charts/tidb-operator --version v2.0.0-alpha.6 -f values.yaml
```
