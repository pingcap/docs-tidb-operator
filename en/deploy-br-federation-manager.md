---
title: Deploy BR Federation Manager on Kubernetes
summary: Learn how to deploy BR Federation Manager on Kubernetes.
---

# Deploy BR Federation Manager on Kubernetes

This document describes how to deploy BR Federation Manager across multiple Kubernetes.

## Prerequisites

Before deploy BR Federation Manager on Kubernetes, make sure you have met the following prerequisites:

* Kubernetes version must be >= v1.12.
* You must have multiple Kubernetes clusters.
* All the Kubernetes clusters that serve as data planes have deployed TiDB Operator.

## Step 1: Generate a kubeconfig file in data planes

The BR Federation Manager manages Kubernetes clusters of data planes by accessing their API servers. To authenticate and authorize itself in the API servers, it requires a kubeconfig file. The users or service accounts in the kubeconfig file need
have at least all the permissions of **backups.pingcap.com** and **restores.pingcap.com** CRD.

You can get the kubeconfig file from the Kubernetes cluster administrator. However, if you have permission to access all the data planes, you can generate the kubeconfig file on your own.

### Step 1.1: Create RBAC resources in data planes

To enable the BR Federation Manager to manipulate Backup and Restore CR, you need to create the following resources in every data plane.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: br-federation-member
  namespace: tidb-admin
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: br-federation-manager:br-federation-member
rules:
- apiGroups:
  - pingcap.com
  resources:
  - backups
  - restores
  verbs:
  - '*'
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: br-federation-manager:br-federation-member
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: br-federation-manager:br-federation-member
subjects:
- kind: ServiceAccount
  name: br-federation-member
  namespace: tidb-admin
```

For Kubernetes >= v1.24, to let external applications access the Kubernetes API server, you need to manually create a service account secret as follows:

```yaml
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
 name: br-federation-member-secret
 annotations:
   kubernetes.io/service-account.name: "br-federation-member"
```

### Step 1.2: Generate kubeconfig files

Execute the following script for every data plane.

```shell
# for Kubernetes < 1.24
export TOKEN_SECRET_NAME=$(kubectl -n tidb-admin get serviceaccount br-federation-member -o=jsonpath='{.secrets[0].name}')
# for Kubernetes >= 1.24, the service account secret should be created manually as above, so you should use its name as value of TOKEN_SECRET_NAME
# export TOKEN_SECRET_NAME=br-federation-member-secret
export USER_TOKEN_VALUE=$(kubectl -n tidb-admin get secret/${TOKEN_SECRET_NAME} -o=go-template='{{.data.token}}' | base64 --decode)
export CURRENT_CONTEXT=$(kubectl config current-context)
export CURRENT_CLUSTER=$(kubectl config view --raw -o=go-template='{{range .contexts}}{{if eq .name "'''${CURRENT_CONTEXT}'''"}}{{ index .context "cluster" }}{{end}}{{end}}')
export CLUSTER_CA=$(kubectl config view --raw -o=go-template='{{range .clusters}}{{if eq .name "'''${CURRENT_CLUSTER}'''"}}"{{with index .cluster "certificate-authority-data" }}{{.}}{{end}}"{{ end }}{{ end }}')
export CLUSTER_SERVER=$(kubectl config view --raw -o=go-template='{{range .clusters}}{{if eq .name "'''${CURRENT_CLUSTER}'''"}}{{ .cluster.server }}{{end}}{{ end }}')
export DATA_PLANE_SYMBOL="a"

cat << EOF > {k8s-name}-kubeconfig
apiVersion: v1
kind: Config
current-context: ${DATA_PLANE_SYMBOL}
contexts:
- name: ${DATA_PLANE_SYMBOL}
  context:
    cluster: ${CURRENT_CLUSTER}
    user: br-federation-member-${DATA_PLANE_SYMBOL}
    namespace: kube-system
clusters:
- name: ${CURRENT_CLUSTER}
  cluster:
    certificate-authority-data: ${CLUSTER_CA}
    server: ${CLUSTER_SERVER}
users:
- name: br-federation-member-${DATA_PLANE_SYMBOL}
  user:
    token: ${USER_TOKEN_VALUE}
EOF
```

- The environment variable `$DATA_PLANE_SYMBOL` represents the name of the data plane cluster. Make sure that you provide a brief and unique name. In the preceding script, you use this variable as the context name for kubeconfig. The context name will be used as `k8sClusterName` in both the `VolumeBackup` and `VolumeRestore` CR.

### Step 1.3: Merge multiple kubeconfig files into one

After following the previous steps to generate kubeconfig, you now have multiple kubeconfig files. You need to merge them into a single kubeconfig file.

Assume that you have 3 kubeconfig files with file paths: `kubeconfig-path1`, `kubeconfig-path2`, `kubeconfig-path3`. To merge these files into one kubeconfig file with file path `data-planes-kubeconfig`, execute the following command:

```shell
KUBECONFIG=${kubeconfig-path1}:${kubeconfig-path2}:${kubeconfig-path3} kubectl config view --flatten > ${data-planes-kubeconfig}
```

## Step 2: Deploy BR Federation Manager in the control plane

To deploy the BR Federation Manager, you need to select one Kubernetes cluster as the control plane. The following steps should **only be executed on the control plane**.

### Step 2.1: Create CRD

The BR Federation Manager uses [Custom Resource Definition (CRD)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions) to extend Kubernetes. Before using the BR Federation Manager, you must create the CRD in your Kubernetes cluster. This operation only needs to be performed once.

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/federation-crd.yaml
```

### Step 2.2: Prepare kubeconfig secret

Now that you already have a kubeconfig file of data planes, you need to encode the kubeconfig file into a secret. Take the following steps:

1. Encode the kubeconfig file:

     ```shell
     base64 -i ${kubeconfig-path}
     ```

2. Store the output from the previous step in a secret object.

> **Note**
>
> The name of the secret and the data key of the kubeconfig field must match the following example:
>
> ```yaml
> apiVersion: v1
> kind: Secret
> metadata:
>   name: br-federation-kubeconfig
> type: Opaque
> data:
>   kubeconfig: ${encoded-kubeconfig}
> ```

### Step 2.3: Install BR Federation Manager

This section describes how to install the BR Federation Manager using [Helm 3](https://helm.sh/docs/intro/install/).

- If you prefer to use the default configuration, follow the **Quick deployment** steps.
- If you want to use a custom configuration, follow the **Custom deployment** steps.

<SimpleTab>
<div label="Quick deployment">

1. To create resources related to the BR Federation Manager, create a namespace:

    ```shell
    kubectl create ns br-fed-admin
    ```

2. In the specified namespace, create a secret that contains all the encoded kubeconfig files:

    ```shell
    kubectl create -f ${secret-path} -n br-fed-admin
    ```

3. Add the PingCAP repository:

    ```shell
    helm repo add pingcap https://charts.pingcap.org/
    ```

4. Install the BR Federation Manager:

    ```shell
    helm install --namespace br-fed-admin br-federation-manager pingcap/br-federation-manager --version v1.5.0-beta.1
    ```

</div>
<div label="Custom deployment">

1. To create resources related to the BR Federation Manager, create a namespace:

    ```shell
    kubectl create ns br-fed-admin
    ```

2. In the specified namespace, create a secret that contains all the encoded kubeconfig files:

    ```shell
    kubectl create -f ${secret-path} -n br-fed-admin
    ```

3. Add the PingCAP repository:

    ```shell
    helm repo add pingcap https://charts.pingcap.org/
    ```

4. Get the `values.yaml` file of the desired `br-federation-manager` chart for deployment.

    ```shell
    mkdir -p ${HOME}/br-federation-manager && \
    helm inspect values pingcap/br-federation-manager --version=${chart_version} > ${HOME}/br-federation-manager/values.yaml
    ```

5. Configure the BR Federation Manager by modifying fields such as `image`, `limits`, `requests`, and `replicas` according to your needs.

6. Deploy the BR Federation Manager.

    ```shell
    helm install --namespace br-fed-admin br-federation-manager pingcap/br-federation-manager --version v1.5.0-beta.1 -f ${HOME}/br-federation-manager/values.yaml && \
    kubectl get po -n br-fed-admin -l app.kubernetes.io/component=br-federation-manager
    ```

</div>
</SimpleTab>