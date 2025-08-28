---
title: Tips for Troubleshooting TiDB on Kubernetes
summary: Learn the commonly used tips for troubleshooting TiDB on Kubernetes.
---

# Tips for Troubleshooting TiDB on Kubernetes

This document provides common tips for troubleshooting TiDB on Kubernetes.

## Modify the configuration of a TiKV instance

In some test scenarios, if you need to modify the configuration of a TiKV instance without affecting other instances, you can refer to the [Modify Configuration Dynamically](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-online) document and use SQL to modify the configuration of a single TiKV instance online.

> **Note:**
>
> The modification made by this method is temporary and not persistent. After the Pod is restarted, the original configuration will be used.
