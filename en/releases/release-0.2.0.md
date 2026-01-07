---
title: TiDB Operator 0.2.0 Release Notes
summary: TiDB Operator 0.2.0 was released on September 11, 2018. Notable changes include experimental support for auto-failover, unification of Tiller and TiDB Operator managed resources labels, managing TiDB service via Tiller, adding toleration for TiDB cluster components, and refactoring upgrade functions as interface. Additionally, a script to set up DinD environment easily was added, and code was linted and formatted in CI.
---

# TiDB Operator 0.2.0 Release Notes

Release date: September 11, 2018

TiDB Operator version: 0.2.0

## Notable Changes

- Support auto-failover experimentally
- Unify Tiller managed resources and TiDB Operator managed resources labels (breaking change)
- Manage TiDB service via Tiller instead of TiDB Operator, allow more parameters to be customized (required for public cloud load balancer)
- Add toleration for TiDB cluster components (useful for dedicated deployment)
- Add script to easy setup DinD environment
- Lint and format code in CI
- Refactor upgrade functions as interface
