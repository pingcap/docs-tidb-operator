---
title: TiDB Operator 1.6.0-beta.1 Release Notes
---

# TiDB Operator 1.6.0-beta.1 Release Notes

Release date: March 27, 2024

TiDB Operator version: 1.6.0-beta.1

## New Feature

- Support deploying PD v8.0.0+ in [microservice mode](https://docs.pingcap.com/tidb/dev/pd-microservices) (experimental) ([#5398](https://github.com/pingcap/tidb-operator/pull/5398), [@HuSharp](https://github.com/HuSharp))
- Support scaling out/in TiDB component parallelly  ([#5570](https://github.com/pingcap/tidb-operator/pull/5570), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting `livenessProbe` and `readinessProbe` for Discovery component ([#5565](https://github.com/pingcap/tidb-operator/pull/5565), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting `startupProbe` for TiDB component ([#5588](https://github.com/pingcap/tidb-operator/pull/5588), [@fgksgf](https://github.com/fgksgf))

## Improvements

- Upgrade Kubernetes dependency to v1.28, it is recommended not to deploy tidb-scheduler anymore ([#5495](https://github.com/pingcap/tidb-operator/pull/5495), [@csuzhangxc](https://github.com/csuzhangxc))
- When deploying via Helm Chart, support setting lock resource for tidb-controller-manager for leader election, default value is `.Values.controllerManager.leaderResourceLock: leases`. When upgrading from versions before v1.6 to v1.6.0-beta.1 and later versions, it is recommended to first set `.Values.controllerManager.leaderResourceLock: endpointsleases` and wait for the new tidb-controller-manager to run normally before setting to `.Values.controllerManager.leaderResourceLock: leases` to update the deployment ([#5450](https://github.com/pingcap/tidb-operator/pull/5450), [@csuzhangxc](https://github.com/csuzhangxc))
- Support for TiFlash to directly mount ConfigMap without relying on InitContainer to process configuration files ([#5552](https://github.com/pingcap/tidb-operator/pull/5552), [@ideascf](https://github.com/ideascf))
- Add check for `resources.request.storage` in TiFlash `storageClaims` configuration ([#5489](https://github.com/pingcap/tidb-operator/pull/5489), [@unw9527](https://github.com/unw9527))

## Bug fixes

- Fix the issue that the last TiKV Pod was not checked for `tikv-min-ready-seconds` during rolling restart of TiKV ([#5544](https://github.com/pingcap/tidb-operator/pull/5544), [@wangz1x](https://github.com/wangz1x))
- Fix the issue that the TiDB cluster could not start when only non `cluster.local` clusterDomain TLS certificates could be used ([#5560](https://github.com/pingcap/tidb-operator/pull/5560), [@csuzhangxc](https://github.com/csuzhangxc))
