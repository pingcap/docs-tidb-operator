---
title: Enable TLS between TiDB Components
summary: Learn how to enable TLS between TiDB components on Kubernetes.
category: how-to
---

# Enable TLS between TiDB Components

This document describes how to enable TLS between components of the TiDB cluster on Kubernetes. Starting from TiDB Operator v1.1, TLS between components of the TiDB cluster on Kubernetes is supported.

To enable TLS between TiDB components, perform the following steps:

1. Issue two sets of certificates for each component of the TiDB cluster to be created:

   - A set of server-side certificates for PD/TiKV/TiDB/Pump/Drainer components, saved as the Kubernetes Secret objects: `<cluster-name>-<component-name>-cluster-secret`
   - A common set of client-side certificates for the various clients of all components, saved as the Kubernetes Secret objects:  `<cluster-name>-cluster-client-secret`.

2. Deploy the cluster, and set `.spec.tlsClient.enabled` to `true`.
3. Configure `pd-ctl` to connect to the cluster.

Certificates can be issued in multiple methods. This document describes two methods. You can choose either of them to issue certificates for the TiDB cluster:

    - [Using the `cfssl` system](#using-cfssl)
    - [Using the `cert-manager` system](#using-cert-manager)

## Step 1: Issue certificates for components of the TiDB cluster

This section describe how to issue certificates using two methods: `cfssl` and `cert-manager`.

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
    > Add `"client auth"` in `profile`-`server`- `usages`, because this server-side certificate is also used as the client-side certificate.

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

        First, create the default `pd-server.json` file:

        {{< copyable "shell-regular" >}}

        ``` shell
        cfssl print-defaults csr > pd-server.json
        ```

        Then, edit this file to change the `CN`, `hosts` attributes:

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

        First, create the default `tikv-server.json` file:

        {{< copyable "shell-regular" >}}

        ``` shell
        cfssl print-defaults csr > tikv-server.json
        ```

        Then, edit this file to change the `CN`, `hosts` attributes:

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

        First, create the default `drainer-server.json` file:

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

        If you set the `drainerName` attributes when deploying Drainer as follows:

        ```yaml
        ...
        # Change the name of the statefulset and pod
        # The default is clusterName-ReleaseName-drainer
        # Do not change the name of an existing running drainer: this is unsupported.
        drainerName: my-drainer
        ...
        ```

        Then you can set the `hosts` attributes as described below:

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

        If you didn't set the `drainerName` attribute when deploying Drainer, configure the `hosts` attributes as follows:

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

    If you have already generated a set of certificates for each component and a set of client-side certificate for each client as described in the above steps, create the Secret objects for the TiDB cluster by the following command:

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

    - One Secret object for the PD/TiKV/TiDB/Pump/Drainer server-side certificates to load when they are started
    - Another Secret object for their clients to connect

### Using `cert-manager`
