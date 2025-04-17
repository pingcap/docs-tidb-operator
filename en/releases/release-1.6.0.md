---
title: TiDB Operator 1.6.0 Release Notes
summary: Learn about new features, improvements, and bug fixes in TiDB Operator 1.6.0.
---

# TiDB Operator 1.6.0 Release Notes

Release date: May 28, 2024

TiDB Operator version: 1.6.0

## New features

- Support setting `maxSkew`, `minDomains`, and `nodeAffinityPolicy` in `topologySpreadConstraints` for components of a TiDB cluster ([#5617](https://github.com/pingcap/tidb-operator/pull/5617), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting additional command-line arguments for TiDB components ([#5624](https://github.com/pingcap/tidb-operator/pull/5624), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting `nodeSelector` for the TidbInitializer component ([#5594](https://github.com/pingcap/tidb-operator/pull/5594), [@csuzhangxc](https://github.com/csuzhangxc))

## Improvements

- Support automatically setting location labels for TiProxy ([#5649](https://github.com/pingcap/tidb-operator/pull/5649), [@djshow832](https://github.com/djshow832))
- Support retrying leader eviction during TiKV rolling restart ([#5613](https://github.com/pingcap/tidb-operator/pull/5613), [@csuzhangxc](https://github.com/csuzhangxc))
- Support setting the `advertise-addr` command-line argument for the TiProxy component ([#5608](https://github.com/pingcap/tidb-operator/pull/5608), [@djshow832](https://github.com/djshow832))

## Bug fixes

- Fix the issue that modifying the storage size of components might cause them to restart when `configUpdateStrategy` is set to `InPlace` ([#5602](https://github.com/pingcap/tidb-operator/pull/5602), [@ideascf](https://github.com/ideascf))
- Fix the issue that recreating the TiKV StatefulSet might cause TiKV to enter the `Upgrading` phase ([#5551](https://github.com/pingcap/tidb-operator/pull/5551), [@ideascf](https://github.com/ideascf))
