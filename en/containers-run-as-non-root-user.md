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

For containers controlled by Custom Resources (CRs), you can configure the security context at the Pod or container level. The supported fields vary by CR.

### Configure the Pod-level security context

`podSecurityContext` applies to all containers in the generated Pod and controls Pod-level settings such as volume ownership.

For `TidbCluster` and `DMCluster`, you can configure `podSecurityContext` at the following levels:

- Cluster level: configure `spec.podSecurityContext` to apply the settings to all components:

    ```yaml
    spec:
      podSecurityContext:
        runAsUser: 1000
        runAsGroup: 2000
        fsGroup: 2000
    ```

- Component level: configure `spec.<component>.podSecurityContext` to apply the settings to a specific component. For example, use `spec.tidb.podSecurityContext` for the TiDB component of a `TidbCluster`, or `spec.master.podSecurityContext` for the master component of a `DMCluster`:

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

If both levels are configured, the component-level `podSecurityContext` replaces the cluster-level `podSecurityContext` for that component.

Other CRs, including `TidbInitializer`, `TidbMonitor`, `Backup`, `BackupSchedule`, and `Restore`, also support Pod-level security context settings. For the supported fields and paths, refer to the [API documentation](<https://github.com/pingcap/tidb-operator/blob/{{{ .tidb_operator_version }}}/docs/api-references/docs.md>).

### Configure the container-level security context

Starting from TiDB Operator v1.6.6, the following CRs support [container-level security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-container):

- For `TidbCluster` and `DMCluster`, configure `spec.<component>.securityContext`, such as `spec.pd.securityContext`, `spec.tidb.securityContext`, `spec.master.securityContext`, or `spec.worker.securityContext`. These CRs do not support cluster-level `spec.securityContext`.
- For `TidbDashboard` and `TidbNGMonitoring`, configure `spec.securityContext`.
- For `TidbMonitor`, configure `securityContext` for each generated container. The supported paths include `spec.initializer.securityContext`, `spec.prometheus.securityContext`, `spec.grafana.securityContext`, `spec.reloader.securityContext`, `spec.prometheusReloader.securityContext`, `spec.thanos.securityContext`, and `spec.dm.initializer.securityContext`.

`TidbInitializer`, `Backup`, `BackupSchedule`, and `Restore` do not support container-level `securityContext`.

For the complete `ComponentSpec.securityContext` schema, refer to the [`ComponentSpec` API documentation](<https://github.com/pingcap/tidb-operator/blob/{{{ .tidb_operator_version }}}/docs/api-references/docs.md#componentspec>).

For example, the following configuration runs the PD container as a non-root user, sets the group ownership of its volumes, and prevents container processes from gaining more privileges than their parent processes:

```yaml
spec:
  pd:
    podSecurityContext:
      fsGroup: 2000
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      runAsGroup: 2000
      allowPrivilegeEscalation: false
```

> **Note:**
>
> - Container-level settings apply only to the corresponding container and override overlapping fields in the effective `podSecurityContext`.
> - Fields that affect Pod volumes, such as `fsGroup`, can only be configured in `podSecurityContext`.
> - Updating `securityContext` for a deployed component changes its Pod template and triggers a rolling update of the affected Pods.
> - To configure the TiDB slow-log tailer, TiKV log tailer, TiFlash log tailer, or TiFlash initializer separately, use `spec.tidb.slowLogTailer.securityContext`, `spec.tikv.logTailer.securityContext`, `spec.tiflash.logTailer.securityContext`, or `spec.tiflash.initializer.securityContext`.

> **Warning:**
>
> `spec.tikv.privileged` and `spec.tiflash.privileged` are deprecated. When you configure any field in the corresponding component's `securityContext`, TiDB Operator ignores the legacy `privileged` field. If the container still needs privileged mode, explicitly configure `securityContext.privileged: true`; otherwise, the component might fail to start.
