---
title: Run Containers as a Non-root User
summary: Learn how to make TiDB Operator related containers run as a non-root user.
---

# Run Containers as a Non-root User

In some Kubernetes environments, containers cannot be run as the root user. In this case, you can set [`securityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-pod) to run containers as a non-root user.

## Configure TiDB Operator containers

For TiDB Operator containers, you can configure security context in the Helm `values.yaml` file. All TiDB Operator components (at `<controllerManager/scheduler/advancedStatefulset/admissionWebhook>.securityContext`) support this configuration.

The following is an example configuration:

```yaml
controllerManager:
  securityContext:
    runAsUser: 1000
    runAsGroup: 2000
    fsGroup: 2000
```

## Configure containers controlled by CR

For the containers controlled by CR, you can configure security context in any CRs (`TidbCluster`/`DMCluster`/`TiInitializer`/`TiMonitor`/`Backup`/`BackupSchedule`/`Restore`) to make the containers run as a non-root user.

You can use either of the following two types of configuration. If you configure both the cluster level and the component level for a component, only the configuration of the component level takes effect.

- Configure `podSecurityContext` at the cluster level (`spec.podSecurityContext`) for all components. The following is an example configuration:

    ```yaml
    spec:
      podSecurityContext:
        runAsUser: 1000
        runAsGroup: 2000
        fsGroup: 2000
    ```

- Configure at the component level for a specific component. For example, configuring  `spec.tidb.podSecurityContext` for `TidbCluster`, `spec.master.podSecurityContext` for `DMCluster`. The following is an example configuration:

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
