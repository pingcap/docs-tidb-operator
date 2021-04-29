---
title: 以非 root 用户运行容器
summary: 以非 root 用户运行所有 tidb-operator 相关的容器
aliases: ['/docs/tidb-in-kubernetes/dev/containers-run-as-non-root-user/']
---

# 以非 root 用户运行容器

在某些 Kubernetes 环境中，无法用 root 用户运行容器。我们可以通过配置 [`SecurityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-pod) 来以非 root 用户启动容器。

## 配置 operator 相关的容器

安全上下文 (Security context) 可以在 helm 的 `values.yaml` 文件中配置。所有 operator 的相关组件都支持该配置 (`<controllerManager/scheduler/advancedStatefulset/admissionWebhook>.securityContext`)。

比如如下配置:

```yaml
controllerManager:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

## 配置按照 CR 生成的容器

安全上下文 (Security context) 同样可以在任意一种 CR 中开启。

该字段可以配置在集群级别 (`spec.podSecurityContext`) 对所有组件生效或者配置在组件级别 (e.g. `spec.tidb.podSecurityContext` in TidbCluster, `spec.master.podSecurityContext` in DMCluster) 仅对该组件生效。

比如集群级别的配置如下:

```yaml
spec:
  podSecurityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

组件级别的例子如下:

```yaml
spec:
  pd:
    podSecurityContext:
      runAsUser: 1000
      runAsGroup: 2000
      fsGroup: 2000
  tidb:
    podSecurityContext:
      runAsUser: 1000
      runAsGroup: 2000
      fsGroup: 2000
```

如果同时配置了集群级别和组件级别，则该组件以组件级别的配置为准。
