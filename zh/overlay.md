---
title: 自定义 Kubernetes 原生资源的配置
summary: 介绍如何使用 TiDB Operator 的 Overlay 功能自定义 Kubernetes 原生资源的配置，例如调整 Pod、PersistentVolumeClaim 等资源，以满足不同的部署需求。
---

# 自定义 Kubernetes 原生资源的配置

本文介绍如何使用 TiDB Operator 的 Overlay 功能来自定义 Kubernetes 原生资源的配置。Overlay 功能是 TiDB Operator 提供的一种配置机制，允许用户在不修改 TiDB Operator 源代码的前提下，自定义 Kubernetes 集群中原生资源的配置。通过 Overlay 功能，你可以灵活地调整 Pod 和 PersistentVolumeClaim (PVC) 等 Kubernetes 资源的配置，以满足特定的部署需求。

目前，TiDB Operator 的 Overlay 功能支持以下资源类型：

- **Pod**：修改 Pod 的元数据和规格
- **PersistentVolumeClaim**：修改 PVC 的元数据和规格

## 使用方法

### Pod Overlay

Pod Overlay 允许用户修改 Pod 的元数据（如标签、注释）和规格。你可以在 Component Group（例如 `PDGroup`、`TiDBGroup`、`TiKVGroup`、`TiFlashGroup`、`TiProxyGroup`、`TiCDCGroup` 等）Custom Resource (CR) 的 `spec.template.spec.overlay.pod` 字段中定义所需的配置。

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

### PVC Overlay

PVC Overlay 允许用户修改 PVC 的元数据（如标签、注释）和规格。你可以在 Component Group（例如 `PDGroup`、`TiDBGroup`、`TiKVGroup`、`TiFlashGroup`、`TiProxyGroup`、`TiCDCGroup` 等）Custom Resource (CR) 的 `spec.template.spec.overlay.volumeClaims` 字段中定义所需的配置。

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

### 注意事项

- Overlay 功能会将你在 `spec.template.spec.overlay` 字段中定义的配置与 TiDB Operator 自动生成的默认配置进行合并。如果存在冲突，以 Overlay 中定义的配置为准。
- 对于 `nodeSelector`、`labels` 等 map 类型的字段，Overlay 功能会将你定义的值添加到已有的值中，而不是完全替换。
- 在使用 Overlay 功能修改配置前，请务必充分了解这些修改可能带来的影响，特别是涉及安全上下文 (`securityContext`) 和资源限制等关键配置时。
- 支持通过 Overlay 进行修改的字段取决于 TiDB Operator 依赖的 Kubernetes API 版本。

## 示例场景

### 配置 Pod 的资源限制和亲和性

```yaml
spec:
  template:
    spec:
      overlay:
        pod:
          spec:
            containers:
              - name: tidb
                resources:
                  limits:
                    cpu: "4"
                    memory: "8Gi"
                  requests:
                    cpu: "2"
                    memory: "4Gi"
            affinity:
              nodeAffinity:
                requiredDuringSchedulingIgnoredDuringExecution:
                  nodeSelectorTerms:
                  - matchExpressions:
                    - key: dedicated
                      operator: In
                      values:
                      - tidb
```

### 配置 Pod 的安全上下文

```yaml
spec:
  template:
    spec:
      overlay:
        pod:
          spec:
            securityContext:
              sysctls:
              - name: net.core.somaxconn
                value: "1024"
```

### 原地更新 Pod 和 PVC 的标签或注解

通过 Overlay 可以原地更新 Pod 和 PVC 的标签或注解，而无需重启 Pod：

```yaml
overlay:
  pod:
    spec:
      overlay:
        pod:
          metadata:
            labels:
              custom-label: "value"
            annotations:
              custom-annotation: "value"
        volumeClaims:
          - name: data
            volumeClaim:
              metadata:
                labels:
                  custom-label: "value"
                annotations:
                  custom-annotation: "value"
```

### 注入 sidecar 容器

可以通过 Overlay 向 Pod 中添加 [sidecar 容器](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/sidecar-containers/)，例如用于监控或日志收集：

```yaml
spec:
  template:
    spec:
      overlay:
        pod:
          spec:
            initContainers:
              - name: logshipper
                image: alpine:latest
                restartPolicy: Always
                command: ['sh', '-c', 'tail -F /opt/logs.txt']
```