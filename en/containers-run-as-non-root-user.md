---
title: TiDB Operator and TiDB clusters run as non-root user
summary: Let TiDB Operator and TiDB clusters run as non root user
aliases: ['/docs/tidb-in-kubernetes/dev/containers-run-as-non-root-user/']
---

# TiDB Operator and TiDB clusters run as non-root user

In some Kubernetes environments, container can't run as root user. You can configure pods to use [`SecurityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-pod) to run as non-root user.

## Configure TiDB Operator containers

Security context can be set in helm `values.yaml`. All of operator components support this config (at `<controllerManager/scheduler/advancedStatefulset/admissionWebhook>.securityContext`).

For example:

```yaml
controllerManager:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

## Configure containers controlled by CR

Security context can also be enabled in all CRs (TidbCluster/DMCluster/TiInitializer/TiMonitor/Backup/BackupSchedule/Restore) to make containers run as non-user.

It can be set at cluster level (`spec.podSecurityContext`) for all of components or component level (e.g. `spec.tidb.podSecurityContext` in TidbCluster, `spec.master.podSecurityContext` in DMCluster) for specific component.

For example (at cluster level):

```yaml
spec:
  podSecurityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

Or (at compnent level):

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

If this field is set at both cluster level and component level, component level config will override the one at cluster level.
