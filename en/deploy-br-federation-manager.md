---
title: Deploy BR Federation Manager on Kubernetes
summary: Learn how to deploy BR Federation Manager on Kubernetes.
aliases: ['/docs/tidb-in-kubernetes/dev/deploy-br-federation-manager/']
---

# Deploy BR Federation Manager on Kubernetes

This document describes how to deploy BR Federation Manager across multiple Kubernetes.

## Prerequisites

Before deploy BR Federation Manager on Kubernetes, you should satisfy conditions below:

* Kubernetes >= v1.12
* you have multiple Kubernetes clusters
* All the Kubernetes clusters that serve as data planes have deployed TiDB-Operator

## Deploy BR Federation Manager

### Generate Kubeconfig file in all Data Planes

BR federation manager manages Kubernetes clusters of data planes by accessing their API servers.
So it needs kubeconfig to authenticate and authorize in the API servers. The users or service accounts in the kubeconfig file need
have all the permissions of **backups.pingcap.com, restores.pingcap.com** CRD at least.

You can get the kubeconfig file from the Kubernetes cluster administrator. But we also provide a way to generate
the kubeconfig file by yourself if you have the permission to access all the data planes.

#### Create Resources about RBAC in Data Plane

We should create the resources below in every data plane to allow br federation manager to manipulate backup and restore CR.

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

For Kubernetes with version >= 1.24, you should create service account secret manually for external applications to access the Kubernetes API server.

```yaml
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
 name: br-federation-member-secret
 annotations:
   kubernetes.io/service-account.name: "br-federation-member"
```

#### Generate Kubeconfig files

You should execute the script below for every data plane.

{{< copyable "shell-regular" >}}

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

> **Note:**
>
> The environment variable `$DATA_PLANE_SYMBOL` indicates the name of the data plane cluster, and you should provide a brief and unique name.
> We use it as the context name of kubeconfig in the script above and the context name will be used as `k8sClusterName`
> in the `VolumeBackup` and `VolumeRestore` CR.

#### Merge multiple kubeconfig files to one

If you follow the step above to generate kubeconfig, you may have multiple kubeconfig files. We should merge them to one kubeconfig file.

Suppose that you have 3 kubeconfig files with file paths: `kubeconfig-path1`, `kubeconfig-path2`, `kubeconfig-path3`,
and you want to merge them to one kubeconfig file with file path `data-planes-kubeconfig`. You can execute the command below to merge kubeconfig files.

{{< copyable "shell-regular" >}}

```shell
KUBECONFIG=${kubeconfig-path1}:${kubeconfig-path2}:${kubeconfig-path3} kubectl config view --flatten > ${data-planes-kubeconfig}
```

### Deploy BR Federation Manager in Control Plane

You should select one Kubernetes cluster as control plane to deploy BR Federation Manager. You need only execute steps below in the control plane.

#### Create CRD

BR Federation Manager uses [Custom Resource Definition (CRD)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions) to extend Kubernetes.
Therefore, to use BR Federation Manager, you must first create the CRD, which is a one-time job in your Kubernetes cluster.

{{< copyable "shell-regular" >}}

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/federation-crd.yaml
```

#### Prepare Kubeconfig Secret

You already have a kubeconfig file of data planes. Now, you need encode the kubeconfig file to a secret.
Firstly, encode the kubeconfig file by `base64 -i ${kubeconfig-path}`. Secondly, put the output of first step to a secret object.
**Note, the name of the secret and the data key of kubeconfig field must be equal to which is in the example below**.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: br-federation-kubeconfig
type: Opaque
data:
  kubeconfig: ${encoded-kubeconfig}
```

#### Install BR Federation Manager

This section describes how to install BR Federation Manager using [Helm 3](https://helm.sh/docs/intro/install/).

##### Quick Deployment

1. Create a namespace to create resources related to br federation manager.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl create ns br-fed-admin
    ```

2. Create the secret that contains all the encoded kubeconfig files in the namespace.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl create -f ${secret-path} -n br-fed-admin
    ```

3. Add the PingCAP repository.

    {{< copyable "shell-regular" >}}
    
    ```shell
    helm repo add pingcap https://charts.pingcap.org/
    ```

4. Install BR Federation Manager.

    {{< copyable "shell-regular" >}}
    
    ```shell
    helm install --namespace br-fed-admin br-federation-manager pingcap/br-federation-manager --version v1.5.0-beta.1
    ```

##### Custom Deployment

1. Create a namespace to create resources related to br federation manager.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl create ns br-fed-admin
    ```

2. Create the secret that contains all the encoded kubeconfig files in the namespace.

    {{< copyable "shell-regular" >}}
    
    ```shell
    kubectl create -f ${secret-path} -n br-fed-admin
    ```

3. Add the PingCAP repository.

    {{< copyable "shell-regular" >}}
    
    ```shell
    helm repo add pingcap https://charts.pingcap.org/
    ```

4. Get the `values.yaml` file of the `br-federation-manager` chart you want to deploy.

    {{< copyable "shell-regular" >}}
    
    ```shell
    mkdir -p ${HOME}/br-federation-manager && \
    helm inspect values pingcap/br-federation-manager --version=${chart_version} > ${HOME}/br-federation-manager/values.yaml
    ```

5. Configure BR Federation Manager. For example, you can modify `image` field if you build the image by yourself. Also, you can modify other fields such as `limits`, `requests`, and `replicas` as needed.
6. Deploy BR Federation Manager.

    {{< copyable "shell-regular" >}}
    
    ```shell
    helm install --namespace br-fed-admin br-federation-manager pingcap/br-federation-manager --version v1.5.0-beta.1 -f ${HOME}/br-federation-manager/values.yaml && \
    kubectl get po -n br-fed-admin -l app.kubernetes.io/component=br-federation-manager
    ```
