---
title: Renew and Replace the TLS Certificate
summary: Learn how to renew and replace TLS certificates between TiDB components.
---

# Renew and Replace the TLS Certificate

This document introduces how to renew and replace certificates of the corresponding components before certificates expire, taking TLS certificates between PD, TiKV, and TiDB components in the TiDB cluster as an example.

If you need to renew and replace certificates between other components in the TiDB cluster, TiDB server-side certificate, or MySQL client-side certificate, you can take similar steps to complete the operation.

The renewal and replacement operations in this document assume that the original certificates have not expired. If the original certificates expire or become invalid, to generate new certificates and restart the TiDB cluster, refer to [Enable TLS between TiDB components](enable-tls-between-components.md) or [Enable TLS for MySQL client](enable-tls-for-mysql-client.md).

## Renew and replace the certificate issued by `cert-manager`

If the original TLS certificate is issued by [the `cert-manager` system](enable-tls-between-components.md#step-1-generate-certificates-for-components-of-the-tidb-cluster), and the original certificate has not expired, the procedure varies with whether to renew the CA certificate.

### Renew and replace the CA certificate

<!-- TODO -->

### Only renew and replace certificates between components

When using cert-manager to issue certificates, you can configure the `spec.renewBefore` field of the `Certificate` resource to have cert-manager automatically renew the certificate before it expires.

1. cert-manager supports automatic renewal of component certificates and their corresponding Kubernetes Secret objects before expiration. To renew manually, refer to [Renew certificates using cmctl](https://cert-manager.io/docs/reference/cmctl/#renew).

2. For certificates between components, each component automatically reloads the new certificates when creating the new connection later.

    > **Note:**
    >
    > - Currently, each component does not support [reload CA certificates](https://docs.pingcap.com/tidb/stable/enable-tls-between-components#reload-certificates) automatically, you need to refer to [renew and replace the CA certificate and certificates between components](#renew-and-replace-the-ca-certificate).
    > - For the TiDB server-side certificate, you can manually reload by referring to any of the following methods:
    >     - Refer to [Reload certificate, key, and CA](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#reload-certificate-key-and-ca).
    >     - Refer to [Rolling restart the TiDB Cluster](restart-a-tidb-cluster.md) to perform a rolling restart of TiDB server.
