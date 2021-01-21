---
title: Renew and Replace the TLS Certificate
summary: Learn how to renew and replace TlS certificates between TiDB components.
---

# Renew and Replace the TLS Certificate

This document introduces how to renew and replace certificate of the corresponding components before certificate expire, taking TLS certificates between PD, TiKV and TiDB components in the TiDB cluster for example.

If you need to renew and replace certificates between other components in the TiDB cluster, TiDB Server certificate, or MySQL Client certificate, you can take similar steps.

The renewal and replacement operations in this document assume that the original certificate have not expired. If the original certificates expire or become invalid, to generate new certificates and restart the TiDB cluster, refer to [Enable TLS between TiDB components](enable-tls-between-components.md) or [Enable TLS for MySQL client](enable-tls-for-mysql-client.md).

## Renew and replace certificates issued by the `cfssl` system

For example, the original TLS certificates are issued by [the `cfssl system](enable-tls-between-components.md#using-cfssl) and the original certificates have not expired. You can renew and replace the certificates between PD, TiKV and TiDB components as follows.

### Renew and replace the CA certificate

> **Note:**
>
> If you don't need to renew the CA certificate, you can skip the operations in this section and directly refer to [renew and replace certificates between components] (#renew-and-replace-certificates-between-components).

1. Back up the original CA certificate and key.

    {{< copyable "shell-regular" >}}

    ```shell
    mv ca.pem ca.old.pem && \
    mv ca-key.pem ca-key.old.pem
    ```

2. Generate the new CA certificate and key based on the configuration of original CA certificate and certificate signing request (CSR).

    {{< copyable "shell-regular" >}}

    ```shell
    cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
    ```

    > **Note:**
    >
    > If necessary, you can update the configuration file and `expiry` in CSR.

3. Back up the new CA certificate and key, and generate a combined CA certificate based on the original CA certificate and the new CA certificate.

    {{< copyable "shell-regular" >}}

    ```shell
    mv ca.pem ca.new.pem && \
    mv ca-key.pem ca-key.new.pem && \
    cat ca.new.pem ca.old.pem > ca.pem
    ```

4. Update each corresponding Kubernetes Secret objects based on the combined CA certificate.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${cluster_name}-pd-cluster-secret --namespace=${namespace} --from-file=tls.crt=pd-server.pem --from-file=tls.key=pd-server-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-tikv-cluster-secret --namespace=${namespace} --from-file=tls.crt=tikv-server.pem --from-file=tls.key=tikv-server-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-tidb-cluster-secret --namespace=${namespace} --from-file=tls.crt=tidb-server.pem --from-file=tls.key=tidb-server-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-cluster-client-secret --namespace=${namespace} --from-file=tls.crt=client.pem --from-file=tls.key=client-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    ```

    In the above command, `${cluster_name}` is the name of the cluster, and `${namespace}` is the namespace deployed for the TiDB cluster.

    > **Note:**
    >
    > The above command only renews the server-side CA certificate and the client-side CA certificate between PD, TiKV, and TiDB components. If you need to renew other server-side CA certificates such as TiCDC, TiFlash, etc., you can execute similar command.

5. Perform the rolling restart to those components that need to load the combined CA certificate, refer to [perform a rolling restart to the TiDB cluster](restart-a-tidb-cluster.md).

    After the completion of rolling restart, based on the combined CA certificate, each component can accept the certificate issued by the original CA certificate and the new CA certificate at the same time.

### Renew and replace certificates between components

> **Note:**
>
> Before renewing and replacing certificates between components, make sure that the CA certificate can verify the certificates between components before and after the renewal as valid. If you [renew and replace the CA certificate](#renew-and-replace-the-CA-certificate), make sure that you complete restarting the TiDB cluster based on the new CA certificate.

1. Generate new server-side and client-side certificates based on the original configuration information of each component.

    {{< copyable "shell-regular" >}}

    ```shell
    cfssl gencert -ca=ca.new.pem -ca-key=ca-key.new.pem -config=ca-config.json -profile=internal pd-server.json | cfssljson -bare pd-server
    cfssl gencert -ca=ca.new.pem -ca-key=ca-key.new.pem -config=ca-config.json -profile=internal tikv-server.json | cfssljson -bare tikv-server
    cfssl gencert -ca=ca.new.pem -ca-key=ca-key.new.pem -config=ca-config.json -profile=internal tidb-server.json | cfssljson -bare tidb-server
    cfssl gencert -ca=ca.new.pem -ca-key=ca-key.new.pem -config=ca-config.json -profile=client client.json | cfssljson -bare client
    ```

    > **Note:**
    >
    > - In the above command, assume that you refer to steps in [renew and replace the TLS Certificate](#renew-and-replace-the-tls-certificate) to back up the new CA certificate as `ca.new.pem` and key as `ca-key.new.pem`. If you do not renew the CA certificate and key, modify the corresponding parameters in the command to `ca.pem` and `ca-key.pem`.
    > - The above command only generates the server-side and the client-side certificates between PD, TiKV, and TiDB components. If you need to generate other server-side certificates such as TiCDC, TiFlash, etc., you can execute similar command.

2. Update each corresponding Kubernetes Secret objects based on the newly generated server-side and client-side certificates.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${cluster_name}-pd-cluster-secret --namespace=${namespace} --from-file=tls.crt=pd-server.pem --from-file=tls.key=pd-server-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-tikv-cluster-secret --namespace=${namespace} --from-file=tls.crt=tikv-server.pem --from-file=tls.key=tikv-server-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-tidb-cluster-secret --namespace=${namespace} --from-file=tls.crt=tidb-server.pem --from-file=tls.key=tidb-server-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-cluster-client-secret --namespace=${namespace} --from-file=tls.crt=client.pem --from-file=tls.key=client-key.pem --from-file=ca.crt=ca.pem --dry-run=client -o yaml | kubectl apply -f -
    ```

    In the above command, `${cluster_name}` is the name of the cluster, and `${namespace}` is the namespace deployed for the TiDB cluster.

    > **Note:**
    >
    >  The above command only renews the server-side and the client-side certificate between PD, TiKV, and TiDB components. If you need to renew other server-side certificates such as TiCDC, TiFlash, etc., you can execute similar command.

3. Perform the rolling restart to those components that need to load the combined CA certificate, refer to [perform a rolling restart to the TiDB cluster](restart-a-tidb-cluster.md).

    After the completion of rolling restart, each component use the new certificate for TLS communication. If you refer to [Renew and replace the CA certificate](#renew-and-replace-the-ca-certificate) and make each component load the combined CA certificate, each component can still accept the certificate issued by the original CA certificate.

### Optional: Remove the original CA certificate in the combined CA certificate

If you refer to [Update and replace CA certificate](#Update and replace-ca-certificate) and [Update and replace inter-component certificate](#Update and replace inter-component certificate) to update and replace the combined CA certificate and Server side, Client If you plan to remove the original CA certificate (if the original CA certificate has expired or the key of the original CA certificate is stolen), you can remove the original CA certificate as follows.

If you renew and replace the combined CA certificate, server-side and client-side certificates between components by referring to [Renew and replace the CA certificate](#renew-and-replace-the-ca-certificate) and [Renew and replace certificates between components](#renew-and-replace-certificates-between-components), you can remove the original CA certificate by the following steps.

1. Renew the Kubernetes Secret object based on the new CA certificate.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic ${cluster_name}-pd-cluster-secret --namespace=${namespace} --from-file=tls.crt=pd-server.pem --from-file=tls.key=pd-server-key.pem --from-file=ca.crt=ca.new.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-tikv-cluster-secret --namespace=${namespace} --from-file=tls.crt=tikv-server.pem --from-file=tls.key=tikv-server-key.pem --from-file=ca.crt=ca.new.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-tidb-cluster-secret --namespace=${namespace} --from-file=tls.crt=tidb-server.pem --from-file=tls.key=tidb-server-key.pem --from-file=ca.crt=ca.new.pem --dry-run=client -o yaml | kubectl apply -f -
    kubectl create secret generic ${cluster_name}-cluster-client-secret --namespace=${namespace} --from-file=tls.crt=client.pem --from-file=tls.key=client-key.pem --from-file=ca.crt=ca.new.pem --dry-run=client -o yaml | kubectl apply -f -
    ```

    In the above command, `${cluster_name}` is the name of the cluster, and `${namespace}` is the namespace deployed for the TiDB cluster.

    > **Note:**
    >
    > In the above command, assume that you refer to steps in [renew and replace the TLS Certificate](#renew-and-replace-the-tls-certificate) to back up the new CA certificate as `ca.new.pem`.

2. Perform the rolling restart to those components that need to load the combined CA certificate, refer to [perform a rolling restart to the TiDB cluster](restart-a-tidb-cluster.md).

    After the completion of rolling restart, each component can only accept the certificate issued by the new CA certificate.

## Renew and replace the certificate issued by the`cert-manager`

If the original TLS certificate is issued by [the `cert-manager` system](enable-tls-between-components.md#using-cert-manager), and the original certificate has not expired, you can handle with the issue separately according to whether to renew the CA certificate.

### Renew and replace the CA certificate and certificates between components

When using cert-manager to issue the certificate, by specifying the `spec.renewBefore` of the `Certificate` resource, the cert-manager can automatically update the certificate before it expires.

However, although cert-manager can automatically update the CA certificate and the corresponding Kubernetes Secret object, it currently does not support merging the old and new CA certificates into a combined CA certificate to accept certificates issued by the new and original CA certificates at the same time. Therefore, in the process of updating and replacing the CA certificate, the issue that TLS between cluster components cannot authenticate each other might occur.

> **Warning:**
>
> Because the certificates issued by the new and original CAs cannot be accepted between components at the same time, renewing and replacing certificates needs to rebuild the Pods of some components, which may cause some requests to access the TiDB cluster to fail.

The steps to renew and replace the CA certificates of PD, TiKV, TiDB and certificates between components are as follows.

1. The cert-manager automatically updates the CA certificate and the Kubernetes Secret object `${cluster_name}-ca-secret` before the certificate expires.

    `${cluster_name}` is the name of the cluster.

    To manually update the CA certificate, you can directly delete the corresponding Kubernetes Secret objects and trigger the cert-manager to regenerate the CA certificate.

2. Delete the Kubernetes Secret objects corresponding to the certificate of each component.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete secret ${cluster_name}-pd-cluster-secret --namespace=${namespace}
    kubectl delete secret ${cluster_name}-tikv-cluster-secret --namespace=${namespace}
    kubectl delete secret ${cluster_name}-tidb-cluster-secret --namespace=${namespace}
    kubectl delete secret ${cluster_name}-cluster-client-secret --namespace=${namespace}
    ```

    In the above command, `${cluster_name}` is the name of the cluster, and `${namespace}` is the namespace deployed for the TiDB cluster.

3. Wait for the cert-manager to issue new certificates for each component based on the new CA certificate.

    Observe the output of `kubectl get secret --namespace=${namespace}` until the Kubernetes Secret objects corresponding to all components are created.

4. Rebuild the Pod of PD, TiKV and TiDB component in sequence forcibly.

    Because the cert-manager does not support combined CA certificates, if you try to perform a rolling update of each component, the Pods that use the new and old CAs to issue certificates can not communicate normally based on TLS. Therefore, you need to delete the Pod forcibly and rebuild the Pod based on the certificate issued by the new CA.

    {{< copyable "shell-regular" >}}

    ```
    kubectl delete -n ${namespace} pod ${pod_name}
    ```

    In the above command, `${namespace}` is the namespace deployed by the TiDB cluster, and the `${pod_name}` is the Pod name of each replica of PD, TiKV and TiDB.

### Only update and replace certificates between components

1. The cert-manager automatically updates the certificate of each component and the Kubernetes Secret object before the certificate expires.

    The `${cluster_name}` is the name of the cluster.

    To manually update the CA certificate, you can directly delete the corresponding Kubernetes Secret object and trigger cert-manager to regenerate the CA certificate.

    For PD, TiKV and TiDB components, the namespace deployed by the TiDB cluster includes the following Kubernetes Secret objects:

    {{< copyable "shell-regular" >}}

    ```
    ${cluster_name}-pd-cluster-secret
    ${cluster_name}-tikv-cluster-secret
    ${cluster_name}-tidb-cluster-secret
    ${cluster_name}-cluster-client-secret
    ```

    In the above command, `${cluster_name}` is the name of the cluster.

    If you want to manually update the certificate between components, you can directly delete the corresponding Kubernetes Secret objects and trigger cert-manager to regenerate the certificate between components.

2. For certificates between components, each component automatically reloads the new certificates when creating the new connection later without manual operation.

    > **Note:**
    >
    > - Currently, each component does not support [reload certificates](https://docs.pingcap.com/tidb/stable/enable-tls-between-components#reload-certificates) manually，you need to refer to [Renew and replace the CA certificate and certificates between components](#renew-and-replace-the-ca-certificate-and-certificates-between-components).
    > - For the TiDB Server certificate, you can manually reload by referring to any of the following methods:
    >     - Refer to [Reload certificate, key, and CA](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#reload-certificate-key-and-ca)。
    >     - Refer to [Rolling Restart TiDB Cluster](restart-a-tidb-cluster.md) to perform a rolling restart of TiDB Server.