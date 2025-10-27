---
title: Enable TLS Between TiDB Components
summary: Learn how to enable TLS between TiDB components on Kubernetes.
---

# Enable TLS Between TiDB Components

This document describes how to enable Transport Layer Security (TLS) between components of the TiDB cluster on Kubernetes. The steps are as follows:

1. Generate certificates for each component group of the TiDB cluster to be created:

    Create a separate set of certificates for each component group, and save it as a Kubernetes Secret object named `${group_name}-${component_name}-cluster-secret`.

    > **Note:**
    >
    > The Secret objects you created must follow the preceding naming convention. Otherwise, the deployment of the TiDB components will fail.

2. Deploy the cluster and set the `.spec.tlsCluster.enabled` field to `true` in the Cluster Custom Resource (CR).

    > **Note:**
    >
    > After the cluster is created, do not modify this field. Otherwise, the cluster will fail to upgrade. If you need to modify this field, delete the cluster and create a new one.

3. Configure `pd-ctl` and `tikv-ctl` to connect to the cluster.

Certificates can be issued in multiple methods. This document describes how to use the `cert-manager` system to issue certificates for the TiDB cluster.

If you need to renew the existing TLS certificate, refer to [Renew and Replace the TLS Certificate](renew-tls-certificate.md).

## Step 1. Generate certificates for components of the TiDB cluster

This section describes how to issue certificates using `cert-manager`.

1. Install `cert-manager`.

    For more information, see [cert-manager installation on Kubernetes](https://cert-manager.io/docs/installation/).

2. Create an Issuer to issue certificates to the TiDB cluster.

    To configure `cert-manager`, create the Issuer resources.

    First, create a directory to save the files that `cert-manager` needs to create certificates:

    ```shell
    mkdir -p cert-manager
    cd cert-manager
    ```

    Then, create a `tidb-cluster-issuer.yaml` file with the following content:

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: Issuer
    metadata:
      name: ${cluster_name}-selfsigned-ca-issuer
      namespace: ${namespace}
    spec:
      selfSigned: {}
    ---
    apiVersion: cert-manager.io/v1
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
    ---
    apiVersion: cert-manager.io/v1
    kind: Issuer
    metadata:
      name: ${cluster_name}-certs-issuer
      namespace: ${namespace}
    spec:
      ca:
        secretName: ${cluster_name}-ca-secret
    ```

    `${cluster_name}` is the name of the cluster. The preceding YAML file creates three objects:

    - An Issuer object of the SelfSigned type, used to generate the CA certificate needed by Issuer of the CA type.
    - A Certificate object, whose `isCa` is set to `true`.
    - An Issuer, used to issue TLS certificates between TiDB components.

    Finally, execute the following command to create an Issuer:

    ```shell
    kubectl apply -f tidb-cluster-issuer.yaml
    ```

3. Generate the component certificate.

    In `cert-manager`, the Certificate resource represents the certificate interface. This certificate is issued and updated by the Issuer created in step 2.

    According to [Enable TLS Between TiDB Components](https://docs.pingcap.com/tidb/stable/enable-tls-between-components), each component needs a certificate.

    - PD certificate

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${pd_group_name}-pd-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${pd_group_name}-pd-cluster-secret
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
          - "${pd_group_name}-pd"
          - "${pd_group_name}-pd.${namespace}"
          - "${pd_group_name}-pd.${namespace}.svc"
          - "${pd_group_name}-pd-peer"
          - "${pd_group_name}-pd-peer.${namespace}"
          - "${pd_group_name}-pd-peer.${namespace}.svc"
          - "*.${pd_group_name}-pd-peer"
          - "*.${pd_group_name}-pd-peer.${namespace}"
          - "*.${pd_group_name}-pd-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        `${pd_group_name}` is the name of PDGroup, and `${cluster_name}` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `${pd_group_name}-pd-cluster-secret`.
        - Add `server auth` and `client auth` in `usages`.
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:
          - `${pd_group_name}-pd`
          - `${pd_group_name}-pd.${namespace}`
          - `${pd_group_name}-pd.${namespace}.svc`
          - `${pd_group_name}-pd-peer`
          - `${pd_group_name}-pd-peer.${namespace}`
          - `${pd_group_name}-pd-peer.${namespace}.svc`
          - `*.${pd_group_name}-pd-peer`
          - `*.${pd_group_name}-pd-peer.${namespace}`
          - `*.${pd_group_name}-pd-peer.${namespace}.svc`
        - Add the following two IPs in `ipAddresses`. You can also add other IPs according to your needs:
          - `127.0.0.1`
          - `::1`
        - Add the preceding created Issuer in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec).

        After the object is created, `cert-manager` generates a `${pd_group_name}-pd-cluster-secret` Secret object to be used by the PD component of the TiDB cluster.

    - TiKV certificate

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${tikv_group_name}-tikv-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${tikv_group_name}-tikv-cluster-secret
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
          - "${tikv_group_name}-tikv"
          - "${tikv_group_name}-tikv.${namespace}"
          - "${tikv_group_name}-tikv.${namespace}.svc"
          - "${tikv_group_name}-tikv-peer"
          - "${tikv_group_name}-tikv-peer.${namespace}"
          - "${tikv_group_name}-tikv-peer.${namespace}.svc"
          - "*.${tikv_group_name}-tikv-peer"
          - "*.${tikv_group_name}-tikv-peer.${namespace}"
          - "*.${tikv_group_name}-tikv-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        `${tikv_group_name}` is the name of TiKVGroup, and `${cluster_name}` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `${tikv_group_name}-tikv-cluster-secret`.
        - Add `server auth` and `client auth` in `usages`.
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:
          - `${tikv_group_name}-tikv`
          - `${tikv_group_name}-tikv.${namespace}`
          - `${tikv_group_name}-tikv.${namespace}.svc`
          - `${tikv_group_name}-tikv-peer`
          - `${tikv_group_name}-tikv-peer.${namespace}`
          - `${tikv_group_name}-tikv-peer.${namespace}.svc`
          - `*.${tikv_group_name}-tikv-peer`
          - `*.${tikv_group_name}-tikv-peer.${namespace}`
          - `*.${tikv_group_name}-tikv-peer.${namespace}.svc`
        - Add the following two IPs in `ipAddresses`. You can also add other IPs according to your needs:
          - `127.0.0.1`
          - `::1`
        - Add the preceding created Issuer in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec).

        After the object is created, `cert-manager` generates a `${tikv_group_name}-tikv-cluster-secret` Secret object to be used by the TiKV component of the TiDB server.

    - TiDB certificate

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${tidb_group_name}-tidb-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${tidb_group_name}-tidb-cluster-secret
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
          - "${tidb_group_name}-tidb"
          - "${tidb_group_name}-tidb.${namespace}"
          - "${tidb_group_name}-tidb.${namespace}.svc"
          - "${tidb_group_name}-tidb-peer"
          - "${tidb_group_name}-tidb-peer.${namespace}"
          - "${tidb_group_name}-tidb-peer.${namespace}.svc"
          - "*.${tidb_group_name}-tidb-peer"
          - "*.${tidb_group_name}-tidb-peer.${namespace}"
          - "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        `${tidb_group_name}` is the name of TiDBGroup, and `${cluster_name}` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `${tidb_group_name}-tidb-cluster-secret`.
        - Add `server auth` and `client auth` in `usages`.
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:
          - `${tidb_group_name}-tidb`
          - `${tidb_group_name}-tidb.${namespace}`
          - `${tidb_group_name}-tidb.${namespace}.svc`
          - `${tidb_group_name}-tidb-peer`
          - `${tidb_group_name}-tidb-peer.${namespace}`
          - `${tidb_group_name}-tidb-peer.${namespace}.svc`
          - `*.${tidb_group_name}-tidb-peer`
          - `*.${tidb_group_name}-tidb-peer.${namespace}`
          - `*.${tidb_group_name}-tidb-peer.${namespace}.svc`
        - Add the following two IPs in `ipAddresses`. You can also add other IPs according to your needs:
          - `127.0.0.1`
          - `::1`
        - Add the preceding created Issuer in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec).

        After the object is created, `cert-manager` generates a `${tidb_group_name}-tidb-cluster-secret` Secret object to be used by the TiDB component of the TiDB server.

    - Other component:

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${group_name}-${component_name}-cluster-secret
          namespace: ${namespace}
        spec:
          secretName: ${group_name}-${component_name}-cluster-secret
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
          - "${group_name}-${component_name}"
          - "${group_name}-${component_name}.${namespace}"
          - "${group_name}-${component_name}.${namespace}.svc"
          - "${group_name}-${component_name}-peer"
          - "${group_name}-${component_name}-peer.${namespace}"
          - "${group_name}-${component_name}-peer.${namespace}.svc"
          - "*.${group_name}-${component_name}-peer"
          - "*.${group_name}-${component_name}-peer.${namespace}"
          - "*.${group_name}-${component_name}-peer.${namespace}.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: ${cluster_name}-certs-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        `${group_name}` is the name of the component group, `${component_name}` is the name of the component, and `${cluster_name}` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `${group_name}-${component_name}-cluster-secret`.
        - Add `server auth` and `client auth` in `usages`.
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:
          - `${group_name}-${component_name}`
          - `${group_name}-${component_name}.${namespace}`
          - `${group_name}-${component_name}.${namespace}.svc`
          - `${group_name}-${component_name}-peer`
          - `${group_name}-${component_name}-peer.${namespace}`
          - `${group_name}-${component_name}-peer.${namespace}.svc`
          - `*.${group_name}-${component_name}-peer`
          - `*.${group_name}-${component_name}-peer.${namespace}`
          - `*.${group_name}-${component_name}-peer.${namespace}.svc`
        - Add the following two IPs in `ipAddresses`. You can also add other IPs according to your needs:
          - `127.0.0.1`
          - `::1`
        - Add the preceding created Issuer in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec).

        After the object is created, `cert-manager` generates a `${group_name}-${component_name}-cluster-secret` Secret object to be used by the component of the TiDB server.

## Step 2. Deploy the TiDB cluster

When you deploy a TiDB cluster, you can enable TLS between TiDB components, and set the `cert-allowed-cn` configuration item (for TiDB, the configuration item is `cluster-verify-cn`) to verify the CN (Common Name) of each component's certificate.

> **Note:**
>
> - For TiDB v8.3.0 and earlier versions, the PD configuration item `cert-allowed-cn` can only be set to a single value. Therefore, the `Common Name` of all authentication objects must be set to the same value.
> - Starting from TiDB v8.4.0, the PD configuration item `cert-allowed-cn` supports multiple values. You can configure multiple `Common Name` in the `cluster-verify-cn` configuration item for TiDB and in the `cert-allowed-cn` configuration item for other components as needed.
> - For more information, see [Enable TLS Between TiDB Components](https://docs.pingcap.com/tidb/stable/enable-tls-between-components/).

Perform the following steps to create a TiDB cluster and enable TLS between TiDB components:

Create the `tidb-cluster.yaml` file:

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: Cluster
metadata:
  name: ${cluster_name}
  namespace: ${namespace}
spec:
  tlsCluster:
    enabled: true
---
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: ${pd_group_name}
  namespace: ${namespace}
spec:
  cluster:
    name: ${cluster_name}
  version: {{{ .tidb_version }}}
  replicas: 3
  template:
    spec:
      config: |
        [security]
        cert-allowed-cn = ["TiDB"]
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 20Gi
---
apiVersion: core.pingcap.com/v1alpha1
kind: TiKVGroup
metadata:
  name: ${tikv_group_name}
  namespace: ${namespace}
spec:
  cluster:
    name: ${cluster_name}
  version: {{{ .tidb_version }}}
  replicas: 3
  template:
    spec:
      config: |
        [security]
        cert-allowed-cn = ["TiDB"]
      volumes:
      - name: data
        mounts:
        - type: data
        storage: 100Gi
---
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: ${tidb_group_name}
  namespace: ${namespace}
spec:
  cluster:
    name: ${cluster_name}
  version: {{{ .tidb_version }}}
  replicas: 1
  template:
    spec:
      config: |
        [security]
        cluster-verify-cn = ["TiDB"]
```

Then, execute `kubectl apply -f tidb-cluster.yaml` to create a TiDB cluster.
