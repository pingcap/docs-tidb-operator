---
title: What's New in TiDB Operator 1.3
---

# What's New in TiDB Operator 1.3

TiDB Operator 1.3 introduces the following key features, which helps you manage TiDB clusters and the tools more easily in terms of extensibility, usability, and security.

## Compatibility changes

- Enhance the feature of deploying a TiDB cluster across Kubernetes clusters. If you deploy a TiDB cluster across multiple Kubernetes clusters by TiDB Operator (<= v1.3.0-beta.1), upgrading TiDB Operator to v1.3.0 directly will cause failed rolling upgrade and the cluster might become abnormal. If you need to upgrade TiDB Operator from earlier versions to v1.3.0, take the following steps:

    1. Update CRD.
    2. Add a new `spec.acrossK8s` field in the TidbCluster spec and set it to `true`.
    3. Upgrade TiDB Operator.

- The `ValidatingWebhook` and `MutatingWebhook` of Pods are depricated. If you deploy Webhook in your TiDB cluster using TiDB Operator v1.2 or earlier versions, and enable `ValidatingWebhook` and `MutatingWebhook` of Pods, upgrading TiDB Operator to v1.3.0-beta.1 or later versions will cause `ValidatingWebhook` and `MutatingWebhook` to be deleted. But this has no impact on TiDB cluster management and does not affect the TiDB clusters in operation.

- Generate v1 CRD to support deploying in Kubernetes v1.22 or later versions. TiDB Operator with v1.3.0-beta.1 or later versions will set the default `baseImage` field of all components. If you use the field `image` instead of the field `baseImage` to set image, upgrading TiDB Operator to v1.3.0-beta.1 will cause TiDB Cluster to roll upgrade and even fail to run because using wrong image. You have to upgrade TiDB Operator by the following steps:
    1. Use fields `baseImage` and `version` to replace the field `image`, refer to the document [Configure TiDB deployment](configure-a-tidb-cluster.md#version).
    2. Upgrade TiDB Operator.

## Rolling upgrade changes

- Optimize the default configuration of TiFlash (>= v5.4.0). Since v1.3.0-beta.1, TiDB Operator optimizes the default configuration for TiFlash >= v5.4.0. If you deploy a TiDB cluster >= v5.4 using TiDB Operator v1.2, after upgrading TiDB Operator to v1.3.x, the TiFlash component will be rolling updated. It is recommended to upgrade TiDB Operator to v1.3.x before upgrading the TiDB cluster to v5.4.x.

- TiKV under specific configurations might be rolling updated. If you deploy TiDB v5.0 or later versions, and configure `spec.tikv.seperateRocksDBLog: true` or `spec.tikv.separateRaftLog: true`, upgrading TiDB Operator to v1.3.x will cause TiKV to be rolling updated.

- To support configuring Prometheus shards in the TidbMonitor CR, upgrading TiDB Operator to v1.3.x will cause the TidbMonitor Pod to be rolling updated.

## Extensibility

- [Deploying a TiDB cluster across multiple Kubernetes clusters](deploy-tidb-cluster-across-multiple-kubernetes.md) becomes generally available. Now you can deploy [heterogeneous TiDB clusters](deploy-heterogeneous-tidb-cluster.md) across Kubernetes clusters.
- Add a new `failover.recoverByUID` field to support one-time recovery for TiKV, TiFlash, and DM Worker.
- Support configuring [PodManagementPolicy](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#pod-management-policies) for the StatefulSets of TiDB cluster components.
- Support configuring DNS config for Pods of all components.
- Support Kubernetes >= v1.22.

## Usability

- Support [gracefully restarting a single TiKV Pod](restart-a-tidb-cluster.md#perform-a-graceful-restart-to-a-single-tikv-pod) by configuring annotation.
- Optimize the user experience of heterogeneous clusters. You can view monitoring metrics of a TiDB cluster and its heterogeneous cluster on the same Dashboard.
- Support [continuous profiling](access-dashboard.md#enable-continuous-profiling) for TiDB clusters.

## Security

- Add a new `spec.tidb.tlsClient.skipInternalClientCA` field to skip server certificate verification when internal components access TiDB.
- Add a new `spec.tidb.initializer.createPassword` field to support setting a random password for TiDB when deploying a new cluster.
- Use `secretRef` in TidbMonitor to obtain Grafana password to avoid plaintext password.
