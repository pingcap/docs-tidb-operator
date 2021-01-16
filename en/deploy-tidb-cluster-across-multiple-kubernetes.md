---
title: Deploy a TiDB Cluster across Multiple Kubernetes Clusters
summary: Learn how to deploy a TiDB cluster across multiple Kubernetes clusters.
---

# Deploy a TiDB Cluster across Multiple Kubernetes Clusters

To deploy a TiDB cluster across multiple Kubernetes clusters refers to deploying **one** TiDB cluster on multiple network-interconnected Kubernetes clusters. Each component of the cluster is distributed on multiple Kubernetes clusters to achieve disaster recovery among Kubernetes clusters. The interconnected network of Kubernetes clusters means that Pod IP can be accessed in any cluster and between clusters, and Pod FQDN records can be parsed in any cluster and between clusters.

## Prerequisites

You need to configure the Kubernetes network and DNS so that the Kubernetes cluster meets the following conditions:

- The TiDB components on each Kubernetes cluster can access the Pod IP of all TiDB components in and between clusters.
- The TiDB components on each Kubernetes cluster can parse the Pod FQDN of all TiDB components in and between clusters.

## Supported scenarios

Currently supported scenarios:

- Newly deployed a TiDB cluster across multiple Kubernetes clusters.
- Deploy new clusters that enable this feature on other Kubernetes clusters and join the clusters that also enable this feature.

Experimental supported scenarios:

- For clusters with existing data that disable this feature, change to enable this feature. If you need to use it in a production environment, it is recommended to complete this requirement through data migration.

Unsupported scenarios:

- Two interconnected existing data clusters. This scenario should be completed through data migration.

## Deploy a cluster across multiple Kubernetes clusters

If you deploy a TiDB cluster across multiple Kubernetes clusters, by default, you have already deployed Kubernetes clusters required for this scenario, and then perform the following deployment on this basis.

The following takes the deployment of two clusters as an example. Cluster one is the initial cluster. Create it according to the configuration given below. After cluster one is running normally, create cluster two according to the configuration given below. After creating and deploying clusters, two clusters run normally.

### Deploy the initial cluster

Set the following environment variables according to the actual situation. You need to set the contents of the `cluster1_name` and `cluster1_cluster_domain` variables according to your actual use, where `cluster1_name` is the cluster name of cluster one, and `cluster1_cluster_domain` is the [Cluster Domain](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#introduction) of cluster one, and `cluster1_namespace` is the namespace of cluster one.

{{< copyable "shell-regular" >}}

```bash

cluster1_name="cluster1"
cluster1_cluster_domain="cluster1.com"
cluster1_namespace="pingcap"
```

Run the following command:

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -f -n ${cluster1_namespace} -
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster1_name}"
spec:
  version: v4.0.9
  timezone: UTC
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster1_cluster_domain}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: {}
EOF
```

### Deploy the new cluster to join the initial cluster

You can wait for the cluster one to complete the deployment, then create cluster two. In actual situation, cluster two can join any existing cluster in multiple clusters.

Refer to the following example and fill in the relevant information such as `Name`, `Cluster Domain`, and `Namespace` of cluster one and cluster two according to the actual situation:

{{< copyable "shell-regular" >}}

```bash
cluster1_name="cluster1"
cluster1_cluster_domain="cluster1.com"
cluster1_namespace="pingcap"
cluster2_name="cluster2"
cluster2_cluster_domain="cluster2.com"
cluster2_namespace="pingcap"
```

Run the following command:

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -f -n ${cluster2_namespace} - 
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster2_name}"
spec:
  version: v4.0.9
  timezone: UTC
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster2_cluster_domain}"
  cluster:
    name: "${cluster1_name}"
    namespace: "${cluster1_namespace}"
    clusterDomain: "${cluster1_clusterdomain}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    config: {}
EOF
```

## Deploy the TiDB cluster with TLS enabled between TiDB components across multiple Kubernetes clusters

You can follow the steps below to enable TLS between TiDB components for TiDB clusters deployed across multiple Kubernetes clusters.

### Issue the root certificate

#### Issue the root certificate using `cfssl`

If you use `cfssl`, the CA certificate issue process is no different from the general issue process. You need to save the CA certificate created for the first time, and use this CA certificate when issuing certificates for TiDB components later. When creating a component certificate in a cluster, you do not need to create a CA certificate again and only need to complete step one to four in the [Enabling TLS between TiDB components](enable-tls-between-components.md#using-cfssl) once to complete the issue of the CA certificate. You need to start from step five for the issue of certificates between other cluster components.

#### Use the `cert-manager` system to issue a root certificate

If you use `cert-manager`, you only need to create a `CA Issuer` and a `CA Certificate` in the initial cluster, and export the `CA Secret` to other new clusters that want to join. Other clusters only need to create component certificates to issue `Issuer` (Refers to the Issuer named ${cluster_name}-tidb-issuer in the [TLS document](enable-tls-between-components.md#using-cert-manager
)). Use this CA to configure `Issuer`, the detailed process is as follows:

1. Create a `CA Issuer` and a `CA Certificate` in the initial cluster.

  Set the following environment variables according to the actual situation:

  {{< copyable "shell-regular" >}}

  ```bash
  cluster_name="cluster1"
  namespace="pingcap"
  ```

  Run the following command:

  {{< copyable "shell-regular" >}}

  ```bash
  cat <<EOF | kubectl apply -f -
    apiVersion: cert-manager.io/v1alpha2
    kind: Issuer
    metadata:
      name: ${cluster_name}-selfsigned-ca-issuer
      namespace: ${namespace}
    spec:
      selfSigned: {}
    ---
    apiVersion: cert-manager.io/v1alpha2
    kind: Certificate
    metadata:
      name: ${cluster_name}-ca
      namespace: ${namespace}
    spec:
      secretName: ${cluster_name}-ca-secret
      commonName: "TiDB"
      isCA: true
      duration: 87600h # 10yrs
      renewBefore: 720h # 30d
      issuerRef:
        name: ${cluster_name}-selfsigned-ca-issuer
        kind: Issuer
    EOF
    ```

2. Export the CA and delete irrelevant information.

  First, you need to export the `Secret` that stores the CA. The name of the `Secret` can be obtained from the `.spec.secretName` of the first step `Certificate`.

  {{< copyable "shell-regular" >}}

  ```bash
  kubectl get secret cluster1-ca-secret -n ${namespace} -o yaml > ca.yaml
  ```

  Delete irrelevant information in the `Secret YAML` file. The `YAML` file after deletion is as follows, where the information in `data` has been omitted:

  ```yaml
    apiVersion: v1
    data:
      ca.crt: LS0...LQo=
      tls.crt: LS0t....LQo=
      tls.key: LS0t...tCg==
    kind: Secret
    metadata:
      name: cluster1-ca-secret
    type: kubernetes.io/tls
    ```

3. Import the exported CA to other clusters.

   You need to configure the `namespace` so that related components can access the CA certificate:

  {{< copyable "shell-regular" >}}

    ```bash
    kubectl apply -f ca.yaml -n ${namespace}
   ·```

4. Create a component certificate in the initial cluster and the new cluster to issue `Issuer` using this CA.

    1. Create a certificate issuing `Issuer` between TiDB components in the initial cluster.

        Set the following environment variables according to the actual situation:

        {{< copyable "shell-regular" >}}

        ```bash
        cluster_name="cluster1"
        namespace="pingcap"
        ca_secret_name="cluster1-ca-secret"
        ```

        Run the following command:

        {{< copyable "shell-regular" >}}

        ```bash
        cat << EOF | kubectl apply -f -
        apiVersion: cert-manager.io/v1alpha2
        kind: Issuer
        metadata:
          name: ${cluster_name}-tidb-issuer
          namespace: ${namespace}
        spec:
          ca:
            secretName: ${ca_secret_name}
        EOF
        ```

    2. Create a certificate issuing `Issuer` between TiDB components in the new cluster.

       Set the following environment variables according to the actual situation. Among them, `ca_secret_name` needs to point to the `Secret` that you just import to store the `CA`. You can use the `cluster_name` and `namespace` in the following operations:

       {{< copyable "shell-regular" >}}
       ```bash
       cluster_name="cluster2"
       namespace="pingcap"
       ca_secret_name="cluster1-ca-secret"
       ```

       Run the following command:

       {{< copyable "shell-regular" >}}

       ```bash
       cat << EOF | kubectl apply -f -
       apiVersion: cert-manager.io/v1alpha2
       kind: Issuer
       metadata:
         name: ${cluster_name}-tidb-issuer
         namespace: ${namespace}
       spec:
         ca:
           secretName: ${ca_secret_name}
       EOF
       ```

### Issue certificates for the TiDB components of each Kubernetes cluster

You need to issue a component certificate for each TiDB component on the Kubernetes cluster. When issuing a component certificate, you need to add an authorization record ending with `.${cluster_domain}` to the hosts, for example, `${cluster_name}-pd.${namespace}.svc.${cluster_domain}`.

#### Use the cfssl system to issue certificates for TiDB components

If you use `cfssl`, take the certificate used to create the PD component as an example, the `pd-server.json` file is as follows.

Set the following environment variables according to the actual situation.

{{< copyable "shell-regular" >}}

```bash
cluster_name=cluster2
cluster_domain=cluster2.com
namespace=pingcap
```

You can create the `pd-server.json` by the following command:

{{< copyable "shell-regular" >}}

```bash
cat << EOF > pd-server.json
{
    "CN": "TiDB",
    "hosts": [
      "127.0.0.1",
      "::1",
      "${cluster_name}-pd",
      "${cluster_name}-pd.${namespace}",
      "${cluster_name}-pd.${namespace}.svc",
      "${cluster_name}-pd.${namespace}.svc.${cluster_domain}",
      "${cluster_name}-pd-peer",
      "${cluster_name}-pd-peer.${namespace}",
      "${cluster_name}-pd-peer.${namespace}.svc",
      "${cluster_name}-pd-peer.${namespace}.svc.${cluster_domain}",
      "*.${cluster_name}-pd-peer",
      "*.${cluster_name}-pd-peer.${namespace}",
      "*.${cluster_name}-pd-peer.${namespace}.svc",
      "*.${cluster_name}-pd-peer.${namespace}.svc.${cluster_domain}"
    ],
    "key": {
        "algo": "ecdsa",
        "size": 256
    },
    "names": [
        {
            "C": "US",
            "L": "CA",
            "ST": "San Francisco"
        }
    ]
}
EOF
```

#### Use the `cert-manager` system to issue certificates for TiDB components

If you use `cert-manager`, take the certificate used to create the PD component as an example, `Certifcates` is shown below.

Set the following environment variables according to the actual situation.

{{< copyable "shell-regular" >}}

```bash
cluster_name="cluster2"
namespace="pingcap"
cluster_domain="cluster2.com"
```

Run the following command:

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: ${cluster_name}-pd-cluster-secret
  namespace: ${namespace}
spec:
  secretName: ${cluster_name}-pd-cluster-secret
  duration: 8760h # 365d
  renewBefore: 360h # 15d
  organization:
  - PingCAP
  commonName: "TiDB"
  usages:
    - server auth
    - client auth
  dnsNames:
    - "${cluster_name}-pd"
    - "${cluster_name}-pd.${namespace}"
    - "${cluster_name}-pd.${namespace}.svc"
    - "${cluster_name}-pd.${namespace}.svc.${cluster_domain}"
    - "${cluster_name}-pd-peer"
    - "${cluster_name}-pd-peer.${namespace}"
    - "${cluster_name}-pd-peer.${namespace}.svc"
    - "${cluster_name}-pd-peer.${namespace}.svc.${cluster_domain}"
    - "*.${cluster_name}-pd-peer"
    - "*.${cluster_name}-pd-peer.${namespace}"
    - "*.${cluster_name}-pd-peer.${namespace}.svc"
    - "*.${cluster_name}-pd-peer.${namespace}.svc.${cluster_domain}"
  ipAddresses:
  - 127.0.0.1
  - ::1
  issuerRef:
    name: ${cluster_name}-tidb-issuer
    kind: Issuer
    group: cert-manager.io
EOF
```

You need to refer to the TLS-related documents, issue the corresponding certificates for the components, and create the `Secret` in the corresponding Kubernetes clusters.

For other TLS-related information, refer to the following documents:

- [Enable TLS between TiDB Components](enable-tls-between-components.md)
- [Enable TLS for the MySQL Client](enable-tls-for-mysql-client.md)

### Deploy the initial cluster

To deploy and initialize the cluster, use the following command. In actual use, you need to set the contents of the `cluster1_name` and `cluster1_cluster_domain` variables according to your actual situation, where `cluster1_name` is the cluster name of cluster one, `cluster1_cluster_domain` is the `Cluster Domain` of cluster one, and `cluster1_namespace` is the namespace of cluster one. The following `YAML` file enables the TLS feature, and each component starts to verify the certificates issued by the `CN` for the `CA` of `TiDB` by configuring the `cert-allowed-cn`.

Set the following environment variables according to the actual situation.

{{< copyable "shell-regular" >}}

```bash
cluster1_name="cluster1"
cluster1_cluster_domain="cluster1.com"
cluster1_namespace="pingcap"

Run the following command:

cat << EOF | kubectl apply -f -n ${cluster1_namespace} -
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster1_name}"
spec:
  version: v4.0.9
  timezone: UTC
  tlsCluster:
   enabled: true
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster1_cluster_domain}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    tlsClient:
      enabled: true
    config:
      security:
       cert-allowed-cn:
         - TiDB
EOF
```

### Deploy a new cluster to join the initial cluster

You can wait for the cluster one to complete the deployment. After completing the deployment, you can create cluster two. The related command are as follows. In actual use, cluster one might not the initial cluster. You can specify any cluster in multiple clusters to join.

Set the following environment variables according to the actual situation:

{{< copyable "shell-regular" >}}

```bash
cluster1_name="cluster1"
cluster1_cluster_domain="cluster1.com"
cluster1_namespace="pingcap"
cluster2_name="cluster2"
cluster2_cluster_domain="cluster2.com"
cluster2_namespace="pingcap"
```

Run the following command:

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -f -n ${cluster2_namespace} -
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${cluster2_name}"
spec:
  version: v4.0.9
  timezone: UTC
  tlsCluster:
   enabled: true
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster2_cluster_domain}"
  cluster:
    name: "${cluster1_name}"
    namespace: "${cluster1_namespace}"
    clusterDomain: "${cluster1_clusterdomain}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
    replicas: 1
    service:
      type: ClusterIP
    tlsClient:
      enabled: true
    config:
      security:
       cert-allowed-cn:
         - TiDB
EOF
```

## Exit and reclaim clusters that already joined

When you need to make a cluster exit from the joined TiDB cluster deployed across Kubernetes and reclaim resources, you can achieve the above requirements through the scaling in. In this scenario, some requirements of scaling in need to be met. The restrictions are as follows:

- After scaling in, the number of TiKV replicas in the cluster should be greater than the number of `max-replicas` set in PD. By default, the number of TiKV replicas needs to be greater than three.

Take the cluster two created in the above document as an example. First, set the number of copies of PD, TiKV, TiDB to `0`. If you enable other components such as TiFlash, TiCDC, Pump, etc., set the number of these copies to `0`:

{{< copyable "shell-regular" >}}

```bash
kubectl patch tc cluster2 --type merge -p '{"spec":{"pd":{"replicas":0},"tikv":{"replicas":0},"tidb":{"replicas":0}}}'
```

Wait for the status of cluster two to become `Ready`, and scale in related components to `0` copy:

{{< copyable "shell-regular" >}}

```bash
kubectl get pods -l app.kubernetes.io/instance=cluster2 -n pingcap
```

The Pod list is displayed as `No resources found.`. At this time, Pods have all been scaled in, and cluster two exits the cluster. Check the cluster status of cluster two:

{{< copyable "shell-regular" >}}

```bash
kubectl get tc cluster2
```

The result shows that cluster two is in the `Ready` status. At this time, you can delete the object and reclaim related resources.

{{< copyable "shell-regular" >}}

```bash
kubectl delete tc cluster2
```

Through the above steps, you can complete exit and resources reclaim of the joined clusters.

## Enable the existing data cluster across multiple Kubernetes cluster feature as the initial TiDB cluster

> **Warning:**
>
> Currently, this is an experimental feature and might cause data loss. Please use it carefully.

1. Update `.spec.clusterDomain` configuration:

    Configure the following parameters according to the `clusterDomain` in your Kubernetes cluster information:

    > **Warning:**
    >
    > Currently, you need to configure `clusterDomain` with correct information. After modifying the configuration, you can not modify it again.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl patch tidbcluster cluster1 --type merge -p '{"spec":{"clusterDomain":"cluster1.com"}}'
    ```

    After completing the modification, the TiDB cluster performs the rolling update.

2. Update the `PeerURL` information of PD:

    After completing the rolling update, you need to use `port-forward` to expose PD's API interface, and use API interface of PD to update `PeerURL` of PD.

    1. Use `port-forward` to expose API interface of PD:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl port-forward pods/cluster1-pd-0 2380:2380 2379:2379 -n pingcap
        ```

    2. Access `PD API` to obtain `members` information. Note that after using `port-forward`, the terminal is occupied. You need to perform the following operations in another terminal:

        {{< copyable "shell-regular" >}}

        ```bash
        curl http://127.0.0.1:2379/v2/members
        ```

        > **Note:**
        >
        > If the cluster enables TLS, you need to configure the certificate when using the curl command. For example:
        >
        > `curl --cacert /var/lib/pd-tls/ca.crt --cert /var/lib/pd-tls/tls.crt --key /var/lib/pd-tls/tls.key https://127.0.0.1:2379/v2/members`

        After running the command, the output is as follows:

        ```output
        {"members":[{"id":"6ed0312dc663b885","name":"cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster1.com","peerURLs":["http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster1.com:2379"]},{"id":"bd9acd3d57e24a32","name":"cluster1-pd-1.cluster1-pd-peer.pingcap.svc.cluster1.com","peerURLs":["http://cluster1-pd-1.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-1.cluster1-pd-peer.pingcap.svc.cluster1.com:2379"]},{"id":"e04e42cccef60246","name":"cluster1-pd-2.cluster1-pd-peer.pingcap.svc.cluster1.com","peerURLs":["http://cluster1-pd-2.cluster1-pd-peer.pingcap.svc:2380"],"clientURLs":["http://cluster1-pd-2.cluster1-pd-peer.pingcap.svc.cluster1.com:2379"]}]}
        ```

    3. Record the `id` of each PD instance, and use the `id` to update the `peerURL` of each member in turn:

        {{< copyable "shell-regular" >}}

        ```bash
        member_ID="6ed0312dc663b885"
        member_peer_url="http://cluster1-pd-0.cluster1-pd-peer.pingcap.svc.cluster1.com:2380"
        curl http://127.0.0.1:2379/v2/members/${member_ID} -XPUT \
        -H "Content-Type: application/json" -d '{"peerURLs":["${member_peer_url}"]}'
        ```

For more examples and development information, refer to [`multi-cluster`](https://github.com/pingcap/tidb-operator/tree/master/examples/multi-cluster).