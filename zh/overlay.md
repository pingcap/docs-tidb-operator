---
title: 使用 Overlay 来自定义 Kubernetes 原生资源的配置
summary: 介绍如何使用 TiDB Operator 的 Overlay 功能自定义 Kubernetes 原生资源的配置，例如调整 Pod、PersistentVolumeClaim 等资源，以满足不同的部署需求。
---

# 使用 Overlay 来自定义 Kubernetes 原生资源的配置

本文介绍 TiDB Operator 的 Overlay 功能，包括其适用场景、使用方法、注意事项和最佳实践。

Overlay 功能是 TiDB Operator 提供的一种配置机制，允许用户在不修改 TiDB Operator 源代码的前提下，自定义 Kubernetes 集群中原生资源的配置。通过 Overlay 功能，你可以灵活地调整 Pod 和 PersistentVolumeClaim (PVC) 等 Kubernetes 资源的配置，以满足特定的部署需求。

## 适用场景

Overlay 功能适用于以下场景：

- 自定义容器环境变量：例如配置容器的日志级别或时区设置
- 配置 Pod 的安全上下文 (`securityContext`)：例如设置特定的 Linux 权限
- 原地更新 Pod 或 PVC 的标签或注解（无需重启）：用于集成第三方工具
- 自定义资源限制：根据实际需求调整容器的 CPU 和内存限制
- 注入 [sidecar 容器](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/sidecar-containers/)：向 Pod 中添加额外的辅助容器 (sidecar)，例如用于监控或日志收集

## 使用方法

你可以在 Component Group（例如 `PDGroup`、`TiDBGroup`、`TiKVGroup`、`TiFlashGroup`、`TiCDCGroup` 等）Custom Resource (CR) 的 `spec.template.spec.overlay` 字段中定义所需的配置。

以下示例展示如何为 PD 容器添加一个名为 `CUSTOM_ENV_VAR` 的环境变量：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: PDGroup
metadata:
  name: pd
spec:
  template:
    spec:
      overlay:
        pod:
          spec:
            containers:
              - name: pd
                env:
                  - name: "CUSTOM_ENV_VAR"
                    value: "custom_value"
```

以下示例展示如何为 TiKV 的 PVC 添加一个名为 `custom-label` 的自定义标签：

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiKVGroup
metadata:
  name: tikv
spec:
  template:
    spec:
      volumes:
      - name: data
        mounts:
          - type: data
        storage: 100Gi
      overlay:
        volumeClaims:
          - name: data
            volumeClaim:
              metadata:
                labels:
                  custom-label: "value"
```

## 注意事项

- Overlay 功能会将你在 `spec.template.spec.overlay` 字段中定义的配置与 TiDB Operator 自动生成的默认配置进行合并。如果存在冲突，以 Overlay 中定义的配置为准。

- 对于 `nodeSelector`、`labels` 等 map 类型的字段，Overlay 功能会将你定义的值添加到已有的值中，而不是完全替换。

- 在使用 Overlay 功能修改配置前，请务必充分了解这些修改可能带来的影响，特别是涉及安全上下文 (`securityContext`) 和资源限制等关键配置时。

- 支持通过 Overlay 进行修改的字段取决于 TiDB Operator 依赖的 Kubernetes API 版本。

## 最佳实践

- **逐步引入变更**：在生产环境中使用 Overlay 功能时，建议先在测试环境中进行充分的验证，确认配置的正确性和稳定性后再逐步应用到生产环境。

- **保持配置简洁**：只覆盖必要的配置，避免引入不必要的复杂性。

- **记录配置变更**：记录所有通过 Overlay 功能进行的配置变更，便于故障排查和配置审计。

- **使用版本控制**：将 Overlay 配置纳入版本控制系统，以跟踪配置的变更历史。
