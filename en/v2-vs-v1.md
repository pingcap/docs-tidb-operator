---
title: Comparison Between TiDB Operator v2 and v1
summary: Introduce the key differences between TiDB Operator v2 and v1.
---

# Comparison Between TiDB Operator v2 and v1

With the rapid development of TiDB and the Kubernetes ecosystem, the existing architecture and implementation of TiDB Operator v1 have encountered some challenges. To better adapt to these changes, TiDB Operator v2 introduces a major refactor of v1.

## Core changes in TiDB Operator v2

### Split the `TidbCluster` CRD

Initially, the TiDB cluster has only three core components: PD, TiKV, and TiDB. To simplify deployment and reduce user cognitive load, all components of the TiDB cluster are defined in a single CRD, `TidbCluster`. However, as TiDB evolves, this design faces several challenges:

- The number of TiDB cluster components has increased, with eight components currently defined in the `TidbCluster` CRD.
- To display status, the state of all nodes is defined in the `TidbCluster` CRD.
- Heterogeneous clusters are not considered initially, so additional `TidbCluster` CRs has to be introduced to support them.
- The `/scale` API is not supported, making it impossible to integrate with Kubernetes [HorizontalPodAutoscaler (HPA)](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).
- A large CR/CRD can cause difficult-to-resolve performance issues.

TiDB Operator v2 addresses these issues by splitting `TidbCluster` into multiple independent CRDs by component.

### Remove the StatefulSet dependency and manage Pods directly

Due to the complexity of TiDB clusters, Kubernetes' native deployment and StatefulSet controllers cannot fully meet TiDB's deployment and operation needs. TiDB Operator v1 manages all TiDB components using StatefulSet, but some limitations of StatefulSet prevent maximizing Kubernetes' capabilities, such as:

- StatefulSet restricts modifications to `VolumeClaimTemplate`, making native scaling impossible.
- StatefulSet enforces the order of scaling and rolling updates, causing repeated leader scheduling.
- StatefulSet requires all Pods under the same controller to have identical configurations, necessitating complex startup scripts to differentiate Pod parameters.
- There is no API for defining raft members, leading to semantic conflicts between restarting Pods and removing raft members, and no intuitive way to remove a specific TiKV node.

TiDB Operator v2 removes the dependency on StatefulSet and introduces the following CRDs:

- `Cluster`
- `ComponentGroup`
- `Instance`

These three-layer CRDs can manage Pods directly. TiDB Operator v2 uses the `ComponentGroup` CRD to manage nodes with common characteristics, reducing complexity, and the `Instance` CRD to facilitate management of individual stateful instances, providing instance-level operations and ensuring flexibility.

Benefits include:

- Better support for volume configuration changes.
- More reasonable rolling update order, such as restarting the leader last to prevent repeated leader migration.
- In-place upgrades for non-core components (such as log tail and istio), reducing the impact of TiDB Operator and infrastructure changes on the TiDB cluster.
- Graceful Pod restarts using `kubectl delete ${pod}` and rebuilding specific TiKV nodes using `kubectl delete ${instance}`.
- More intuitive status display.

### Introduce the Overlay mechanism and no longer manage Kubernetes fields unrelated to TiDB directly

Each new version of Kubernetes may introduce new fields that users need, but TiDB Operator may not care about these fields. In v1, a lot of development effort was spent supporting new Kubernetes features, including manually adding new fields to the `TidbCluster` CRD and propagating them. TiDB Operator v2 introduces the Overlay mechanism, which supports all new Kubernetes resource fields (especially for Pods) in a unified way. For details, see [Overlay](overlay.md).

### Other new features in TiDB Operator v2

#### Enhance validation capabilities

TiDB Operator v2 enhances configuration validation through Validation Rules and Validating Admission Policies, improving usability and robustness.

#### Support `/status` and `/scale` sub resources

TiDB Operator v2 supports CRD sub resources and can integrate with Kubernetes HPA for automated scaling.

#### Remove `tidb scheduler` component and support the evenly spread policy

TiDB Operator v2 supports configuring the evenly spread policy to distribute components evenly across regions and zones as needed, and removes the `tidb scheduler` component.

## Components and features not yet supported in TiDB Operator v2

### Components

#### `Binlog` (Pump + Drainer)

This component is deprecated. For more information, see [TiDB Binlog Overview](https://docs.pingcap.com/tidb/v8.3/tidb-binlog-overview/).

#### Dumpling + TiDB Lightning

TiDB Operator no longer provides direct support. It is recommended to use native Kubernetes jobs to run them.

#### `TidbInitializer`

TiDB Operator v2 no longer supports this CRD. You can use BootstrapSQL to run initialization SQL statements.

#### `TidbMonitor`

TiDB Operator v2 no longer supports this CRD. Because monitoring systems are often complex and varied, `TidbMonitor` is difficult to integrate into production-grade monitoring systems. TiDB provides more flexible solutions for integrating with common monitoring systems, rather than running a Prometheus + Grafana + Alert-Manager combination through CRD. For details, see [Deploy Monitoring and Alerts for a TiDB Cluster](monitor-a-tidb-cluster.md).

#### `TidbNgMonitoring`

Not supported yet.

#### `TidbDashboard`

Deployment through CRD is not supported. You can use the built-in dashboard or deploy it yourself through Deployment.

### Features

#### Cross-namespace deployment

Not supported due to potential security issues and unclear user scenarios.

#### Cross-Kubernetes cluster deployment

Not supported due to potential security issues and unclear user scenarios.

#### Back up and restore based on EBS volume snapshots

Backup based on EBS volume snapshots has the following unsolvable issues:

- High cost. EBS volume snapshots are very expensive.
- Long RTO. Recovery from EBS volume snapshots takes a long time.

With continuous optimization, TiDB BR performance has greatly improved, so backup and restore based on EBS volume snapshots is no longer necessary. Therefore, TiDB Operator v2 no longer supports this feature.
