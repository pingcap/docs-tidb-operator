---
title: Tips for troubleshooting TiDB on Kubernetes
summary: Learn the commonly used tips for troubleshooting TiDB on Kubernetes.
---

# Tips for troubleshooting TiDB on Kubernetes

This document describes the commonly used tips for troubleshooting TiDB on Kubernetes.

## Modify the configuration of a TiKV instance

In some test scenarios, if you need to modify the configuration of a TiKV instance and do not want the configuration to affect other instances, you can refer to the [document](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-online) and use SQL to online modify the configuration of a single TiKV instance.

> **Note:**
>
> The modification made by this method is temporary and not persistent. After the Pod is restarted, the original configuration will be used.
