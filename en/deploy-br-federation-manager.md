---
title: Deploy BR Federation Manager on Kubernetes
summary: Learn how to deploy BR Federation Manager on Kubernetes.
---

# Deploy BR Federation Manager on Kubernetes

## Prerequisites

Before deploy BR Federation Manager on Kubernetes, you should satisfy conditions below:

* you have multiple Kubernetes clusters
* Every Kubernetes clusters can communicate with each other by network
* All the Kubernetes clusters that serve as data planes have deployed TiDB-Operator

## Deploy BR Federation Manager

### Generate Kubeconfig files in all Data Planes

BR federation manager manages Kubernetes clusters of data planes by accessing their API servers.
So it needs kubeconfing files to authenticate the API servers. The user or service account in the kubeconfig file need
have all the permissions of **backups.pingcap.com, restores.pingcap.com** CRD at least.

You can get kubeconfig files from the Kubernetes cluster administrator. But we also provide a way to generate
kubeconfig files by yourself if you have the permission to access all the data planes.

#### Create Resources about RBAC

We should create the resources below in every data plane to allow br federation manager to manipulate backup and restore CR.

{{< copyable "shell-regular" >}}

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

#### Generate Kubeconfig

{{< copyable "shell-regular" >}}

```shell
export USER_TOKEN_NAME=$(kubectl -n tidb-admin get serviceaccount br-federation-member -o=jsonpath='{.secrets[0].name}')
export USER_TOKEN_VALUE=$(kubectl -n tidb-admin get secret/${USER_TOKEN_NAME} -o=go-template='{{.data.token}}' | base64 --decode)
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

Suppose that you have 3 kubeconfig files with file paths: `kubeconfig-path1`, `kubeconfig-path2`, `kubeconfig-path3`, and you want to merge them to one kubeconfing file with file path `data-planes-kubeconfig`.

{{< copyable "shell-regular" >}}

```shell
KUBECONFIG=kubeconfig-path1:kubeconfig-path2:kubeconfig-path3 kubectl config view --flatten > data-planes-kubeconfig
```

### Control Plane

You should select one Kubernetes cluster as control plane to deploy BR Federation Manager. You need only execute steps below in the control plane.

#### Create CRD

{{< copyable "shell-regular" >}}

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/federation-crd.yaml
```

#### Create Secret

You already have a kubeconfig file of data planes. Now, you need encode the kubeconfig file to a secret.

Firstly, encode the kubeconfig file by `base64 -i {kubeconfig-path}`.

Secondly, put the output of first step to a secret object.

{{< copyable "shell-regular" >}}

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: br-federation-kubeconfig
type: Opaque
data:
  kubeconfig: {encoded-kubeconfig}
```

#### Install BR Federation Manager

1. Create a namespace to create resources related to br federation manager.

{{< copyable "shell-regular" >}}

```shell
kubectl create ns br-fed-admin
```
2. Create the secret that contains all the encoded kubeconfig files in the namespace

{{< copyable "shell-regular" >}}

```shell
kubectl create -f {secret}.yaml -n br-fed-admin
```
3. Download tidb-operator repo and switch to release-1.5 branch. Enter the Helm chart directory `./charts/br-federation`
and install the helm chart.

{{< copyable "shell-regular" >}}

```shell
helm install --namespace br-fed-admin br-federation-manager . --set image=${br-federation-image}
```

#### Customize BR Federation Manager Deployment

The first two steps are same as above, and we just describe the third step. There are two ways to finish that.

##### Use Helm

Download tidb-operator repo and switch to release-1.5 branch. Enter the Helm chart directory `./charts/br-federation`
and find the file `values.yaml`. Then edit this file, replace the value of `image` if you want to set a custom image.
Then execute the command as followed to install the helm chart

{{< copyable "shell-regular" >}}

```shell
helm install --namespace br-fed-admin br-federation-manager . --values ./values.yaml
```

##### Use Deployment Directly

Install resources about RBAC.

{{< copyable "shell-regular" >}}

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    app.kubernetes.io/component: br-federation-manager
    app.kubernetes.io/instance: br-federation-manager
    app.kubernetes.io/name: br-federation
  name: br-federation-manager
  namespace: br-fed-admin
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    app.kubernetes.io/component: br-federation-manager
    app.kubernetes.io/instance: br-federation-manager
    app.kubernetes.io/name: br-federation
  name: br-federation-manager:br-federation-manager
rules:
  - apiGroups:
      - ""
    resources:
      - endpoints
      - events
    verbs:
      - create
      - get
      - list
      - watch
      - update
      - delete
      - patch
  - apiGroups:
      - federation.pingcap.com
    resources:
      - '*'
    verbs:
      - '*'
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    app.kubernetes.io/component: br-federation-manager
    app.kubernetes.io/instance: br-federation-manager
    app.kubernetes.io/name: br-federation
  name: br-federation-manager:br-federation-manager
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: br-federation-manager:br-federation-manager
subjects:
  - kind: ServiceAccount
    name: br-federation-manager
    namespace: br-fed-admin
```
{{< copyable "shell-regular" >}}

Install the `Deployment`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app.kubernetes.io/component: br-federation-manager
    app.kubernetes.io/instance: br-federation-manager
    app.kubernetes.io/name: br-federation
  name: br-federation-manager
  namespace: br-fed-admin
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/component: br-federation-manager
      app.kubernetes.io/instance: br-federation-manager
      app.kubernetes.io/name: br-federation
  template:
    metadata:
      labels:
        app.kubernetes.io/component: br-federation-manager
        app.kubernetes.io/instance: br-federation-manager
        app.kubernetes.io/name: br-federation
    spec:
      containers:
      - command:
        - /usr/local/bin/br-federation-manager
        - -v=4
        env:
        - name: NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: TZ
          value: UTC
        image: wangle1321/br-federation-manager:202307261800-1.5
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 10
          initialDelaySeconds: 30
          periodSeconds: 10
          tcpSocket:
            port: 6060
        name: br-federation-manager
        resources:
          requests:
            cpu: 80m
            memory: 50Mi
        volumeMounts:
        - mountPath: /etc/br-federation/federation-kubeconfig
          name: federation-kubeconfig
          readOnly: true
      serviceAccount: br-federation-manager
      volumes:
      - name: federation-kubeconfig
        secret:
          secretName: br-federation-kubeconfig
```

# Backup EBS across Kubernetes Clusters

## Prerequisites

1. You have latest tidb-operator and tidb-backup-manager in all data planes
2. Update latest CRD in all data planes

{{< copyable "shell-regular" >}}

```shell
kubectl create -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/crd.yaml
```
3. You have a TiDB cluster deployed across all the data planes.

## Create Volume Backup in Control Plane

1. Create a volume backup yaml `backup.yaml`. **Note**, the value of `spec.clusters.k8sClusterName` field should be same as
the **context name** of the kubeconfig which the br-federation-manager uses.

{{< copyable "shell-regular" >}}

```yaml
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeBackup
metadata:
  name: {backup-name}
spec:
  clusters:
  - k8sClusterName: {k8s-name1}
    tcName: {tc-name1}
    tcNamespace: {tc-namespace1}
  - k8sClusterName: {k8s-name2}
    tcName: {tc-name2}
    tcNamespace: {tc-namespace2}
  - ...
  template:
    br:
      sendCredToTikv: false
    s3:
      provider: aws
      region: {region-name}
      bucket: {bucket-name}
      prefix: {backup-path}
    toolImage: {br-image}
    serviceAccount: tidb-backup-manager
    cleanPolicy: Delete
```

2. Create the VolumeBackup CR in the Control Plane

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f backup.yaml -n {namespace}
```

3. After the volume backup complete, you can get the information of all the data planes in `status.backups` field, which can
be used in volume restore.

```yaml
status:
  backups:
  - backupName: fed-{backup-name}-{k8s-name1}
    backupPath: s3://{bucket-name}/{backup-path}-{k8s-name1}
    commitTs: "ts1"
    k8sClusterName: {k8s-name1}
    tcName: {tc-name1}
    tcNamespace: {tc-namespace1}
  - backupName: fed-{backup-name}-{k8s-name2}
    backupPath: s3://{bucket-name}/{backup-path}-{k8s-name2}
    commitTs: "ts2"
    k8sClusterName: {k8s-name2}
    tcName: {tc-name2}
    tcNamespace: {tc-namespace2}
  - ...
```

# Restore EBS across Kubernetes Clusters

## Prerequisites

You have a TiDB cluster deployed across all the data planes, and `spec.recoveryMode` of TiDBCluster CR in all the data planes
**must** be `true`

## Create Volume Backup in Control Plane

1. Create a volume restore yaml `restore.yaml`. You can get the value of `spec.clusters.backup.s3` from `status.backups.backupPath` of the VolumeBackup CR.
**Note**, the value of `spec.clusters.k8sClusterName` field should be same as the **context name** of the kubeconfig which the br-federation-manager uses.

{{< copyable "shell-regular" >}}

```yaml
apiVersion: federation.pingcap.com/v1alpha1
kind: VolumeRestore
metadata:
  name: {restore-name}
spec:
  clusters:
  - k8sClusterName: {k8s-name1}
    tcName: {tc-name1}
    tcNamespace: {tc-namespace1}
    backup:
      s3:
        provider: aws
        region: {region-name}
        bucket: {bucket-name}
        prefix: {backup-path1}
  - k8sClusterName: {k8s-name2}
    tcName: {tc-name2}
    tcNamespace: {tc-namespace2}
    backup:
      s3:
        provider: aws
        region: {region-name}
        bucket: {bucket-name}
        prefix: {backup-path2}
  - ...
  template:
    br:
      sendCredToTikv: false
    toolImage: {br-image}
    serviceAccount: tidb-backup-manager
    # if you want to use the warmup function, fill the 2 fields below
    # warmup: sync/async
    # warmupImage: {warmup-image}
```

2. Create the VolumeRestore CR in the Control Plane

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f restore.yaml -n {namespace}
```

# Scheduled volume backup across Kubernetes Clusters

You can set a backup policy to perform scheduled backups of the TiDB cluster, and set a backup retention policy to avoid excessive backup items. A scheduled snapshot backup is described by a custom `VolumeBackupSchedule` CR object. A volume backup is triggered at each backup time point. Its underlying implementation is the ad-hoc volume backup.

## Perform a scheduled volume backup

Perform a scheduled volume backup by doing one of the following:

+ Create the `VolumeBackupSchedule` CR, and back up cluster data as described below:

  {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f volume-backup-scheduler.yaml
    ```

  The content of `volume-backup-scheduler.yaml` is as follows:

  {{< copyable "" >}}

    ```yaml
    ---
    apiVersion: federation.pingcap.com/v1alpha1
    kind: VolumeBackupSchedule
    metadata:
      name: {scheduler-name}
      namespace: {namespace-name}
    spec:
      #maxBackups: {number}
      #pause: {bool}
      maxReservedTime: {duration}
      schedule: {cron-expression}
      backupTemplate:
        clusters:
          - k8sClusterName: {k8s-name1}
            tcName: {tc-name1}
            tcNamespace: {tc-namespace1}
            backup:
          - k8sClusterName: {k8s-name2}
            tcName: {tc-name2}
            tcNamespace: {tc-namespace2} 
          - ...
        template:
          br:
            sendCredToTikv: false
            cleanPolicy: Delete
            resources: {}
          s3:
            provider: aws
            region: {region-name}
            bucket: {bucket-name}
            prefix: {backup-path}
          serviceAccount: tidb-backup-manager
          toolImage: {br-image}
    ```
