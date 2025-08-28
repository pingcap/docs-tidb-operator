---
title: Kubernetes 上的 TiDB 集群常见异常
summary: 介绍 TiDB 集群运行过程中常见异常以及处理办法。
---

# Kubernetes 上的 TiDB 集群常见异常

本文介绍 TiDB 集群运行过程中常见异常以及处理办法。

## TiDB 长连接被异常中断

许多负载均衡器 (Load Balancer) 会设置连接空闲超时时间。当连接上没有数据传输的时间超过设定值，负载均衡器会主动将连接中断。若发现 TiDB 使用过程中，长查询会被异常中断，可检查客户端与 TiDB 服务端之间的中间件程序。若其连接空闲超时时间较短，可尝试增大该超时时间。若不可修改，可打开 TiDB `tcp-keep-alive` 选项，启用 TCP keepalive 特性。

默认情况下，Linux 发送 keepalive 探测包的等待时间为 7200 秒。若需减少该时间，可通过 `podSecurityContext` 字段配置 `sysctls`。

- 如果 Kubernetes 集群内的 [kubelet](https://kubernetes.io/zh-cn/docs/reference/command-line-tools-reference/kubelet/) 允许配置 `--allowed-unsafe-sysctls=net.*`，请使用 [Overlay](overlay.md) 功能按如下方式配置 TiDBGroup：

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

- 如果 Kubernetes 集群内的 [kubelet](https://kubernetes.io/zh-cn/docs/reference/command-line-tools-reference/kubelet/) 不允许配置 `--allowed-unsafe-sysctls=net.*`，请使用 [Overlay](overlay.md) 功能按如下方式配置 TiDBGroup：

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
