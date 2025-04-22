---
title: Overlay 功能
summary: 了解如何使用 TiDB Operator 的 Overlay 功能来自定义和覆盖 Kubernetes 原生资源的配置，包括 Pod、PersistentVolumeClaim 等资源的灵活配置调整。
---

# Overlay 功能

本文档介绍 TiDB Operator 的 Overlay 功能的使用场景、使用方法、使用限制和常见问题。 

Overlay 功能是 TiDB Operator 提供的一种配置机制，允许用户自定义和覆盖 Kubernetes 原生资源的配置。通过 Overlay，你可以在不修改 TiDB Operator 代码的情况下，灵活地调整 Pod、PersistentVolumeClaim (PVC) 等 Kubernetes 资源的配置，以满足特定的部署需求。

## 使用场景

Overlay 功能可以在以下场景中使用：

- 为容器添加自定义环境变量：例如配置日志级别、时区等
- 配置 Pod 的安全上下文（security context）：如设置特定的 Linux 权限
- 原地更新 Pod/PVC 的标签或注解（无需重启）：用于集成第三方工具
- 自定义资源限制：调整 CPU 和内存限制
- 添加 sidecar 容器：注入监控或日志收集容器

## 使用方法

在 Component Group (如 `PDGroup`、`TiDBGroup`、`TiKVGroup`、`TiFlashGroup`、`TiCDCGroup`) 等 Custom Resource (CR) 的 `spec.template.spec.overlay` 字段中定义配置。

例如，为 PD 的容器添加了一个自定义环境变量：

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

或者为 TiKV 的 PVC 添加一个自定义标签：

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

1. Overlay 功能会将你定义的配置与 TiDB Operator 生成的默认配置合并。如果存在冲突，会以 Overlay 中定义的配置为准。

2. 对于 map 类型的字段（例如 `nodeSelector`、`labels` 等），Overlay 会将你定义的值与已存在的值合并，而不是完全替换。

3. 使用 Overlay 功能时，请确保你了解所修改配置的影响，特别是涉及到安全上下文、资源限制等关键配置时。

4. 某些字段可能不支持通过 Overlay 进行修改，这取决于 TiDB Operator 的实现。

## 最佳实践

1. **逐步引入变更**：在生产环境中使用 Overlay 功能时，建议先在测试环境验证配置，然后再逐步应用到生产环境。

2. **保持配置简洁**：只覆盖必要的配置，避免不必要的复杂性。

3. **记录配置变更**：保持对使用 Overlay 功能所做变更的记录，以便于故障排查和配置审计。

4. **使用版本控制**：将 Overlay 配置纳入版本控制系统，以跟踪配置的变更历史。
