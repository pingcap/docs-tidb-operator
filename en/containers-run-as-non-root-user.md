---
title: Run TiDB Operator and TiDB Clusters as a Non-root User
summary: Make TiDB Operator and TiDB clusters run as a non-root user
aliases: ['/docs/tidb-in-kubernetes/dev/containers-run-as-non-root-user/']
---

# Run TiDB Operator and TiDB Clusters as a Non-root User

In some Kubernetes environments, containers cannot be run as the root user. In this case, you can configure pods using [`SecurityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-pod) to run as a non-root user.

## Configure TiDB Operator containers

You can configure security context in the helm `values.yaml` file. All TiDB Operator components (at `<controllerManager/scheduler/advancedStatefulset/admissionWebhook>.securityContext`) support this configuration.

The following is an example configuration:

```yaml
controllerManager:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

## Configure containers controlled by CR

You can also enable security context in all CRs (TidbCluster/DMCluster/TiInitializer/TiMonitor/Backup/BackupSchedule/Restore) to make containers run as a non-root user.

You can set `podSecurityContext` at a cluster level (`spec.podSecurityContext`) for all components or at a component level (such as `spec.tidb.podSecurityContext` for TidbCluster, `spec.master.podSecurityContext` for DMCluster) for a specific component.

The following is an example configuration at a cluster level:

```yaml
spec:
  podSecurityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

The following is an example configuration at a component level:

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

For a component, if both the cluster level and the component level are configured, only the configuration of the component level takes effect.
