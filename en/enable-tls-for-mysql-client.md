---
title: Enable TLS for the MySQL Client
summary: Learn how to enable TLS for MySQL client of the TiDB cluster on Kubernetes.
aliases: ['/docs/tidb-in-kubernetes/dev/enable-tls-for-mysql-client/']
---

# Enable TLS for the MySQL Client

This document describes how to enable TLS for MySQL client of the TiDB cluster on Kubernetes. Starting from TiDB Operator v1.1, TLS for the MySQL client of the TiDB cluster on Kubernetes is supported.

To enable TLS for the MySQL client, perform the following steps:

1. [Issue two sets of certificates](#step-1-issue-two-sets-of-certificates-for-the-tidb-cluster): a set of server-side certificates for TiDB server, and a set of client-side certificates for MySQL client. Create two Secret objects, `${cluster_name}-tidb-server-secret` and `${cluster_name}-tidb-client-secret`, respectively including these two sets of certificates.

    > **Note:**
    >
    > The Secret objects you created must follow the above naming convention. Otherwise, the deployment of the TiDB cluster will fail.

    Certificates can be issued in multiple methods. This document describes how to use the `cert-manager` system to issue certificates. You can also issue certificates for the TiDB cluster as needed.

    If you need to renew the existing TLS certificate, refer to [Renew and Replace the TLS Certificate](renew-tls-certificate.md).

2. [Deploy the cluster](#step-2-deploy-the-tidb-cluster), and set `.spec.tidb.tlsClient.enabled` to `true`.

    * To skip TLS authentication for internal components that serve as the MySQL client (such as TidbInitializer, Dashboard, Backup, and Restore), you can add the `tidb.tidb.pingcap.com/skip-tls-when-connect-tidb="true"` annotation to the cluster's corresponding `TidbCluster`.
    * To disable the client CA certificate authentication on the TiDB server, you can set `.spec.tidb.tlsClient.disableClientAuthn` to `true`. This means skipping setting the `ssl-ca` parameter when you [configure TiDB server to enable secure connections](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#configure-tidb-server-to-use-secure-connections).
    * To skip the CA certificate authentication for internal components that serve as the MySQL client, you can set `.spec.tidb.tlsClient.skipInternalClientCA` to `true`.

    > **Note:**
    >
    > For an existing cluster, if you change `.spec.tidb.tlsClient.enabled` from `false` to `true`, the TiDB Pods will be rolling restarted.

3. [Configure the MySQL client to use an encrypted connection](#step-3-configure-the-mysql-client-to-use-a-tls-connection).

## Step 1. Issue two sets of certificates for the TiDB cluster

This section describes how to issue certificates for the TiDB cluster using `cert-manager`.

1. Install `cert-manager`.

    Refer to [cert-manager installation on Kubernetes](https://cert-manager.io/docs/installation/).

2. Create an Issuer to issue certificates for the TiDB cluster.

    To configure `cert-manager`, create the Issuer resources.

    First, create a directory which saves the files that `cert-manager` needs to create certificates:

    ``` shell
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
      name: ${cluster_name}-tidb-issuer
      namespace: ${namespace}
    spec:
      ca:
        secretName: ${cluster_name}-ca-secret
    ```

    This `.yaml` file creates three objects:

    - An Issuer object of SelfSigned class, used to generate the CA certificate needed by Issuer of CA class
    - A Certificate object, whose `isCa` is set to `true`
    - An Issuer, used to issue TLS certificates for the TiDB server

    Finally, execute the following command to create an Issuer:

    ``` shell
    kubectl apply -f tidb-server-issuer.yaml
    ```

3. Generate the server-side certificate.

    In `cert-manager`, the Certificate resource represents the certificate interface. This certificate is issued and updated by the Issuer created in Step 2.

    First, create a `tidb-server-cert.yaml` file with the following content:

    ``` yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${cluster_name}-tidb-server-secret
      namespace: ${namespace}
    spec:
      secretName: ${cluster_name}-tidb-server-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB Server"
      usages:
        - server auth
      dnsNames:
        - "${cluster_name}-tidb"
        - "${cluster_name}-tidb.${namespace}"
        - "${cluster_name}-tidb.${namespace}.svc"
        - "*.${cluster_name}-tidb"
        - "*.${cluster_name}-tidb.${namespace}"
        - "*.${cluster_name}-tidb.${namespace}.svc"
        - "*.${cluster_name}-tidb-peer"
        - "*.${cluster_name}-tidb-peer.${namespace}"
        - "*.${cluster_name}-tidb-peer.${namespace}.svc"
      ipAddresses:
        - 127.0.0.1
        - ::1
      issuerRef:
        name: ${cluster_name}-tidb-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    `${cluster_name}` is the name of the cluster. Configure the items as follows:

    - Set `spec.secretName` to `${cluster_name}-tidb-server-secret`
    - Add `server auth` in `usages`
    - Add the following 6 DNSs in `dnsNames`. You can also add other DNSs according to your needs:
        - `${cluster_name}-tidb`
        - `${cluster_name}-tidb.${namespace}`
        - `${cluster_name}-tidb.${namespace}.svc`
        - `*.${cluster_name}-tidb`
        - `*.${cluster_name}-tidb.${namespace}`
        - `*.${cluster_name}-tidb.${namespace}.svc`
        - `*.${cluster_name}-tidb-peer`
        - `*.${cluster_name}-tidb-peer.${namespace}`
        - `*.${cluster_name}-tidb-peer.${namespace}.svc`
    - Add the following 2 IPs in `ipAddresses`. You can also add other IPs according to your needs:
        - `127.0.0.1`
        - `::1`
    - Add the Issuer created above in the `issuerRef`
    - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec).

    Execute the following command to generate the certificate:

    ``` shell
    kubectl apply -f tidb-server-cert.yaml
    ```

    After the object is created, cert-manager generates a `${cluster_name}-tidb-server-secret` Secret object to be used by the TiDB server.

4. Generate the client-side certificate:

    Create a `tidb-client-cert.yaml` file with the following content:

    ``` yaml
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
      name: ${cluster_name}-tidb-client-secret
      namespace: ${namespace}
    spec:
      secretName: ${cluster_name}-tidb-client-secret
      duration: 8760h # 365d
      renewBefore: 360h # 15d
      subject:
        organizations:
        - PingCAP
      commonName: "TiDB Client"
      usages:
        - client auth
      issuerRef:
        name: ${cluster_name}-tidb-issuer
        kind: Issuer
        group: cert-manager.io
    ```

    `${cluster_name}` is the name of the cluster. Configure the items as follows:

    - Set `spec.secretName` to `${cluster_name}-tidb-client-secret`
    - Add `client auth` in `usages`
    - `dnsNames` and `ipAddresses` are not required
    - Add the Issuer created above in the `issuerRef`
    - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec)

    Execute the following command to generate the certificate:

    ``` shell
    kubectl apply -f tidb-client-cert.yaml
    ```

    After the object is created, cert-manager generates a `${cluster_name}-tidb-client-secret` Secret object to be used by the TiDB client.

5. Create multiple sets of client-side certificates (optional).

    Four components in the TiDB Operator cluster need to request the TiDB server. When TLS is enabled, these components can use certificates to request the TiDB server, each with a separate certificate. The four components are listed as follows:

    - TidbInitializer
    - PD Dashboard
    - Backup (when using Dumpling)
    - Restore (when using TiDB Lightning)

    If you need to [restore data using TiDB Lightning](restore-data-using-tidb-lightning.md), you need to generate a server-side certificate for the TiDB Lightning component.

    To create certificates for these components, take the following steps:

    1. Create a `tidb-components-client-cert.yaml` file with the following content:

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-tidb-initializer-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-tidb-initializer-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "TiDB Initializer client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ---
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-pd-dashboard-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-pd-dashboard-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "PD Dashboard client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ---
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-backup-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-backup-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "Backup client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ---
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-restore-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-restore-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "Restore client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ```

        In the `.yaml` file above, `${cluster_name}` is the name of the cluster. Configure the items as follows:

        - Set the value of `spec.secretName` to `${cluster_name}-${component}-client-secret`.
        - Add `client auth` in `usages`.
        - `dnsNames` and `ipAddresses` are not required.
        - Add the Issuer created above in the `issuerRef`.
        - For other attributes, refer to [cert-manager API](https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificateSpec).

        To generate a client-side certificate for TiDB Lightning, use the following content and set `tlsCluster.tlsClientSecretName` to `${cluster_name}-lightning-client-secret` in TiDB Lightning's `values.yaml` file.

        ```yaml
        apiVersion: cert-manager.io/v1
        kind: Certificate
        metadata:
          name: ${cluster_name}-lightning-client-secret
          namespace: ${namespace}
        spec:
          secretName: ${cluster_name}-lightning-client-secret
          duration: 8760h # 365d
          renewBefore: 360h # 15d
          subject:
            organizations:
            - PingCAP
          commonName: "Lightning client"
          usages:
            - client auth
          issuerRef:
            name: ${cluster_name}-tidb-issuer
            kind: Issuer
            group: cert-manager.io
        ```

    2. Create the certificate by running the following command:

        ``` shell
        kubectl apply -f tidb-components-client-cert.yaml
        ```

    3. After creating these objects, cert-manager will generate four secret objects for the four components.

    > **Note:**
    >
    > TiDB server's TLS is compatible with the MySQL protocol. When the certificate content is changed, the administrator needs to manually execute the SQL statement `alter instance reload tls` to refresh the content.

## Step 2. Deploy the TiDB cluster

In this step, you create a TiDB cluster and perform the following operations:

- Enable TLS for the MySQL client
- Initialize the cluster (an `app` database is created for demonstration)
- Create a Backup object to back up the cluster
- Create a Restore object to restore the cluster
- Use separate client-side certificates for `TidbInitializer`, PD Dashboard, Backup, and Restore (specified by `tlsClientSecretName`)

1. Create three `.yaml` files:

    - `tidb-cluster.yaml` file:

        ```yaml
        apiVersion: pingcap.com/v1alpha1
        kind: TidbCluster
        metadata:
          name: ${cluster_name}
          namespace: ${namespace}
        spec:
          version: {{{ .tidb_version }}}
          timezone: UTC
          pvReclaimPolicy: Retain
          pd:
            baseImage: pingcap/pd
            maxFailoverCount: 0
            replicas: 1
            requests:
              storage: "10Gi"
            config: {}
            tlsClientSecretName: ${cluster_name}-pd-dashboard-client-secret
          tikv:
            baseImage: pingcap/tikv
            maxFailoverCount: 0
            replicas: 1
            requests:
              storage: "100Gi"
            config: {}
          tidb:
            baseImage: pingcap/tidb
            maxFailoverCount: 0
            replicas: 1
            service:
              type: ClusterIP
            config: {}
            tlsClient:
              enabled: true
        ---
        apiVersion: pingcap.com/v1alpha1
        kind: TidbInitializer
        metadata:
          name: ${cluster_name}-init
          namespace: ${namespace}
        spec:
          image: tnir/mysqlclient
          cluster:
            namespace: ${namespace}
            name: ${cluster_name}
          initSql: |-
            create database app;
          tlsClientSecretName: ${cluster_name}-tidb-initializer-client-secret
        ```

    - `backup.yaml`:

        ```
        apiVersion: pingcap.com/v1alpha1
        kind: Backup
        metadata:
          name: ${cluster_name}-backup
          namespace: ${namespace}
        spec:
          backupType: full
          br:
            cluster: ${cluster_name}
            clusterNamespace: ${namespace}
            sendCredToTikv: true
          s3:
            provider: aws
            region: ${my_region}
            secretName: ${s3_secret}
            bucket: ${my_bucket}
            prefix: ${my_folder}
        ```

    - `restore.yaml`:

        ```
        apiVersion: pingcap.com/v1alpha1
        kind: Restore
        metadata:
          name: ${cluster_name}-restore
          namespace: ${namespace}
        spec:
          backupType: full
          br:
            cluster: ${cluster_name}
            clusterNamespace: ${namespace}
            sendCredToTikv: true
          s3:
            provider: aws
            region: ${my_region}
            secretName: ${s3_secret}
            bucket: ${my_bucket}
            prefix: ${my_folder}
        ```

    In the above file, `${cluster_name}` is the name of the cluster, and `${namespace}` is the namespace in which the TiDB cluster is deployed. To enable TLS for the MySQL client, set `spec.tidb.tlsClient.enabled` to `true`.

2. Deploy the TiDB cluster:

    ``` shell
    kubectl apply -f tidb-cluster.yaml
    ```

3. Back up the cluster:

    ``` shell
    kubectl apply -f backup.yaml
    ```

4. Restore the cluster:

    ``` shell
    kubectl apply -f restore.yaml
    ```

## Step 3. Configure the MySQL client to use a TLS connection

To connect the MySQL client with the TiDB cluster, use the client-side certificate created above and take the following methods. For details, refer to [Configure the MySQL client to use encrypted connections](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#configure-the-mysql-client-to-use-encrypted-connections).

Execute the following command to acquire the client-side certificate and connect to the TiDB server:

``` shell
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret -ojsonpath='{.data.tls\.crt}' | base64 --decode > client-tls.crt
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret -ojsonpath='{.data.tls\.key}' | base64 --decode > client-tls.key
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret -ojsonpath='{.data.ca\.crt}' | base64 --decode > client-ca.crt
```

``` shell
mysql --comments -uroot -p -P 4000 -h ${tidb_host} --ssl-cert=client-tls.crt --ssl-key=client-tls.key --ssl-ca=client-ca.crt
```

Finally, to verify whether TLS is successfully enabled, refer to [checking the current connection](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#check-whether-the-current-connection-uses-encryption).

When not relying on client certificates the following is sufficient:

``` shell
kubectl get secret -n ${namespace} ${cluster_name}-tidb-client-secret  -ojsonpath='{.data.ca\.crt}'  | base64 --decode > client-ca.crt
```

``` shell
mysql --comments -uroot -p -P 4000 -h ${tidb_host} --ssl-ca=client-ca.crt
```

## Troubleshooting

The X.509 certificates are stored in Kubernetes secrets. To inspect them, use commands similar to `kubectl -n ${namespace} get secret`.

These secrets are mounted into the containers. To view the volume mounts, check the **Volumes** section in the output of the `kubectl -n ${namespace} describe pod ${podname}` command.

To check these secret mounts from inside the container, run the following command:

``` shell
kubectl exec -n ${cluster_name} --stdin=true --tty=true ${cluster_name}-tidb-0 -c tidb -- /bin/sh
```

The contents of the TLS directories is as follows:

``` shell
sh-5.1# ls -l /var/lib/*tls
/var/lib/tidb-server-tls:
total 0
lrwxrwxrwx. 1 root root 13 Sep 25 12:23 ca.crt -> ..data/ca.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.crt -> ..data/tls.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.key -> ..data/tls.key

/var/lib/tidb-tls:
total 0
lrwxrwxrwx. 1 root root 13 Sep 25 12:23 ca.crt -> ..data/ca.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.crt -> ..data/tls.crt
lrwxrwxrwx. 1 root root 14 Sep 25 12:23 tls.key -> ..data/tls.key
```

The output of `kubectl -n ${cluster_name} logs ${cluster_name}-tidb-0 -c tidb` is as follows:

```
[2025/09/25 12:23:19.739 +00:00] [INFO] [server.go:291] ["mysql protocol server secure connection is enabled"] ["client verification enabled"=true]
```

## Reload certificates

If you generate the certificate and key files using `cert-manager`, the Secret is updated automatically whenever a new certificate is issued.

To let TiDB use the new certificate, run [`ALTER INSTANCE RELOAD TLS`](https://docs.pingcap.com/tidb/stable/sql-statement-alter-instance/#reload-tls).

To verify the certificate validity period, run the following SQL statement to check the `Ssl_server_not_before` and `Ssl_server_not_after` status variables:

```sql
SHOW GLOBAL STATUS LIKE 'Ssl\_server\_not\_%';
```

```
+-----------------------+--------------------------+
| Variable_name         | Value                    |
+-----------------------+--------------------------+
| Ssl_server_not_after  | Apr 23 07:59:47 2026 UTC |
| Ssl_server_not_before | Jan 24 07:59:47 2025 UTC |
+-----------------------+--------------------------+
2 rows in set (0.011 sec)
```
