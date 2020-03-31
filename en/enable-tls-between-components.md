---
title: Enable TLS between TiDB Components
summary: Learn how to enable TLS between TiDB components on Kubernetes.
category: how-to
---

# Enable TLS between TiDB Components

This document describes how to enable Transport Layer Security (TLS) between components of the TiDB cluster in Kubernetes, which is supported since TiDB Operator v1.1.

To enable TLS between TiDB components, perform the following steps:

1. Generate certificates for each component of the TiDB cluster to be created:

   - A set of server-side certificates for the PD/TiKV/TiDB/Pump/Drainer component, saved as the Kubernetes Secret objects: `<cluster-name>-<component-name>-cluster-secret`
   - A set of shared client-side certificates for the various clients of each component, saved as the Kubernetes Secret objects: `<cluster-name>-cluster-client-secret`.

2. Deploy the cluster, and set `.spec.tlsClient.enabled` to `true`.
3. Configure `pd-ctl` to connect to the cluster.

Certificates can be issued in multiple methods. This document describes two methods. You can choose either of them to issue certificates for the TiDB cluster:

    - [Using the `cfssl` system](#using-cfssl)
    - [Using the `cert-manager` system](#using-cert-manager)

## Step 1: Generate certificates for components of the TiDB cluster

This section describes how to issue certificates using two methods: `cfssl` and `cert-manager`.

### Using `cfssl`

1. Download `cfssl` and initialize the certificate issuer:

    {{< copyable "shell-regular" >}}

    ```shell
    mkdir -p ~/bin
    curl -s -L -o ~/bin/cfssl https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
    curl -s -L -o ~/bin/cfssljson https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
    chmod +x ~/bin/{cfssl,cfssljson}
    export PATH=$PATH:~/bin
    mkdir -p ~/cfssl
    cd ~/cfssl
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
                        "server auth",
                        "client auth"
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

    > **Note:**
    >
    > Add `"client auth"` in `profiles` - `server` - `usages`, because this server-side certificate is also used as the client-side certificate.

3. Change the certificate signing request (CSR) of `ca-csr.json`:

    ``` json
    {
        "CN": "TiDB Server",
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

    {{< copyable "shell-regular" >}}

    ```shell
    cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
    ```

5. Generate the server-side certificates:

    In this step, a set of server-side certificate is created for each component of the TiDB cluster.

    - PD

        First, generate the default `pd-server.json` file:

        {{< copyable "shell-regular" >}}

        ``` shell
        cfssl print-defaults csr > pd-server.json
        ```

        Then, edit this file to change the `CN` and `hosts` attributes:

        ```json
        ...
            "CN": "PD Server",
            "hosts": [
              "127.0.0.1",
              "::1",
              "<cluster-name>-pd",
              "<cluster-name>-pd.<namespace>",
              "<cluster-name>-pd.<namespace>.svc",
              "<cluster-name>-pd-peer",
              "<cluster-name>-pd-peer.<namespace>",
              "<cluster-name>-pd-peer.<namespace>.svc",
              "*.<cluster-name>-pd-peer",
              "*.<cluster-name>-pd-peer.<namespace>",
              "*.<cluster-name>-pd-peer.<namespace>.svc"
            ],
        ...
        ```

        `<cluster-name>` is the name of the cluster. `<namespace>` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

        Finally, generate the PD server-side certificate:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server pd-server.json | cfssljson -bare pd-server
        ```

    - TiKV

        First, generate the default `tikv-server.json` file:

        {{< copyable "shell-regular" >}}

        ``` shell
        cfssl print-defaults csr > tikv-server.json
        ```

        Then, edit this file to change the `CN` and `hosts` attributes:

        ```json
        ...
            "CN": "TiKV Server",
            "hosts": [
              "127.0.0.1",
              "::1",
              "<cluster-name>-tikv",
              "<cluster-name>-tikv.<namespace>",
              "<cluster-name>-tikv.<namespace>.svc",
              "<cluster-name>-tikv-peer",
              "<cluster-name>-tikv-peer.<namespace>",
              "<cluster-name>-tikv-peer.<namespace>.svc",
              "*.<cluster-name>-tikv-peer",
              "*.<cluster-name>-tikv-peer.<namespace>",
              "*.<cluster-name>-tikv-peer.<namespace>.svc"
            ],
        ...
        ```

        `<cluster-name>` is the name of the cluster. `<namespace>` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

        Finally, generate the TiKV server-side certificate:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server tikv-server.json | cfssljson -bare tikv-server
        ```

    - TiDB

        First, create the default `tidb-server.json` file:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl print-defaults csr > tidb-server.json
        ```

        Then, edit this file to change the `CN`, `hosts` attributes:

        ```json
        ...
            "CN": "TiDB Server",
            "hosts": [
              "127.0.0.1",
              "::1",
              "<cluster-name>-tidb",
              "<cluster-name>-tidb.<namespace>",
              "<cluster-name>-tidb.<namespace>.svc",
              "<cluster-name>-tidb-peer",
              "<cluster-name>-tidb-peer.<namespace>",
              "<cluster-name>-tidb-peer.<namespace>.svc",
              "*.<cluster-name>-tidb-peer",
              "*.<cluster-name>-tidb-peer.<namespace>",
              "*.<cluster-name>-tidb-peer.<namespace>.svc"
            ],
        ...
        ```

        `<cluster-name>` is the name of the cluster. `<namespace>` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

        Finally, generate the TiDB server-side certificate:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server tidb-server.json | cfssljson -bare tidb-server
        ```

    - Pump

        First, create the default `pump-server.json` file:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl print-defaults csr > pump-server.json
        ```

        Then, edit this file to change the `CN`, `hosts` attributes:

        ``` json
        ...
            "CN": "Pump Server",
            "hosts": [
              "127.0.0.1",
              "::1",
              "*.<cluster-name>-pump",
              "*.<cluster-name>-pump.<namespace>",
              "*.<cluster-name>-pump.<namespace>.svc"
            ],
        ...
        ```

        `<cluster-name>` is the name of the cluster. `<namespace>` is the namespace in which the TiDB cluster is deployed. You can also add your customized `hosts`.

        Finally, generate the Pump server-side certificate:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server pump-server.json | cfssljson -bare pump-server
        ```

    - Drainer

        First, generate the default `drainer-server.json` file:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl print-defaults csr > drainer-server.json
        ```

        Then, edit this file to change the `CN`, `hosts` attributes:

        ```json
        ...
            "CN": "Drainer Server",
            "hosts": [
              "127.0.0.1",
              "::1",
              "<for hosts list, see the following instructions>"
            ],
        ...
        ```

        Drainer is deployed using Helm. The `hosts` field varies with different configuration of the `values.yaml` file.

        If you have set the `drainerName` attribute when deploying Drainer as follows:

        ```yaml
        ...
        # Changes the names of the statefulset and Pod.
        # The default value is clusterName-ReleaseName-drainer.
        # Does not change the name of an existing running Drainer, which is unsupported.
        drainerName: my-drainer
        ...
        ```

        Then you can set the `hosts` attribute as described below:

        ```json
        ...
            "CN": "Drainer Server",
            "hosts": [
              "127.0.0.1",
              "::1",
              "*.<drainer-name>",
              "*.<drainer-name>.<namespace>",
              "*.<drainer-name>.<namespace>.svc"
            ],
        ...
        ```

        If you have not set the `drainerName` attribute when deploying Drainer, configure the `hosts` attribute as follows:

        ```json
        ...
            "CN": "Drainer Server",
            "hosts": [
              "127.0.0.1",
              "::1",
              "*.<cluster-name>-<release-name>-drainer",
              "*.<cluster-name>-<release-name>-drainer.<namespace>",
              "*.<cluster-name>-<release-name>-drainer.<namespace>.svc"
            ],
        ...
        ```

        `<cluster-name>` is the name of the cluster. `<namespace>` is the namespace in which the TiDB cluster is deployed. `<release-name>` is the `release name` you set when `helm install` is executed. `<drainer-name>` is `drainerName` in the `values.yaml` file. You can also add your customized `hosts`.

        Finally, generate the Drainer server-side certificate:

        {{< copyable "shell-regular" >}}

        ```shell
        cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server drainer-server.json | cfssljson -bare drainer-server
        ```

6. Generate the client-side certificate:

    First, create the default `client.json` file:

    {{< copyable "shell-regular" >}}

    ```shell
    cfssl print-defaults csr > client.json
    ```

    Then, edit this file to change the `CN`, `hosts` attributes. You can leave the `hosts` empty:

    ```json
    ...
        "CN": "TiDB Cluster Client",
        "hosts": [],
    ...
    ```

    Finally, generate the client-side certificate:

    ```shell
    cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client client.json | cfssljson -bare client
    ```

7. Create the Kubernetes Secret object:

    If you have already generated a set of certificates for each component and a set of client-side certificate for each client as described in the above steps, create the Secret objects for the TiDB cluster by executing the following command:

    - The PD cluster certificate Secret:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic <cluster-name>-pd-cluster-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/pd-server.pem --from-file=tls.key=~/cfssl/pd-server-key.pem --from-file=ca.crt=~/cfssl/ca.pem
        ```

    - The TiKV cluster certificate Secret:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic <cluster-name>-tikv-cluster-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/tikv-server.pem --from-file=tls.key=~/cfssl/tikv-server-key.pem --from-file=ca.crt=~/cfssl/ca.pem
        ```

    - The TiDB cluster certificate Secret:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic <cluster-name>-tidb-cluster-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/tidb-server.pem --from-file=tls.key=~/cfssl/tidb-server-key.pem --from-file=ca.crt=~/cfssl/ca.pem
        ```

    - The Pump cluster certificate Secret:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic <cluster-name>-pump-cluster-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/pump-server.pem --from-file=tls.key=~/cfssl/pump-server-key.pem --from-file=ca.crt=~/cfssl/ca.pem
        ```

    - The Drainer cluster certificate Secret:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic <cluster-name>-drainer-cluster-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/drainer-server.pem --from-file=tls.key=~/cfssl/drainer-server-key.pem --from-file=ca.crt=~/cfssl/ca.pem
        ```

    - The client certificate Secret:

        {{< copyable "shell-regular" >}}

        ```shell
        kubectl create secret generic <cluster-name>-cluster-client-secret --namespace=<namespace> --from-file=tls.crt=~/cfssl/client.pem --from-file=tls.key=~/cfssl/client-key.pem --from-file=ca.crt=~/cfssl/ca.pem
        ```

    You have created two Secret objects:

    - One Secret object for each PD/TiKV/TiDB/Pump/Drainer server-side certificate to load when the server is started;
    - One Secret object for their clients to connect.

### Using `cert-manager`

1. Install `cert-manager`.

    Refer to [cert-manager installation in Kubernetes](https://docs.cert-manager.io/en/release-0.11/getting-started/install/kubernetes.html) for details.

2. Create a ClusterIssuer to issue certificates to the TiDB cluster.

    To configure `cert-manager`, create the Issuer or ClusterIssuer resources. This document describes how to use ClusterIssuer, which supports issuing certificates in multiple `namespace`.

    First, create a directory which saves the files that `cert-manager` needs to create certificates:

    {{< copyable "shell-regular" >}}

    ```shell
    mkdir -p ~/cert-manager
    cd ~/cert-manager
    ```

    Then, create a `tidb-cluster-issuer.yaml` file with the following content:

    ```yaml
    apiVersion: cert-manager.io/v1alpha2
    kind: ClusterIssuer
    metadata:
      name: tidb-selfsigned-ca-issuer
    spec:
      selfSigned: {}
    ---
    apiVersion: cert-manager.io/v1alpha2
    kind: Certificate
    metadata:
      name: tidb-cluster-issuer-cert
      namespace: cert-manager
    spec:
      secretName: tidb-cluster-issuer-cert
      commonName: "TiDB CA"
      isCA: true
      issuerRef:
        name: tidb-selfsigned-ca-issuer
        kind: ClusterIssuer
    ---
    apiVersion: cert-manager.io/v1alpha2
    kind: ClusterIssuer
    metadata:
      name: tidb-cluster-issuer
    spec:
      ca:
        secretName: tidb-cluster-issuer-cert
    ```

    The above yaml file creates three objects:

    - A ClusterIssuer object of the SelfSigned type, used to generate the CA certificate needed by ClusterIssuer of the CA type;
    - A Certificate object, whose `isCa` is set to `true`.
    - A ClusterIssuer, used to issue TLS certificates between TiDB components.

    Finally, execute the following command to create a ClusterIssuer:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl apply -f ~/cert-manager/tidb-cluster-issuer.yaml
    ```

3. Generate the server-side certificate.

    In `cert-manager`, the Certificate resource represents the certificate interface. This certificate is issued and updated by the ClusterIssuer created in Step 2.

    According to [Enable TLS Authentication | TiDB Documentation](https://pingcap.com/docs/stable/how-to/secure/enable-tls-between-components/), each component needs a server-side certificate, and all components need a shared client-side certificate for their clients.

    - PD

        ``` yaml
        apiVersion: cert-manager.io/v1alpha2
        kind: Certificate
        metadata:
          name: <cluster-name>-pd-cluster-secret
          namespace: <namespace>
        spec:
          secretName: <cluster-name>-pd-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          organization:
          - PingCAP
          commonName: "PD"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "<cluster-name>-pd"
          - "<cluster-name>-pd.<namespace>"
          - "<cluster-name>-pd.<namespace>.svc"
          - "<cluster-name>-pd-peer"
          - "<cluster-name>-pd-peer.<namespace>"
          - "<cluster-name>-pd-peer.<namespace>.svc"
          - "*.<cluster-name>-pd-peer"
          - "*.<cluster-name>-pd-peer.<namespace>"
          - "*.<cluster-name>-pd-peer.<namespace>.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: tidb-cluster-issuer
            kind: ClusterIssuer
            group: cert-manager.io
        ```

        `<cluster-name>` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `<cluster-name>-pd-cluster-secret`.
        - Add `server auth` and `client auth` in `usages`.
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:
            - `<cluster-name>-pd`
            - `<cluster-name>-pd.<namespace>`
            - `<cluster-name>-pd.<namespace>.svc`
            - `<cluster-name>-pd-peer`
            - `<cluster-name>-pd-peer.<namespace>`
            - `<cluster-name>-pd-peer.<namespace>.svc`
            - `*.<cluster-name>-pd-peer`
            - `*.<cluster-name>-pd-peer.<namespace>`
            - `*.<cluster-name>-pd-peer.<namespace>.svc`
        - Add the following two IPs in `ipAddresses`. You can also add other IPs according to your needs:
            - `127.0.0.1`
            - `::1`
        - Add the ClusterIssuer created above in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec).

        After the object is created, `cert-manager` generates a `<cluster-name>-pd-cluster-secret` Secret object to be used by the PD component of the TiDB server.

    - TiKV

        ``` yaml
        apiVersion: cert-manager.io/v1alpha2
        kind: Certificate
        metadata:
          name: <cluster-name>-tikv-cluster-secret
          namespace: <namespace>
        spec:
          secretName: <cluster-name>-tikv-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          organization:
          - PingCAP
          commonName: "TiKV"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "<cluster-name>-tikv"
          - "<cluster-name>-tikv.<namespace>"
          - "<cluster-name>-tikv.<namespace>.svc"
          - "<cluster-name>-tikv-peer"
          - "<cluster-name>-tikv-peer.<namespace>"
          - "<cluster-name>-tikv-peer.<namespace>.svc"
          - "*.<cluster-name>-tikv-peer"
          - "*.<cluster-name>-tikv-peer.<namespace>"
          - "*.<cluster-name>-tikv-peer.<namespace>.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: tidb-cluster-issuer
            kind: ClusterIssuer
            group: cert-manager.io
        ```

        `<cluster-name>` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `<cluster-name>-tikv-cluster-secret`.
        - Add `server auth` and `client auth` in `usages`.
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:

            - `<cluster-name>-tikv`
            - `<cluster-name>-tikv.<namespace>`
            - `<cluster-name>-tikv.<namespace>.svc`
            - `<cluster-name>-tikv-peer`
            - `<cluster-name>-tikv-peer.<namespace>`
            - `<cluster-name>-tikv-peer.<namespace>.svc`
            - `*.<cluster-name>-tikv-peer`
            - `*.<cluster-name>-tikv-peer.<namespace>`
            - `*.<cluster-name>-tikv-peer.<namespace>.svc`

        - Add the following 2 IPs in `ipAddresses`. You can also add other IPs according to your needs:
            - `127.0.0.1`
            - `::1`
        - Add the ClusterIssuer created above in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec).

        After the object is created, `cert-manager` generates a `<cluster-name>-tikv-cluster-secret` Secret object to be used by the TiKV component of the TiDB server.

    - TiDB

        ``` yaml
        apiVersion: cert-manager.io/v1alpha2
        kind: Certificate
        metadata:
          name: <cluster-name>-tidb-cluster-secret
          namespace: <namespace>
        spec:
          secretName: <cluster-name>-tidb-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          organization:
          - PingCAP
          commonName: "TiDB"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "<cluster-name>-tidb"
          - "<cluster-name>-tidb.<namespace>"
          - "<cluster-name>-tidb.<namespace>.svc"
          - "<cluster-name>-tidb-peer"
          - "<cluster-name>-tidb-peer.<namespace>"
          - "<cluster-name>-tidb-peer.<namespace>.svc"
          - "*.<cluster-name>-tidb-peer"
          - "*.<cluster-name>-tidb-peer.<namespace>"
          - "*.<cluster-name>-tidb-peer.<namespace>.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: tidb-cluster-issuer
            kind: ClusterIssuer
            group: cert-manager.io
        ```

        `<cluster-name>` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `<cluster-name>-tidb-cluster-secret`
        - Add `server auth` and `client auth` in `usages`
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:

            - `<cluster-name>-tidb`
            - `<cluster-name>-tidb.<namespace>`
            - `<cluster-name>-tidb.<namespace>.svc`
            - `<cluster-name>-tidb-peer`
            - `<cluster-name>-tidb-peer.<namespace>`
            - `<cluster-name>-tidb-peer.<namespace>.svc`
            - `*.<cluster-name>-tidb-peer`
            - `*.<cluster-name>-tidb-peer.<namespace>`
            - `*.<cluster-name>-tidb-peer.<namespace>.svc`

        - Add the following 2 IPs in `ipAddresses`. You can also add other IPs according to your needs:
            - `127.0.0.1`
            - `::1`
        - Add the ClusterIssuer created above in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec).

        After the object is created, `cert-manager` generates a `<cluster-name>-tidb-cluster-secret` Secret object to be used by the TiDB component of the TiDB server.

    - Pump

        ``` yaml
        apiVersion: cert-manager.io/v1alpha2
        kind: Certificate
        metadata:
          name: <cluster-name>-pump-cluster-secret
          namespace: <namespace>
        spec:
          secretName: <cluster-name>-pump-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          organization:
          - PingCAP
          commonName: "Pump"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "*.<cluster-name>-pump"
          - "*.<cluster-name>-pump.<namespace>"
          - "*.<cluster-name>-pump.<namespace>.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: tidb-cluster-issuer
            kind: ClusterIssuer
            group: cert-manager.io
        ```

        `<cluster-name>` is the name of the cluster. Configure the items as follows:

        - Set `spec.secretName` to `<cluster-name>-pump-cluster-secret`
        - Add `server auth` and `client auth` in `usages`
        - Add the following DNSs in `dnsNames`. You can also add other DNSs according to your needs:

            - `*.<cluster-name>-pump`
            - `*.<cluster-name>-pump.<namespace>`
            - `*.<cluster-name>-pump.<namespace>.svc`

        - Add the following 2 IPs in `ipAddresses`. You can also add other IPs according to your needs:
            - `127.0.0.1`
            - `::1`
        - Add the ClusterIssuer created above in the `issuerRef`
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec).

        After the object is created, `cert-manager` generates a `<cluster-name>-pump-cluster-secret` Secret object to be used by the Pump component of the TiDB server.

    - Drainer

        Drainer is deployed using Helm. The `dnsNames` field varies with different configuration of the `values.yaml` file.

        If you set the `drainerName` attributes when deploying Drainer as follows:

        ```yaml
        ...
        # Changes the name of the statefulset and Pod.
        # The default value is clusterName-ReleaseName-drainer
        # Does not change the name of an existing running Drainer, which is unsupported.
        drainerName: my-drainer
        ...
        ```

        Then you need to configure the certificate as described below:

        ``` yaml
        apiVersion: cert-manager.io/v1alpha2
        kind: Certificate
        metadata:
          name: <cluster-name>-drainer-cluster-secret
          namespace: <namespace>
        spec:
          secretName: <cluster-name>-drainer-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          organization:
          - PingCAP
          commonName: "Drainer"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "*.<drainer-name>"
          - "*.<drainer-name>.<namespace>"
          - "*.<drainer-name>.<namespace>.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: tidb-cluster-issuer
            kind: ClusterIssuer
            group: cert-manager.io
        ```

        If you didn't set the `drainerName` attribute when deploying Drainer, configure the `dnsNames` attributes as follows:

        ``` yaml
        apiVersion: cert-manager.io/v1alpha2
        kind: Certificate
        metadata:
          name: <cluster-name>-drainer-cluster-secret
          namespace: <namespace>
        spec:
          secretName: <cluster-name>-drainer-cluster-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          organization:
          - PingCAP
          commonName: "Drainer"
          usages:
            - server auth
            - client auth
          dnsNames:
          - "*.<cluster-name>-<release-name>-drainer"
          - "*.<cluster-name>-<release-name>-drainer.<namespace>"
          - "*.<cluster-name>-<release-name>-drainer.<namespace>.svc"
          ipAddresses:
          - 127.0.0.1
          - ::1
          issuerRef:
            name: tidb-cluster-issuer
            kind: ClusterIssuer
            group: cert-manager.io
        ```

        `<cluster-name>` is the name of the cluster. `<namespace>` is the namespace in which the TiDB cluster is deployed. `<release-name>` is the `release name` you set when `helm install` is executed. `<drainer-name>` is `drainerName` in the `values.yaml` file. You can also add your customized `dnsNames`.

        - Set `spec.secretName` to `<cluster-name>-drainer-cluster-secret`.
        - Add `server auth` and `client auth` in `usages`.
        - See the above descriptions for `dnsNames`.
        - Add the following 2 IPs in `ipAddresses`. You can also add other IPs according to your needs:
            - `127.0.0.1`
            - `::1`
        - Add the ClusterIssuer created above in `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec).

        After the object is created, `cert-manager` generates a `<cluster-name>-drainer-cluster-secret` Secret object to be used by the Drainer component of the TiDB server.

4. Generate the client-side certificate for components of the TiDB cluster.

    ```yaml
    apiVersion: cert-manager.io/v1alpha2
    kind: Certificate
    metadata:
        name: <cluster-name>-cluster-client-secret
        namespace: <namespace>
    spec:
        secretName: <cluster-name>-cluster-client-secret
        duration: 8760h # 365d
        renewBefore: 360h # 15d
        organization:
        - PingCAP
        commonName: "TiDB Components TLS Client"
        usages:
        - client auth
        issuerRef:
        name: tidb-cluster-issuer
        kind: ClusterIssuer
        group: cert-manager.io
    ```

    `<cluster-name>` is the name of the cluster. Configure the items as follows:

    - Set `spec.secretName` to `<cluster-name>-cluster-client-secret`.
    - Add `client auth` in `usages`.
    - You can leave `dnsNames` and `ipAddresses` empty.
    - Add the ClusterIssuer created above in `issuerRef`.
    - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1alpha2.CertificateSpec).

    After the object is created, `cert-manager` generates a `<cluster-name>-cluster-client-secret` Secret object to be used by the clients of the TiDB components.

    To obtain the client certificate, run the following commands:

    {{< copyable "shell-regular" >}}

    ``` shell
    mkdir -p ~/<cluster-name>-cluster-client-tls
    cd ~/<cluster-name>-cluster-client-tls
    kubectl get secret -n <namespace> <cluster-name>-cluster-client-secret  -ojsonpath='{.data.tls\.crt}' | base64 --decode > tls.crt
    kubectl get secret -n <namespace> <cluster-name>-cluster-client-secret  -ojsonpath='{.data.tls\.key}' | base64 --decode > tls.key
    kubectl get secret -n <namespace> <cluster-name>-cluster-client-secret  -ojsonpath='{.data.ca\.crt}' | base64 --decode > ca.crt
    ```

## Step 2: Deploy the TiDB cluster

In this step, you need to perform the following operations:

    - Create a TiDB cluster
    - Enable TLS between the TiDB components
    - Deploy a monitoring system
    - Deploy the Pump component

1. Create a TiDB cluster:

    Create the `tidb-cluster.yaml` file:

    ``` yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbCluster
    metadata:
     name: <cluster-name>
     namespace: <namespace>
    spec:
     tlsClusster:
       enabled: true
     version: v3.0.8
     timezone: UTC
     pvReclaimPolicy: Retain
     pd:
       baseImage: pingcap/pd
       replicas: 1
       requests:
         storage: "1Gi"
       config: {}
     tikv:
       baseImage: pingcap/tikv
       replicas: 1
       requests:
         storage: "1Gi"
       config: {}
     tidb:
       baseImage: pingcap/tidb
       replicas: 1
       service:
         type: ClusterIP
       config: {}
     pump:
       baseImage: pingcap/tidb-binlog
       replicas: 1
       requests:
         storage: "1Gi"
       config: {}
    ---
    apiVersion: pingcap.com/v1alpha1
    kind: TidbMonitor
    metadata:
     name: <cluser-name>-monitor
     namespace: <namespace>
    spec:
     clusters:
     - name: <cluster-name>
     prometheus:
       baseImage: prom/prometheus
       version: v2.11.1
     grafana:
       baseImage: grafana/grafana
       version: 6.0.1
     initializer:
       baseImage: pingcap/tidb-monitor-initializer
       version: v3.0.8
     reloader:
       baseImage: pingcap/tidb-monitor-reloader
       version: v1.0.1
     imagePullPolicy: IfNotPresent
    ```

    Execute `kubectl apply -f tidb-cluster.yaml` to create a TiDB cluster.

    This operation also includes deploying a monitoring system and the Pump component.

2. Create a Drainer component and enable TLS:

    - Method 1: Set `drainerName` when you create Drainer.

        Edit the `values.yaml` file, set `drainer-name`, and enable the TLS feature:

        ``` yaml
        ...
        drainerName: <drainer-name>
        tlsCluster:
          enabled: true
        ...
        ```

        Deploy the Drainer cluster:

        {{< copyable "shell-regular" >}}

        ``` shell
        helm install charts/tidb-drainer --name=<release-name> --namespace=<namespace>
        ```

    - Method 2: Do not set `drainerName` when you create Drainer.

        Edit the `values.yaml` file, and enable the TLS feature:

        ``` yaml
        ...
        tlsCluster:
          enabled: true
        ...
        ```

        Deploy the Drainer cluster:

        {{< copyable "shell-regular" >}}

        ``` shell
        helm install charts/tidb-drainer --name=<release-name> --namespace=<namespace>
        ```

3. Create the Backup/Restore resource object:

    - Create the `backup.yaml` file:

        ``` yaml
        apiVersion: pingcap.com/v1alpha1
        kind: Backup
        metadata:
          name: <cluster-name>-backup
          namespace: <namespace>
        spec:
          backupType: full
          br:
            cluster: <cluster-name>
            clusterNamespace: <namespace>
            sendCredToTikv: true
          from:
            host: <host>
            secretName: <tidb-secret>
            port: 4000
            user: root
          s3:
            provider: aws
            region: <my-region>
            secretName: <s3-secret>
            bucket: <my-bucket>
            prefix: <my-folder>
        ````

        Deploy Backup:

        {{< copyable "shell-regular" >}}

        ``` shell
        kubectl apply -f backup.yaml
        ```

    - Create the `restore.yaml` file:

         ``` yaml
        apiVersion: pingcap.com/v1alpha1
        kind: Restore
        metadata:
          name: <cluster-name>-restore
          namespace: <namespace>
        spec:
          backupType: full
          br:
            cluster: <cluster-name>
            clusterNamespace: <namespace>
            sendCredToTikv: true
          to:
            host: <host>
            secretName: <tidb-secret>
            port: 4000
            user: root
          s3:
            provider: aws
            region: <my-region>
            secretName: <s3-secret>
            bucket: <my-bucket>
            prefix: <my-folder>
        ```

        Deploy Restore:

        {{< copyable "shell-regular" >}}

        ``` shell
        kubectl apply -f restore.yaml
        ```

## Step 3: Configure `pd-ctl` and connect to the cluster

1. Download `pd-ctl`:

    Refer to [Download TiDB installation package](https://pingcap.com/docs/stable/reference/tools/pd-control/#download-tidb-installation-package).

2. Connect to the cluster:

    First, download the client-side certificate, which is the client certificate you have created in Step 1. You can directly use it, or obtain it from the `<cluster-name>-cluster-client-secret` Kubernetes Secret object created before.

    {{< copyable "shell-regular" >}}

    ``` shell
    mkdir -p ~/<cluster-name>-cluster-client-tls
    cd ~/<cluster-name>-cluster-client-tls
    kubectl get secret -n <namespace> <cluster-name>-cluster-client-secret  -ojsonpath='{.data.tls\.crt}' | base64 --decode > tls.crt
    kubectl get secret -n <namespace> <cluster-name>-cluster-client-secret  -ojsonpath='{.data.tls\.key}' | base64 --decode > tls.key
    kubectl get secret -n <namespace> <cluster-name>-cluster-client-secret  -ojsonpath='{.data.ca\.crt}' | base64 --decode > ca.crt
    ```

3. Connect to the PD cluster by `pd-ctl`:

    When you deploy the server-side certificate for the PD component, some `hosts` are customized, so you need to use these `hosts` to connect to the PD cluster.

    {{< copyable "shell-regular" >}}

    ``` shell
    pd-ctl --cacert=~/<cluster-name>-cluster-client-tls/ca.crt --cert=~/<cluster-name>-cluster-client-tls/tls.crt --key=~/<cluster-name>-cluster-client-tls/tls.key -u https://<cluster-name>-pd.<namespace>.svc:2379 member
    ```
