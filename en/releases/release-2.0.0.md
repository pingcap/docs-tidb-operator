---
title: TiDB Operator 2.0.0 Release Notes
summary: TiDB Operator 2.0.0 is released. The v2 version introduces major refactoring from v1, with key changes including splitting the `TidbCluster` CRD into multiple CRDs, removing the dependency on StatefulSet, and introducing the Overlay feature for more flexible custom configurations.
---

# TiDB Operator 2.0.0 Release Notes

Release date: December 18, 2025

TiDB Operator version: 2.0.0

With the rapid development of TiDB and the Kubernetes ecosystem, TiDB Operator releases v2.0.0, which includes comprehensive refactoring from v1 to provide a more stable, efficient, and maintainable cluster management experience.

For a detailed comparison between v2 and v1, see [Comparison Between TiDB Operator v2 and v1](../v2-vs-v1.md).

## Major changes and improvements

### Core architecture refactoring

TiDB Operator v2 includes a comprehensive redesign of the v1 architecture, with the following key changes:

- **CRD splitting**: split the v1 `TidbCluster` CRD into multiple independent CRDs for more granular component management, improving maintainability and flexibility.
- **Direct Pod management**: remove the dependency on StatefulSet. Pods are now managed directly, providing higher flexibility and more precise control over Pod lifecycle and scheduling behavior.
- **Controller architecture upgrade**: implement controller logic based on the [controller-runtime](https://github.com/kubernetes-sigs/controller-runtime) framework. This simplifies controller development, improves development efficiency, and enhances system stability and reliability.

### New features and enhancements

- **Support the Overlay field**:
    - Enable you to flexibly specify all Kubernetes-supported fields for Pods without modifying the TiDB Operator source code.
    - Provide security validation mechanisms to prevent accidental overwrites of critical system labels.

- **Support topology-aware scheduling**:
    - Support the `EvenlySpread` strategy to evenly distribute Pods across topology domains.
    - Support topology weight configuration for flexible control of instance distribution ratios across topology domains.
    - Enhance cluster high availability and fault tolerance.

- **Enhance the field validation**:
    - Integrate Kubernetes [Validation Rules](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) and [Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/).
    - Support field format and value range validation.
    - Provide clear and user-friendly error messages to facilitate troubleshooting.

- **Support [CRD subresources](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#subresources)**:
    - Support the `status` subresource for unified status management.
    - Support the `scale` subresource to integrate with [HorizontalPodAutoscaler (HPA)](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/), enabling auto-scaling.
    - Improve compatibility with the Kubernetes ecosystem.

- **Support feature gates to control change behavior**:
    - You can use [Feature Gates](../feature-gates.md) to control changes that might trigger cluster node restarts, reducing the impact on cluster stability.

- **Support canceling TiKV and TiFlash scale-in operations**:
    - If you add new TiKV or TiFlash nodes while a scale-in operation is in progress, TiDB Operator prioritizes canceling the scale-in for nodes that are not yet fully decommissioned. This prevents the unnecessary re-creation of nodes.

### Removed features

- Remove the support for [Backup and Restore Based on EBS Volume Snapshots](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/volume-snapshot-backup-restore/).
- Remove the `tidb-scheduler` component.
- Remove the following CRDs: `TiDBInitializer`, `TiDBDashboard`, `DMCluster`, `FedVolumeBackup`, `FedVolumeBackupSchedule`, and `FedVolumeRestore`.
- Remove the `TiDBMonitor` and `TiDBNGMonitoring` CRDs. Related features are integrated through other methods. For details, see [Deploy Monitoring and Alerts for a TiDB Cluster](../monitor-a-tidb-cluster.md).

## Acknowledgments

Thanks to all the developers and community members who contributed to TiDB Operator! We look forward to your feedback and suggestions to help us improve this milestone release.
