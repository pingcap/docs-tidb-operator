---
title: What's New in TiDB Operator v1.6
summary: Learn about new features in TiDB Operator 1.6.0.
---

# What's New in TiDB Operator v1.6

TiDB Operator 1.6 introduces the following key features, which helps you manage TiDB clusters and the tools more easily in terms of extensibility and usability.

## Compatibility changes

- Upgrade Kubernetes dependency to v1.28, and it is not recommended to deploy `tidb-scheduler`.
- When deploying using Helm chart, support setting lock resource used by `tidb-controller-manager` for leader election, with the default value of `.Values.controllerManager.leaderResourceLock: leases`. When upgrading TiDB Operator to v1.6.0-beta.1 or a later version, it is recommended to first set `.Values.controllerManager.leaderResourceLock: endpointsleases` and wait for the new `tidb-controller-manager` to run normally before setting it to `.Values.controllerManager.leaderResourceLock: leases` to update the deployment.

## Extensibility

- Support deploying PD v8.0.0 and later versions in [microservice mode](https://docs.pingcap.com/tidb/dev/pd-microservices) (experimental).
- Support scaling out or in TiDB components in parallel.

## Usability

- Support automatically setting location labels for TiProxy.
- Support setting `maxSkew`, `minDomains`, and `nodeAffinityPolicy` in `topologySpreadConstraints` for components of a TiDB cluster.
- Support setting `startupProbe` for TiDB components.
- Support setting additional command-line arguments for TiDB components.
- Support setting `livenessProbe` and `readinessProbe` for the Discovery component.
- Support setting `nodeSelector` for the TidbInitializer component.
- Enable TiFlash to directly mount ConfigMap without relying on an InitContainer to process configuration files.
