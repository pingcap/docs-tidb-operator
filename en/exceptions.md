---
title: Common Cluster Exceptions of TiDB on Kubernetes
summary: Learn the common exceptions during the operation of TiDB clusters on Kubernetes and their solutions.
---

# Common Cluster Exceptions of TiDB on Kubernetes

This document describes common exceptions during the operation of TiDB clusters on Kubernetes and their solutions.

## Persistent connections are abnormally terminated in TiDB

Load balancers often set the idle connection timeout. If no data is sent via a connection for a specific period of time, the load balancer closes the connection.

- If a persistent connection is terminated when you use TiDB, check the middleware program between the client and the TiDB server.
- If the idle timeout is not long enough for your query, try to set the timeout to a larger value. If you cannot reset it, enable the `tcp-keep-alive` option in TiDB.

On Linux, the keepalive probe packet is sent every 7,200 seconds by default. To shorten the interval, configure `sysctls` via the `podSecurityContext` field.

- If `--allowed-unsafe-sysctls=net.*` can be configured for [kubelet](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/) in the Kubernetes cluster, configure TiDBGroup using the [Overlay](overlay.md) feature as follows:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiDBGroup
    spec:
      template:
        spec:
          overlay:
            pod:
              spec:
                securityContext:
                  sysctls:
                    - name: net.ipv4.tcp_keepalive_time
                      value: "300"
    ```

- If `--allowed-unsafe-sysctls=net.*` cannot be configured for [kubelet](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/) in the Kubernetes cluster, configure TiDBGroup using the [Overlay](overlay.md) feature as follows:

    ```yaml
    apiVersion: core.pingcap.com/v1alpha1
    kind: TiDBGroup
    spec:
      template:
        spec:
          overlay:
            pod:
              spec:
                initContainers:
                  - name: init
                    image: busybox
                    commands:
                      - "sh"
                      - "-c"
                      - "sysctl"
                      - "-w"
                      - "net.ipv4.tcp_keepalive_time=300"
                    securityContext:
                      privileged: true
    ```
