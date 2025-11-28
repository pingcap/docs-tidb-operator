---
title: Feature Gates
summary: Introduce how to configure feature gates of a TiDB cluster
---

# Feature Gates

TiDB Operator supports to enable/disable feature gates by the field `spec.featureGates` in the Cluster CR.

## Feature gates list

| Feature | Default | Stage | Since | Until | Restart |
|:---|:---|:---|:---|:---|:---|
| FeatureModification            | false | Alpha | 2.0 | - |      |
| VolumeAttributesClass          | false | Alpha | 2.0 | - |      |
| DisablePDDefaultReadinessProbe | false | Alpha | 2.0 | - | PD   |
| UsePDReadyAPI                  | false | Alpha | 2.0 | - | PD   |
| SessionTokenSigning            | false | Alpha | 2.0 | - | TiDB |

## Stage

### Alpha

Alpha feature means:

- Disabled by default.
- Recommanded to enable only when create a new TiDB cluster.
- Might not support to enable/disable for an existing TiDB cluster.
- Not recommanded to enable in prod env if not well tested.

### Beta

Beta feature means:

- Normally the feature is well tested.
- Recommanded to enable for all new created TiDB clusters.
- Normally enable/disable the feature for an existing TiDB cluster has been supported.

### GA

GA feature means:

- Normally the feature has been tested in a long time.
- Enabled by default. And cannot be disabled.

## Description of features

### FeatureModification

Support to change `spec.featureGates` if enabled.

### VolumeAttributesClass

Support to change `VolumeAttributesClass` of PVCs. This feature should also be enabled in Kubernetes, see [VolumeAttributesClass](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/)

### DisablePDDefaultReadinessProbe

If enabled, default tcp readiness probe of PD will be removed.

### UsePDReadyAPI

If enabled, use `/ready` api as readiness probe of PD. See [tikv/pd#8749](https://github.com/tikv/pd/pull/8749)

### SessionTokenSigning

If enabled, `session-token-signing-cert` and `session-token-signing-key` will be configured. See [TiDB ConfigFile](https://docs.pingcap.com/tidb/stable/tidb-configuration-file/#session-token-signing-cert-new-in-v640)
