---
title: TiDB Operator Architecture
summary: Learn about the architecture of TiDB Operator and how it works.
---

# TiDB Operator Architecture

This document introduces the architecture of TiDB Operator and how it works.

## Architecture

The following diagram shows an overview of the TiDB Operator architecture:

![TiDB Operator Architecture](/media/tidb-operator-architecture.png)

The diagram includes several resource objects defined by [Custom Resource Definitions (CRDs)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/), such as `Cluster`, `PDGroup`, `PD`, `TiKVGroup`, `TiKV`, `TiDBGroup`, `TiDB`, `Backup`, and `Restore`. The following describes some of these resources:

- `Cluster`: represents a complete TiDB cluster. It contains shared configuration and feature flags for the TiDB cluster and reflects the overall cluster status. This CRD is designed as the "namespace" for the TiDB cluster, and all components in the cluster must reference a `Cluster` CR.
- `ComponentGroup`: describes a group of TiDB cluster components with the same configuration. For example:

    - `PDGroup`: a group of PD instances with the same configuration.
    - `TiKVGroup`: a group of TiKV instances with the same configuration.
    - `TiDBGroup`: a group of TiDB instances with the same configuration.

- `Component`: describes an individual TiDB cluster component. For example:

    - `PD`: a single PD instance.
    - `TiKV`: a single TiKV instance.
    - `TiDB`: a single TiDB instance.

- `Backup`: describes a backup task for the TiDB cluster.
- `Restore`: describes a restore task for the TiDB cluster.

## Control flow

TiDB Operator uses a declarative API to automate cluster management by continuously monitoring user-defined resources. The core workflow is as follows:

1. The user creates `Cluster` and other component Custom Resource (CR) objects through `kubectl`, such as `PDGroup`, `TiKVGroup`, and `TiDBGroup`.
2. TiDB Operator continuously watches these CRs and dynamically adjusts the corresponding `Pod`, `PVC`, and `ConfigMap` objects based on the actual cluster state.

Through this control (reconciliation) loop, TiDB Operator can automatically perform cluster node health checks and failure recovery. Operations such as deployment, upgrades, and scaling can also be completed with one action by modifying the `Cluster` and other component CRs.

The following diagram shows the control flow using TiKV as an example:

![TiDB Operator Control Flow](/media/tidb-operator-control-flow.png)

In this workflow:

- TiKVGroup Controller: watches the `TiKVGroup` CR and creates or updates the corresponding `TiKV` CR based on its configuration.
- TiKV Controller: watches the `TiKV` CR and creates or updates related resources such as Pod, PVC, and ConfigMap based on the configuration in the CR.
