---
title: TiDB Operator 1.6.0-beta.1 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.0-beta.1.
---

# TiDB Operator 1.6.0-beta.1 Release Notes

Release date: March 27, 2024

TiDB Operator version: 1.6.0-beta.1

## New features

- Support deploying PD v8.0.0 and later versions in [microservice mode](https://docs.pingcap.com/tidb/dev/pd-microservices) (experimental) ([#5398](https://github.com/pingcap/tidb-operator/pull/5398), [@HuSharp](https://github.com/HuSharp))
- Support scaling out or in TiDB components in parallel ([#5570](https://github.com/pingcap/tidb-operator/pull/5570), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting `livenessProbe` and `readinessProbe` for the Discovery component ([#5565](https://github.com/pingcap/tidb-operator/pull/5565), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting `startupProbe` for TiDB components ([#5588](https://github.com/pingcap/tidb-operator/pull/5588), [@fgksgf](https://github.com/fgksgf))

## Improvements

- Upgrade Kubernetes dependency to v1.28, and it is not recommended to deploy tidb-scheduler ([#5495](https://github.com/pingcap/tidb-operator/pull/5495), [@csuzhangxc](https://github.com/csuzhangxc))
- When deploying using Helm chart, support setting lock resource used by tidb-controller-manager for leader election, with the default value of `.Values.controllerManager.leaderResourceLock: leases`. When upgrading from versions before v1.6 to v1.6.0-beta.1 and later versions, it is recommended to first set `.Values.controllerManager.leaderResourceLock: endpointsleases` and wait for the new tidb-controller-manager to run normally before setting it to `.Values.controllerManager.leaderResourceLock: leases` to update the deployment ([#5450](https://github.com/pingcap/tidb-operator/pull/5450), [@csuzhangxc](https://github.com/csuzhangxc))
- Support for TiFlash to directly mount ConfigMap without relying on an InitContainer to process configuration files ([#5552](https://github.com/pingcap/tidb-operator/pull/5552), [@ideascf](https://github.com/ideascf))
- Add check for `resources.request.storage` in the `storageClaims` configuration of TiFlash ([#5489](https://github.com/pingcap/tidb-operator/pull/5489), [@unw9527](https://github.com/unw9527))

## Bug fixes

- Fix the issue that the `tikv-min-ready-seconds` check is not performed on the last TiKV Pod during a rolling restart of TiKV ([#5544](https://github.com/pingcap/tidb-operator/pull/5544), [@wangz1x](https://github.com/wangz1x))
- Fix the issue that the TiDB cluster cannot start when only non-`cluster.local` clusterDomain TLS certificates are available ([#5560](https://github.com/pingcap/tidb-operator/pull/5560), [@csuzhangxc](https://github.com/csuzhangxc))
