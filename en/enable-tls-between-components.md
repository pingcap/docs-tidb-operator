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

Certificates can be issued in multiple methods. This document describes two methods. You can choose either of them to issue certificates for the TiDB cluster:

- Use `cfssl`
- Use `cert-manager`

If you need to renew the existing TLS certificate, refer to [Renew and Replace the TLS Certificate](renew-tls-certificate.md).

## Step 1. Generate certificates for components of the TiDB cluster

This section describes how to issue certificates using two methods: `cfssl` and `cert-manager`.

### Use `cfssl`

1. Download `cfssl` and initialize the certificate issuer:

    ```shell
    mkdir -p ~/bin
    curl -s -L -o ~/bin/cfssl https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
    curl -s -L -o ~/bin/cfssljson https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
    chmod +x ~/bin/{cfssl,cfssljson}
    export PATH=$PATH:~/bin

    mkdir -p cfssl
    cd cfssl
    ```

2. Generate the `ca-config.json` configuration file:

    > **Note:**
    >
    > - All TiDB components share the same set of TLS certificates for inter-component communication to encrypt traffic between clients and servers. Therefore, when generating the CA configuration, you must specify both `server auth` and `client auth`.
    > - It is recommended that all component certificates be issued by the same CA.

    ```shell
    cat << EOF > ca-config.json
    {
        "signing": {
            "default": {
                "expiry": "8760h"
            },
            "profiles": {
                "internal": {
                    "expiry": "8760h",
                    "usages": [
                        "signing",
                        "key encipherment",
                        "server auth",
                        "client auth"
                    ]
                }
            }
        }
    }
    EOF
    ```

3. Generate the `ca-csr.json` configuration file:

    ```shell
    cat << EOF > ca-csr.json
    {
        "CN": "TiDB",
        "CA": {
            "expiry": "87600h"
        },
        "key": {
            "algo": "rsa",
            "size": 2048
        },
        "names": [
            {
                "C": "US",
                "L": "CA",
                "O": "PingCAP",
                "ST": "Beijing",
                "OU": "TiDB"
            }
        ]
    }
    EOF
    ```

4. Generate CA by the configured option:

    ```shell
    cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
    ```

5. Generate certificates:

    In this step, you need to generate a set of certificates for each component group of the TiDB cluster.

    - PD certificate

        First, generate the default `pd.json` file:

        ```shell
        cfssl print-defaults csr > pd.json
        ```

        Then, edit this file to change the `CN` and `hosts` attributes:

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${pd_group_name}-pd",
              "${pd_group_name}-pd.${namespace}",
              "${pd_group_name}-pd.${namespace}.svc",
              "${pd_group_name}-pd-peer",
              "${pd_group_name}-pd-peer.${namespace}",
              "${pd_group_name}-pd-peer.${namespace}.svc",
              "*.${pd_group_name}-pd-peer",
              "*.${pd_group_name}-pd-peer.${namespace}",
              "*.${pd_group_name}-pd-peer.${namespace}.svc"
            ],
        ...
        ```

        `${pd_group_name}` is the name of PDGroup, and `${namespace}` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

        Finally, generate the PD certificate:

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal pd.json | cfssljson -bare pd
        ```

    - TiKV certificate

        First, generate the default `tikv.json` file:

        ```shell
        cfssl print-defaults csr > tikv.json
        ```

        Then, edit this file to change the `CN` and `hosts` attributes:

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${tikv_group_name}-tikv",
              "${tikv_group_name}-tikv.${namespace}",
              "${tikv_group_name}-tikv.${namespace}.svc",
              "${tikv_group_name}-tikv-peer",
              "${tikv_group_name}-tikv-peer.${namespace}",
              "${tikv_group_name}-tikv-peer.${namespace}.svc",
              "*.${tikv_group_name}-tikv-peer",
              "*.${tikv_group_name}-tikv-peer.${namespace}",
              "*.${tikv_group_name}-tikv-peer.${namespace}.svc"
            ],
        ...
        ```

        `${tikv_group_name}` is the name of TiKVGroup, and `${namespace}` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

        Finally, generate the TiKV certificate:

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal tikv.json | cfssljson -bare tikv
        ```

    - TiDB certificate

        First, generate the default `tidb.json` file:

        ```shell
        cfssl print-defaults csr > tidb.json
        ```

        Then, edit this file to change the `CN` and `hosts` attributes:

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${tidb_group_name}-tidb",
              "${tidb_group_name}-tidb.${namespace}",
              "${tidb_group_name}-tidb.${namespace}.svc",
              "${tidb_group_name}-tidb-peer",
              "${tidb_group_name}-tidb-peer.${namespace}",
              "${tidb_group_name}-tidb-peer.${namespace}.svc",
              "*.${tidb_group_name}-tidb-peer",
              "*.${tidb_group_name}-tidb-peer.${namespace}",
              "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
            ],
        ...
        ```

        `${tidb_group_name}` is the name of TiDBGroup, and `${namespace}` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

        Finally, generate the TiDB certificate:

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal tidb.json | cfssljson -bare tidb
        ```

    - Other components

        In addition to PD, TiKV, and TiDB, other component groups also require their own TLS certificates. The following example shows the basic steps to generate a component certificate:

        First, generate the default `${component_name}.json` file:

        ```shell
        cfssl print-defaults csr > ${component_name}.json
        ```

        Then, edit this file to change the `CN` and `hosts` attributes:

        ```json
        ...
            "CN": "TiDB",
            "hosts": [
              "127.0.0.1",
              "::1",
              "${group_name}-${component_name}",
              "${group_name}-${component_name}.${namespace}",
              "${group_name}-${component_name}.${namespace}.svc",
              "${group_name}-${component_name}-peer",
              "${group_name}-${component_name}-peer.${namespace}",
              "${group_name}-${component_name}-peer.${namespace}.svc",
              "*.${group_name}-${component_name}-peer",
              "*.${group_name}-${component_name}-peer.${namespace}",
              "*.${group_name}-${component_name}-peer.${namespace}.svc"
            ],
        ...
        ```

        In this file:

        - `${group_name}` is the name of the component group.
        - `${component_name}` is the name of the component (use lowercase letters, such as `pd`, `tikv`, and `tidb`).
        - `${namespace}` the namespace in which the TiDB cluster is deployed.
        - You can also add your customized `hosts`.

        Finally, generate the component certificate:

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=internal ${component_name}.json | cfssljson -bare ${component_name}
        ```

6. Create the Kubernetes Secret object:

    If you have already generated a set of certificates for each component and a set of client-side certificates for each client as described in the preceding steps, create the Secret objects for the TiDB cluster by executing the following command:

    Create the Secret for the PD cluster certificate:

    ```shell
    kubectl create secret generic ${pd_group_name}-pd-cluster-secret --namespace=${namespace} --from-file=tls.crt=pd.pem --from-file=tls.key=pd-key.pem --from-file=ca.crt=ca.pem
    ```

    Create the Secret for the TiKV cluster certificate:

    ```shell
    kubectl create secret generic ${tikv_group_name}-tikv-cluster-secret --namespace=${namespace} --from-file=tls.crt=tikv.pem --from-file=tls.key=tikv-key.pem --from-file=ca.crt=ca.pem
    ```

    Create the Secret for the TiDB cluster certificate:

    ```shell
    kubectl create secret generic ${tidb_group_name}-tidb-cluster-secret --namespace=${namespace} --from-file=tls.crt=tidb.pem --from-file=tls.key=tidb-key.pem --from-file=ca.crt=ca.pem
    ```

    Create the Secret for other component certificates:

    ```shell
    kubectl create secret generic ${group_name}-${component_name}-cluster-secret --namespace=${namespace} --from-file=tls.crt=${component_name}.pem --from-file=tls.key=${component_name}-key.pem --from-file=ca.crt=ca.pem
    ```

    In this step, separate Secrets are created for the server-side certificates of PD, TiKV, and TiDB for loading during startup, and another set of client-side certificates is provided for their client connections.

### Use `cert-manager`

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
  version: v8.1.0
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
  version: v8.1.0
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
  version: v8.1.0
  replicas: 1
  template:
    spec:
      config: |
        [security]
        cluster-verify-cn = ["TiDB"]
```

Then, execute `kubectl apply -f tidb-cluster.yaml` to create a TiDB cluster.
