---
title: 特性门控
summary: 介绍如何配置 TiDB 集群的特性门控
---

# 特性门控

TiDB Operator 支持通过 Cluster CR 上的 `spec.featureGates` 开启或关闭一些不成熟或者可能导致组件重启的特性。

## 特性门控列表


| 特性 | 默认值 | 阶段 | 自从 | 直到 |
|:---|:---|:---|:---|:---|
| FeatureModification            | false | Alpha | 2.0 | - |
| VolumeAttributesClass          | false | Alpha | 2.0 | - |
| DisablePDDefaultReadinessProbe | false | Alpha | 2.0 | - |
| UsePDReadyAPI                  | false | Alpha | 2.0 | - |
| SessionTokenSigning            | false | Alpha | 2.0 | - |

## 阶段

### Alpha

Alpha 阶段的特性有如下特征

- 默认关闭
- 建议只在新建集群时开启。
- 不一定支持对已经创建的集群开启或关闭
- 启用此特性可能会有错误
- 建议未充分测试的情况不在生产环境下开启

### Beta

Beta 阶段的特性有如下特征

- 通常已经经过良好的测试
- 建议对所有新建集群开启
- 通常支持对已经创建的集群开启或关闭(可能重启组件)

### GA

GA 阶段的特性有如下特征

- 通常已经经过长期的测试
- 默认开启，并不支持关闭

## 特性说明

### FeatureModification

开启后支持变更 `spec.featureGates`.

### VolumeAttributesClass

开启后支持变更 PVC 的 VolumeAttributesClass. 需要 Kubernetes 支持对应功能, 详见 [VolumeAttributesClass](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/)

### DisablePDDefaultReadinessProbe

需要重启: [PD]

开启后不再通过 tcp ping 来检查 PD 的 readiness

### UsePDReadyAPI

需要重启: [PD]

开启后通过 `/ready` 来检查 PD 的 readiness, 详见 https://github.com/tikv/pd/pull/8749

### SessionTokenSigning

需要重启: [TiDB]

开启后 TiDB 会配置 `session-token-signing-cert` 和 `session-token-signing-key`, 详见 [TiDB 配置文件](https://docs.pingcap.com/tidb/stable/tidb-configuration-file/#session-token-signing-cert-new-in-v640)
