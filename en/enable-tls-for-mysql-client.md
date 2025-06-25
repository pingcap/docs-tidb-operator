---
title: Enable TLS for the MySQL Client
summary: Learn how to enable TLS for the MySQL client of the TiDB cluster on Kubernetes.
---

# Enable TLS for the MySQL Client

This document describes how to enable TLS for MySQL client of the TiDB cluster on Kubernetes. To enable TLS for the MySQL client, perform the following steps:

1. Issue two sets of certificates: a set of server-side certificates for the TiDB server, and a set of client-side certificates for the MySQL client. Create two Secret objects, `${tidb_group_name}-tidb-server-secret` and `${tidb_group_name}-tidb-client-secret`, respectively including these two sets of certificates.

    > **Note:**
    >
    > - The Secret objects you created must follow the preceding naming convention. Otherwise, the deployment of the TiDB cluster will fail.
    > - Explicitly specifying the MySQL TLS Secret will be supported in a future release.
    > - The default naming convention for Secrets differs between TiDB Operator v2 and v1:
    >     - For TiDB clusters created by TiDB Operator v1, the default Secret names are `${cluster_name}-tidb-server-secret` and `${cluster_name}-tidb-client-secret`.
    >     - In TiDB Operator v2, different `TiDBGroup` objects support different TLS certificates. Therefore, the default Secret names are `${tidb_group_name}-tidb-server-secret` and `${tidb_group_name}-tidb-client-secret`.

2. Deploy the cluster, and set the `.spec.template.spec.security.tls.mysql.enabled` field in `TiDBGroup` to `true`.

    > **Note:**
    >
    > Enabling or modifying the TLS configuration of a running `TiDBGroup` triggers a rolling restart of TiDB Pods. Perform this operation with caution.

3. Configure the MySQL client to use an encrypted connection.

There are multiple ways to issue certificates. This document provides two methods, and you can also issue certificates for TiDB clusters as needed. The two methods are:

- Use the `cfssl` system to issue certificates
- (Recommended) Use the `cert-manager` system to issue certificates

To renew existing TLS certificates, see [Renew and Replace the TLS Certificate](renew-tls-certificate.md).

## Step 1: Issue two sets of certificates for the TiDB cluster

### Use `cfssl` to issue certificates

1. Download `cfssl` and initialize the certificate issuer:

    ```shell
    mkdir -p ~/bin
    curl -s -L -o ~/bin/cfssl https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
    curl -s -L -o ~/bin/cfssljson https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
    chmod +x ~/bin/{cfssl,cfssljson}
    export PATH=$PATH:~/bin

    mkdir -p cfssl
    cd cfssl
    cfssl print-defaults config > ca-config.json
    cfssl print-defaults csr > ca-csr.json
    ```

2. Configure the client auth (CA) option in `ca-config.json`:

    ```json
    {
        "signing": {
            "default": {
                "expiry": "8760h"
            },
            "profiles": {
                "server": {
                    "expiry": "8760h",
                    "usages": [
                        "signing",
                        "key encipherment",
                        "server auth"
                    ]
                },
                "client": {
                    "expiry": "8760h",
                    "usages": [
                        "signing",
                        "key encipherment",
                        "client auth"
                    ]
                }
            }
        }
    }
    ```

3. Change the certificate signing request (CSR) of `ca-csr.json`:

    ```json
    {
        "CN": "TiDB Server",
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
    ```

4. Generate CA by the configured option:

    ```shell
    cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
    ```

5. Generate the server-side certificate:

    First, create the default `server.json` file:

    ```shell
    cfssl print-defaults csr > server.json
    ```

    Then, edit this file to change the `CN` and `hosts` attributes:

    ```json
    ...
        "CN": "TiDB Server",
        "hosts": [
          "127.0.0.1",
          "::1",
          "${tidb_group_name}-tidb",
          "${tidb_group_name}-tidb.${namespace}",
          "${tidb_group_name}-tidb.${namespace}.svc",
          "*.${tidb_group_name}-tidb",
          "*.${tidb_group_name}-tidb.${namespace}",
          "*.${tidb_group_name}-tidb.${namespace}.svc",
          "*.${tidb_group_name}-tidb-peer",
          "*.${tidb_group_name}-tidb-peer.${namespace}",
          "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
        ],
    ...
    ```

    `${tidb_group_name}` is the name of `TiDBGroup`. `${namespace}` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

    Finally, generate the server-side certificate:

    ```shell
    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server server.json | cfssljson -bare server
    ```

6. Generate the client-side certificate:

    First, create the default `client.json` file:

    ```shell
    cfssl print-defaults csr > client.json
    ```

    Then, edit this file to change the `CN` and `hosts` attributes. You can leave the `hosts` empty:

    ```json
    ...
        "CN": "TiDB Client",
        "hosts": [],
    ...
    ```

    Finally, generate the client-side certificate:

    ```shell
    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client client.json | cfssljson -bare client
    ```

7. Create the Kubernetes Secret object.

    If you have already generated two sets of certificates as described in the above steps, create the Secret object for the TiDB cluster by the following command:

    ```shell
    kubectl create secret generic ${tidb_group_name}-tidb-server-secret --namespace=${namespace} --from-file=tls.crt=server.pem --from-file=tls.key=server-key.pem --from-file=ca.crt=ca.pem
    kubectl create secret generic ${tidb_group_name}-tidb-client-secret --namespace=${namespace} --from-file=tls.crt=client.pem --from-file=tls.key=client-key.pem --from-file=ca.crt=ca.pem
    ```

    You have created two Secret objects for the server-side and client-side certificates:

    - The TiDB server loads one Secret object when it starts
    - The MySQL client uses the other Secret object when it connects to the TiDB cluster

You can generate multiple sets of client-side certificates. At least one set of client-side certificates is needed for the internal components of TiDB Operator to access the TiDB server.

### Use `cert-manager` to issue certificates

1. Install `cert-manager`.

    Refer to [cert-manager installation on Kubernetes](https://docs.cert-manager.io/en/release-0.11/getting-started/install/kubernetes.html).

2. Create an Issuer to issue certificates for the TiDB cluster.

    To configure `cert-manager`, create the Issuer resources.

    First, create a directory to save the files that `cert-manager` needs to create certificates:

    ```shell
    mkdir -p cert-manager
    cd cert-manager
    ```

    Then, create a `tidb-server-issuer.yaml` file with the following content:

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
      commonName: "TiDB CA"
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
      name: ${cluster_name}-cert-issuer
      namespace: ${namespace}
    spec:
      ca:
        secretName: ${cluster_name}-ca-secret
    ```

    This `.yaml` file creates three objects:

    - An Issuer object of SelfSigned class, used to generate the CA certificate needed by the Issuer of the CA class
    - A Certificate object, whose `isCa` is set to `true`
    - An Issuer, used to issue TLS certificates for the TiDB server

    Finally, execute the following command to create an Issuer:

    ```shell
    kubectl apply -f tidb-server-issuer.yaml
    ```

3. Generate the server-side certificate.

    In `cert-manager`, the Certificate resource represents the certificate interface. This certificate is issued and updated by the Issuer created in Step 2.

    First, create a `tidb-server-cert.yaml` file with the following content:

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${tidb_group_name}-tidb-server-secret
      namespace: ${namespace}
    spec:
      secretName: ${tidb_group_name}-tidb-server-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB"
      usages:
        - server auth
      dnsNames:
        - "${tidb_group_name}-tidb"
        - "${tidb_group_name}-tidb.${namespace}"
        - "${tidb_group_name}-tidb.${namespace}.svc"
        - "*.${tidb_group_name}-tidb"
        - "*.${tidb_group_name}-tidb.${namespace}"
        - "*.${tidb_group_name}-tidb.${namespace}.svc"
        - "*.${tidb_group_name}-tidb-peer"
        - "*.${tidb_group_name}-tidb-peer.${namespace}"
        - "*.${tidb_group_name}-tidb-peer.${namespace}.svc"
      ipAddresses:
        - 127.0.0.1
        - ::1
      issuerRef:
        name: ${cluster_name}-cert-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    `${cluster_name}` is the name of the cluster. `${tidb_group_name}` is the name of `TiDBGroup`:

    - Set `spec.secretName` to `${tidb_group_name}-tidb-server-secret`
    - Add `server auth` in `usages`.
    - Add the following six DNSs in `dnsNames`. You can also add other DNSs according to your needs:
      - `${tidb_group_name}-tidb`
      - `${tidb_group_name}-tidb.${namespace}`
      - `${tidb_group_name}-tidb.${namespace}.svc`
      - `*.${tidb_group_name}-tidb`
      - `*.${tidb_group_name}-tidb.${namespace}`
      - `*.${tidb_group_name}-tidb.${namespace}.svc`
      - `*.${tidb_group_name}-tidb-peer`
      - `*.${tidb_group_name}-tidb-peer.${namespace}`
      - `*.${tidb_group_name}-tidb-peer.${namespace}.svc`
    - Add the following two IPs in `ipAddresses`. You can also add other IPs according to your needs:
      - `127.0.0.1`
      - `::1`
    - Add the preceding created Issuer in the `issuerRef`
    - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec).

    Execute the following command to generate the certificate:

    ```shell
    kubectl apply -f tidb-server-cert.yaml
    ```

    After the object is created, cert-manager generates a `${tidb_group_name}-tidb-server-secret` Secret object to be used by the TiDB server.

4. Generate the client-side certificate:

    Create a `tidb-client-cert.yaml` file with the following content:

    ```yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${tidb_group_name}-tidb-client-secret
      namespace: ${namespace}
    spec:
      secretName: ${tidb_group_name}-tidb-client-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB"
      usages:
        - client auth
      issuerRef:
        name: ${cluster_name}-cert-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    `${cluster_name}` is the name of the cluster. `${tidb_group_name}` is the name of `TiDBGroup`:

    - Set `spec.secretName` to `${tidb_group_name}-tidb-client-secret`
    - Add `client auth` in `usages`
    - `dnsNames` and `ipAddresses` are not required
    - Add the Issuer created above in the `issuerRef`
    - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)

    Execute the following command to generate the certificate:

    ```shell
    kubectl apply -f tidb-client-cert.yaml
    ```

    After the object is created, cert-manager generates a `${tidb_group_name}-tidb-client-secret` Secret object to be used by the TiDB client.

    > **Note:**
    >
    > - The `ca.crt` included in the Secret issued by cert-manager is the CA that signed the certificate, not the CA used to validate the peer's mTLS certificate.
    > - In this example, the client and server TLS certificates are issued by the same CA, so they can be used directly. If the client and server certificates are issued by different CAs, it is recommended to use the [Trust Manager](https://cert-manager.io/docs/trust/trust-manager/) to distribute the appropriate `ca.crt`.

## Step 2: Deploy the TiDBGroup

The following configuration example shows how to create a `TiDBGroup` with MySQL TLS enabled:

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: tidb
spec:
  cluster:
    name: tls
  version: v8.1.0
  replicas: 1
  template:
    spec:
      security:
        tls:
          mysql:
            enabled: true
      config: |
        [security]
        cluster-verify-cn = ["TiDB"]
```

## Step 3: Configure the MySQL client to use an encrypted connection

To connect the MySQL client with the TiDB cluster, use the client-side certificate created above and take the following methods. For details, refer to [Configure the MySQL client to use TLS connections](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers/#configure-the-mysql-client-to-use-tls-connections).

Execute the following command to acquire the client-side certificate and connect to the TiDB server:

```shell
kubectl get secret -n ${namespace} ${tidb_group_name}-tidb-client-secret  -ojsonpath='{.data.tls\.crt}' | base64 --decode > client-tls.crt
kubectl get secret -n ${namespace} ${tidb_group_name}-tidb-client-secret  -ojsonpath='{.data.tls\.key}' | base64 --decode > client-tls.key
kubectl get secret -n ${namespace} ${tidb_group_name}-tidb-client-secret  -ojsonpath='{.data.ca\.crt}'  | base64 --decode > client-ca.crt
```

```shell
mysql --comments -uroot -p -P 4000 -h ${tidb_host} --ssl-cert=client-tls.crt --ssl-key=client-tls.key --ssl-ca=client-ca.crt
```

Finally, to verify whether TLS is successfully enabled, refer to [Check whether the current connection uses encryption](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers/#check-whether-the-current-connection-uses-encryption).
