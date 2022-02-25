---
title: Deploy a TiDB Cluster across Multiple Kubernetes Clusters
summary: Learn how to deploy a TiDB cluster across multiple Kubernetes clusters.
---

# Deploy a TiDB Cluster across Multiple Kubernetes Clusters

To deploy a TiDB cluster across multiple Kubernetes clusters refers to deploying **one** TiDB cluster on multiple interconnected Kubernetes clusters. Each component of the cluster is distributed on multiple Kubernetes clusters to achieve disaster recovery among Kubernetes clusters. The interconnected network of Kubernetes clusters means that Pod IP can be accessed in any cluster and between clusters, and Pod FQDN records can be looked up by querying the DNS service in any cluster and between clusters.

## Prerequisites

You need to configure the Kubernetes network and DNS so that the Kubernetes cluster meets the following conditions:

- The TiDB components on each Kubernetes cluster can access the Pod IP of all TiDB components in and between clusters.
- The TiDB components on each Kubernetes cluster can look up the Pod FQDN of all TiDB components in and between clusters.

To build multiple connected EKS or GKE clusters, refer to [Build Multiple Interconnected AWS EKS Clusters](build-multi-aws-eks.md) or [Build Multiple Interconnected GCP GKE Clusters](build-multi-gcp-gke.md).

## Supported scenarios

Currently supported scenarios:

- Deploy a new TiDB cluster across multiple Kubernetes clusters.
- Deploy new TiDB clusters that enable this feature on other Kubernetes clusters and join the initial TiDB cluster.

Experimentally supported scenarios:

- Enable this feature for a cluster that already has data. If you need to perform this action in a production environment, it is recommended to complete this requirement through data migration.

Unsupported scenarios:

- You cannot interconnect two clusters that already have data. You might perform this action through data migration.

## Deploy a cluster across multiple Kubernetes clusters

Before you deploy a TiDB cluster across multiple Kubernetes clusters, you need to first deploy the Kubernetes clusters required for this operation. The following deployment assumes that you have completed Kubernetes deployment.

The following takes the deployment of one TiDB cluster across two Kubernetes clusters as an example. One TidbCluster is deployed in each Kubernetes cluster.

In the following sections, `${tc_name_1}` and `${tc_name_2}` refer to the name of TidbCluster that will be deployed in each Kubernetes cluster. `${namespace_1}` and `${namespace_2}` refer to the namespace of TidbCluster. `${cluster_domain_1}` and `${cluster_domain_2}` refer to the [Cluster Domain](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#introduction) of each Kubernetes cluster.

### Step 1. Deploy the initial TidbCluster

Create and deploy the initial TidbCluster.

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -n ${namespace_1} -f -
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${tc_name_1}"
spec:
  version: v5.4.0
  timezone: UTC
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster_domain_1}"
  acrossK8s: true
  discovery: {}
  pd:
    baseImage: pingcap/pd
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    maxFailoverCount: 0
    replicas: 1
    service:
      type: ClusterIP
    config: {}
EOF
```

In the above configuration, the field `spec.acrossK8s: true` is required. It indicates that the TiDB cluster is deployed across Kubernetes clusters.

### Step 2. Deploy the new TidbCluster to join the TiDB cluster

After the initial cluster completes the deployment, you can deploy the new TidbCluster to join the TiDB cluster. You can create a new TidbCluster to join any existing TidbCluster.

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -n ${namespace_2} -f -
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${tc_name_2}"
spec:
  version: v5.4.0
  timezone: UTC
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster_domain_2}"
  acrossK8s: true
  cluster:
    name: "${tc_name_1}"
    namespace: "${namespace_1}"
    clusterDomain: "${cluster_domain_1}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tikv:
    baseImage: pingcap/tikv
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config: {}
  tidb:
    baseImage: pingcap/tidb
    maxFailoverCount: 0
    replicas: 1
    service:
      type: ClusterIP
    config: {}
EOF
```

## Deploy the TLS-enabled TiDB cluster across multiple Kubernetes clusters

You can follow the steps below to enable TLS between TiDB components for TiDB clusters deployed across multiple Kubernetes clusters.

The following takes the deployment of a TiDB cluster across two Kubernetes clusters as an example. One TidbCluster is deployed in each Kubernetes cluster.

In the following sections, `${tc_name_1}` and `${tc_name_2}` refer to the name of TidbCluster that will be deployed in each Kubernetes cluster. `${namespace_1}` and `${namespace_2}` refer to the namespace of TidbCluster. `${cluster_domain_1}` and `${cluster_domain_2}` refer to the [Cluster Domain](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/#introduction) of each Kubernetes cluster.

### Step 1. Issue the root certificate

#### Use `cfssl`

If you use `cfssl`, the CA certificate issue process is the same as the general issue process. You need to save the CA certificate created for the first time, and use this CA certificate when you issue certificates for TiDB components later.

In other words, when you create a component certificate in a cluster, you do not need to create a CA certificate again. Complete step 1 ~ 4 in [Enabling TLS between TiDB components](enable-tls-between-components.md#using-cfssl) once to issue the CA certificate. After that, start from step 5 to issue certificates between other cluster components.

#### Use `cert-manager`

If you use `cert-manager`, you only need to create a `CA Issuer` and a `CA Certificate` in the initial cluster, and export the `CA Secret` to other new clusters that want to join.

For other clusters, you only need to create a component certificate `Issuer` (refers to `${cluster_name}-tidb-issuer` in the [TLS document](enable-tls-between-components.md#using-cert-manager)) and configure the `Issuer` to use the `CA`. The detailed process is as follows:

1. Create a `CA Issuer` and a `CA Certificate` in the initial Kubernetes cluster.

    Run the following command:

    {{< copyable "shell-regular" >}}

    ```bash
    cat <<EOF | kubectl apply -f -
    apiVersion: cert-manager.io/v1
    kind: Issuer
    metadata:
      name: ${tc_name_1}-selfsigned-ca-issuer
      namespace: ${namespace}
    spec:
      selfSigned: {}
    ---
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${tc_name_1}-ca
      namespace: ${namespace_1}
    spec:
      secretName: ${tc_name_1}-ca-secret
      commonName: "TiDB"
      isCA: true
      duration: 87600h # 10yrs
      renewBefore: 720h # 30d
      issuerRef:
        name: ${tc_name_1}-selfsigned-ca-issuer
        kind: Issuer
    EOF
    ```

2. Export the CA and delete irrelevant information.

    First, you need to export the `Secret` that stores the CA. The name of the `Secret` can be obtained from `.spec.secretName` of the `Certificate` YAML file in the first step.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl get secret ${tc_name_1}-ca-secret -n ${namespace_1} -o yaml > ca.yaml
    ```

    Delete irrelevant information in the Secret YAML file. After the deletion, the YAML file is as follows (the information in `data` is omitted):

    ```yaml
    apiVersion: v1
    data:
      ca.crt: LS0...LQo=
      tls.crt: LS0t....LQo=
      tls.key: LS0t...tCg==
    kind: Secret
    metadata:
      name: ${tc_name_2}-ca-secret
    type: kubernetes.io/tls
    ```

3. Import the exported CA to other clusters.

    You need to configure the `namespace` so that related components can access the CA certificate:

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl apply -f ca.yaml -n ${namespace_2}
    ```

4. Create a component certificate `Issuer` in all Kubernetes clusters and configure it to use this CA.

    1. In the initial Kubernetes cluster, create an `Issuer` that issues certificates between TiDB components.

        Run the following command:

        {{< copyable "shell-regular" >}}

        ```bash
        cat << EOF | kubectl apply -f -
        apiVersion: cert-manager.io/v1
        kind: Issuer
        metadata:
          name: ${tc_name_1}-tidb-issuer
          namespace: ${namespace_1}
        spec:
          ca:
            secretName: ${tc_name_1}-ca-secret
        EOF
        ```

    2. In other Kubernetes clusters, create an `Issuer` that issues certificates between TiDB components.

       Run the following command:

       {{< copyable "shell-regular" >}}

       ```bash
       cat << EOF | kubectl apply -f -
       apiVersion: cert-manager.io/v1
       kind: Issuer
       metadata:
         name: ${tc_name_2}-tidb-issuer
         namespace: ${namespace_2}
       spec:
         ca:
           secretName: ${tc_name_2}-ca-secret
       EOF
       ```

### Step 2. Issue certificates for the TiDB components of each Kubernetes cluster

You need to issue a component certificate for each TiDB component on the Kubernetes cluster. When issuing a component certificate, you need to add an authorization record ending with `.${cluster_domain}` to the hosts, for example, the record of the initial TidbCluster is `${tc_name_1}-pd.${namespace_1}.svc.${cluster_domain_1}`.

#### Use the `cfssl` system to issue certificates for TiDB components

The following example shows how to use `cfssl` to create a certificate used by PD. Run the following command to create the `pd-server.json` file for the initial TidbCluster.

{{< copyable "shell-regular" >}}

```bash
cat << EOF > pd-server.json
{
    "CN": "TiDB",
    "hosts": [
      "127.0.0.1",
      "::1",
      "${tc_name_1}-pd",
      "${tc_name_1}-pd.${namespace_1}",
      "${tc_name_1}-pd.${namespace_1}.svc",
      "${tc_name_1}-pd.${namespace_1}.svc.${cluster_domain_1}",
      "${tc_name_1}-pd-peer",
      "${tc_name_1}-pd-peer.${namespace_1}",
      "${tc_name_1}-pd-peer.${namespace_1}.svc",
      "${tc_name_1}-pd-peer.${namespace_1}.svc.${cluster_domain_1}",
      "*.${tc_name_1}-pd-peer",
      "*.${tc_name_1}-pd-peer.${namespace_1}",
      "*.${tc_name_1}-pd-peer.${namespace_1}.svc",
      "*.${tc_name_1}-pd-peer.${namespace_1}.svc.${cluster_domain_1}"
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

The following example shows how to use `cert-manager` to create a certificate used by PD for the initial TidbCluster. `Certifcates` is shown below.

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: ${tc_name_1}-pd-cluster-secret
  namespace: ${namespace_1}
spec:
  secretName: ${tc_name_1}-pd-cluster-secret
  duration: 8760h # 365d
  renewBefore: 360h # 15d
  subject:
    organizations:
    - PingCAP
  commonName: "TiDB"
  usages:
    - server auth
    - client auth
  dnsNames:
    - "${tc_name_1}-pd"
    - "${tc_name_1}-pd.${namespace_1}"
    - "${tc_name_1}-pd.${namespace_1}.svc"
    - "${tc_name_1}-pd.${namespace_1}.svc.${cluster_domain_1}"
    - "${tc_name_1}-pd-peer"
    - "${tc_name_1}-pd-peer.${namespace_1}"
    - "${tc_name_1}-pd-peer.${namespace_1}.svc"
    - "${tc_name_1}-pd-peer.${namespace_1}.svc.${cluster_domain_1}"
    - "*.${tc_name_1}-pd-peer"
    - "*.${tc_name_1}-pd-peer.${namespace_1}"
    - "*.${tc_name_1}-pd-peer.${namespace_1}.svc"
    - "*.${tc_name_1}-pd-peer.${namespace_1}.svc.${cluster_domain_1}"
  ipAddresses:
  - 127.0.0.1
  - ::1
  issuerRef:
    name: ${tc_name_1}-tidb-issuer
    kind: Issuer
    group: cert-manager.io
EOF
```

You need to refer to the TLS-related documents, issue the corresponding certificates for the components, and create the `Secret` in the corresponding Kubernetes clusters.

For other TLS-related information, refer to the following documents:

- [Enable TLS between TiDB Components](enable-tls-between-components.md)
- [Enable TLS for the MySQL Client](enable-tls-for-mysql-client.md)

### Step 3. Deploy the initial TidbCluster

Run the following commands to deploy the initial TidbCluster. The following `YAML` file enables the TLS feature and configures `cert-allowed-cn`, which makes each component start to verify the certificates issued by the `CN` for the `CA` of `TiDB`.

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -n ${namespace_1} -f -
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${tc_name_1}"
spec:
  version: v5.4.0
  timezone: UTC
  tlsCluster:
   enabled: true
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster_domain_1}"
  acrossK8s: true
  discovery: {}
  pd:
    baseImage: pingcap/pd
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
    maxFailoverCount: 0
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

### Step 4. Deploy a new TidbCluster to join the TiDB cluster

After the initial cluster completes the deployment, you can deploy the new TidbCluster to join the TiDB cluster. You can create a new TidbCluster to join any existing TidbCluster.

{{< copyable "shell-regular" >}}

```bash
cat << EOF | kubectl apply -n ${namespace_2} -f -
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: "${tc_name_2}"
spec:
  version: v5.4.0
  timezone: UTC
  tlsCluster:
   enabled: true
  pvReclaimPolicy: Delete
  enableDynamicConfiguration: true
  configUpdateStrategy: RollingUpdate
  clusterDomain: "${cluster_domain_2}"
  acrossK8s: true
  cluster:
    name: "${tc_name_1}"
    namespace: "${namespace_1}"
    clusterDomain: "${cluster_domain_1}"
  discovery: {}
  pd:
    baseImage: pingcap/pd
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
        cert-allowed-cn:
          - TiDB
  tikv:
    baseImage: pingcap/tikv
    maxFailoverCount: 0
    replicas: 1
    requests:
      storage: "10Gi"
    config:
      security:
       cert-allowed-cn:
         - TiDB
  tidb:
    baseImage: pingcap/tidb
    maxFailoverCount: 0
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

## Upgrade TiDB Cluster

For a TiDB cluster deployed across Kubernetes clusters, to perform a rolling upgrade for each component Pod of the TiDB cluster, take the following steps in sequence to modify the `version` configuration of each component in the TidbCluster spec for each Kubernetes cluster.

1. Upgrade PD versions for all Kubernetes clusters.

   1. Modify the `spec.pd.version` field in the spec for the initial TidbCluster.

      ```yaml
      apiVersion: pingcap.com/v1alpha1
      kind: TidbCluster
      # ...
      spec:
        pd:
          version: ${version}
      ```

    2. Watch the status of PD Pods and wait for PD Pods in the initial TidbCluster to finish recreation and become `Running`.

    3. Repeat the first two substeps to upgrade all PD Pods in other TidbCluster.

2. Take step 1 as an example, perform the following upgrade operations in sequence:

    1. If TiFlash is deployed in clusters, upgrade the TiFlash versions for all the Kubernetes clusters that have TiFlash deployed.
    2. Upgrade TiKV versions for all Kubernetes clusters.
    3. If Pump is deployed in clusters, upgrade the Pump versions for all the Kubernetes clusters that have Pump deployed.
    4. Upgrade TiDM versions for all Kubernetes clusters.
    5. If TiCDC is deployed in clusters, upgrade the TiCDC versions for all the Kubernetes clusters that have TiCDC deployed.

## Exit and reclaim TidbCluster that already join a cross-Kubernetes cluster

When you need to make a cluster exit from the joined TiDB cluster deployed across Kubernetes and reclaim resources, you can perform the operation by scaling in the cluster. In this scenario, the following requirements of scaling-in need to be met.

- After scaling in the cluster, the number of TiKV replicas in the cluster should be greater than the number of `max-replicas` set in PD. By default, the number of TiKV replicas needs to be greater than three.

Take the second TidbCluster created in [the last section](#step-2-deploy-the-new-tidbcluster-to-join-the-tidb-cluster) as an example. First, set the number of replicas of PD, TiKV, and TiDB to `0`. If you have enabled other components such as TiFlash, TiCDC, and Pump, set the number of these replicas to `0`:

{{< copyable "shell-regular" >}}

```bash
kubectl patch tc ${tc_name_2} -n ${namespace_2} --type merge -p '{"spec":{"pd":{"replicas":0},"tikv":{"replicas":0},"tidb":{"replicas":0}}}'
```

Wait for the status of the second TidbCluster to become `Ready`, and scale in related components to `0` replica:

{{< copyable "shell-regular" >}}

```bash
kubectl get pods -l app.kubernetes.io/instance=${tc_name_2} -n ${namespace_2}
```

The Pod list shows `No resources found`. At this time, all Pods have been scaled in, and the second TidbCluster exits the cluster. Check the cluster status of the second TidbCluster:

{{< copyable "shell-regular" >}}

```bash
kubectl get tc ${tc_name_2} -n ${namespace_2}
```

The result shows that the second TidbCluster is in the `Ready` status. At this time, you can delete the object and reclaim related resources.

{{< copyable "shell-regular" >}}

```bash
kubectl delete tc ${tc_name_2} -n ${namespace_2}
```

Through the above steps, you can complete exit and resources reclaim of the joined clusters.

## Enable the feature for a cluster with existing data and make it the initial TiDB cluster

> **Warning:**
>
> Currently, this is an experimental feature and might cause data loss. Please use it carefully.

A cluster with existing data refer to a deployed TiDB cluster with the configuration `spec.acrossK8s: false`.

Depending on the network between multiple Kubernetes clusters, there are different methods.

If all Kubernetes have the same Cluster Domain, you only need to update the `spec.crossK8s` configuration of TidbCluster. Run the following command:

{{< copyable "shell-regular" >}}

```bash
kubectl patch tidbcluster cluster1 --type merge -p '{"spec":{"acrossK8s": true}}'
```

After the modification, wait for the TiDB cluster to complete rolling update.

If each Kubernetes have different Cluster Domain, you need to update the `spec.clusterDomain` and `spec.acrossK8s` fields. Take the following steps:

1. Update the `spec.clusterDomain` and `spec.acrossK8s` fields:

    Configure the following parameters according to the `clusterDomain` in your Kubernetes cluster information:

    > **Warning:**
    >
    > Currently, you need to configure `clusterDomain` with correct information. After modifying the configuration, you can not modify it again.

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl patch tidbcluster cluster1 --type merge -p '{"spec":{"clusterDomain":"cluster1.com", "acrossK8s": true}}'
    ```

    After completing the modification, the TiDB cluster performs the rolling update.

2. Update the `PeerURL` information of PD:

    After completing the rolling update, you need to use `port-forward` to expose PD's API, and use API of PD to update `PeerURL` of PD.

    1. Use `port-forward` to expose API of PD:

        {{< copyable "shell-regular" >}}

        ```bash
        kubectl port-forward pods/cluster1-pd-0 2380:2380 2379:2379 -n pingcap
        ```

    2. Access `PD API` to obtain `members` information. Note that after using `port-forward`, the terminal session is occupied. You need to perform the following operations in another terminal session:

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

After completing the above steps, this TidbCluster can be used as the initial TidbCluster for TiDB cluster deployment across Kubernetes clusters. You can refer the [section](#step-2-deploy-the-new-tidbcluster-to-join-the-tidb-cluster) to deploy other TidbCluster.

For more examples and development information, refer to [`multi-cluster`](https://github.com/pingcap/tidb-operator/tree/master/examples/multi-cluster).
