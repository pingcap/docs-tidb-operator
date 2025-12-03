---
title: Feature Gates
summary: Learn how to use feature gates to enable or disable specific features in a TiDB cluster.
---

# Feature Gates

Feature gates are configuration switches that enable or disable specific features in TiDB Operator. These features are generally experimental, and enabling them might require restarting certain components for the changes to take effect.

You can configure feature gates in the `spec.featureGates` field of the Cluster Custom Resource (CR). The following example shows how to enable the `FeatureModification` feature gate:

```yaml
spec:
  featureGates:
    FeatureModification: true
```

## Supported feature gates

This section describes the feature gates supported by TiDB Operator. For definitions of feature stages, see [Feature gate stages](#feature-gate-stages).

### `FeatureModification`

- When this feature is enabled, you can modify the `spec.featureGates` configuration.
- Default value: `false`
- Stage: Alpha in v2.0 and later versions
- Components requiring restart: None

### `VolumeAttributesClass`

- When this feature is enabled, you can modify the `VolumeAttributesClass` attribute of a PVC. This feature depends on the corresponding Kubernetes capability. For more information, see the [Kubernetes documentation for VolumeAttributesClass](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/).
- Default value: `false`
- Stage: Alpha in v2.0 and later versions
- Components requiring restart: None

### `DisablePDDefaultReadinessProbe`

- When this feature is enabled, TiDB Operator no longer checks PD readiness using TCP probes.
- Default value: `false`
- Stage: Alpha in v2.0 and later versions
- Components requiring restart: PD

### `UsePDReadyAPI`

- When this feature is enabled, TiDB Operator checks PD readiness using the `/ready` API. For implementation details, see [`tikv/pd` #8749](https://github.com/tikv/pd/pull/8749).
- Default value: `false`
- Stage: Alpha in v2.0 and later versions
- Components requiring restart: PD

### `SessionTokenSigning`

- When this feature is enabled, TiDB Operator automatically configures the [`session-token-signing-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file/#session-token-signing-cert-new-in-v640) and [`session-token-signing-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file/#session-token-signing-key-new-in-v640) parameters for TiDB.
- Default value: `false`
- Stage: Alpha in v2.0 and later versions
- Components requiring restart: TiDB

## Feature gate stages

TiDB Operator classifies feature gates into three stages based on feature maturity: Alpha, Beta, and GA.

### Alpha

Alpha-stage features have the following characteristics:

- Disabled by default.
- Recommended only for newly created clusters.
- Dynamic enabling or disabling in existing clusters is not guaranteed.
- Known or unknown issues might occur after being enabled.
- **Not recommended for production environments** unless risks are fully evaluated and validated.

### Beta

Beta-stage features have the following characteristics:

- Typically have undergone thorough testing.
- Recommended to enable in all newly created clusters.
- Usually support enabling or disabling in existing clusters, but might require restarting related components.

### GA

GA (General Availability) features have the following characteristics:

- Typically have undergone long-term and large-scale testing.
- Enabled by default.
- Cannot be disabled using feature gates.
