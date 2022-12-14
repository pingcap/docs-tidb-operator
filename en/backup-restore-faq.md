---
title: FAQs on EBS Snapshot Backup and Restore
summary: Learn about the common questions and solutions for EBS snapshot backup and restore.
---

# FAQs on EBS Snapshot Backup and Restore

This document describes the common questions occur during ESB snapshot backup and restore and the solutions.

## Backup issues

You might encounter the following problems during EBS snapshot backup:

- [Failed to start a backup or the backup failed immediately after it started](#failed-to-start-a-backup-or-the-backup-failed-immediately-after-it-started)
- [The backup CR of a failed task could not be deleted](#the-backup-cr-of-a-failed-task-could-not-be-deleted)
- [Backup failed immediately after being initiated](#backup-failed-immediately-after-being-initiated)

### Failed to start a backup or the backup failed immediately after it started

Issue: [#4781](https://github.com/pingcap/tidb-operator/issues/4781)

- Symptom 1: Apply the backup CRD yaml file. The pod and job are not created, and the backup cannot be started.

    * Run the following command to check the pod of TiDB Operator:

        ```shell
        kubectl get po -n ${namespace}
        ```

    * Run the following command to check the log of `tidb-controller-manager`:

        ```shell
        kubectl -n ${namespace} logs ${tidb-controller-manager}
        ```

    * Check whether the log contains the following error message:

        ```shell
        metadata.annotations: Too long: must have at most 262144 bytes, spec.template.annotations: Too long: must have  at most 262144 bytes
        ```

    Cause: TiDB uses annotations to pass in the PVC or PV configuration and the annotation of a backup job should not exceed 256 KB. When a TiKV cluster is excessively large, the configuration of PVC or PV will be larger than 256 KB. As a result, calling Kubernetes API fails.

- Symptom 2: Apply the backup CRD yaml file. The pod and job are successfully created, but the backup failed immediately.

    Check the log of the backup job as described in symptom 1. The error message is as follows:

    ```shell
    exec /entrypoint.sh: argument list too long
    ```

    Cause: In TiDB Operator, before the backup pod starts, the PVC or PV configuration is injected to the environment variables of the backup pod. Then the backup task starts. The environment variables cannot exceed 1 MB. When the configuration of PVC or PV is larger than 1 MB, the backup pod cannot get the environment variables and the backup fails.

    Scenario: This issue occurs when the TiKV cluster is excessively large (40+ TiKV nodes) or too many volumes have been configured, and the TiDB Operator is v1.4.0-beta.2 or earlier.

Solution: Upgrade TiDB Operator to the latest version.

### The backup CR of a failed task could not be deleted

Issue: [#4778](https://github.com/pingcap/tidb-operator/issues/4778)

Symptom: Deleting the backup CP is stuck.

Scenario: This issue occurs when the TiDB Operator is v1.4.0-beta.2 or earlier.

Solution: Upgrade TiDB Operator to the latest version.

### Backup failed immediately after being initiated

Issue: [#13838](https://github.com/tikv/tikv/issues/13838)

Symptom: Apply the backup CRD yaml file. The pod and job are successfully created, but the backup failed immediately.

Check whether the log contains the following error:

```shell
GC safepoint 437271276493996032 exceed TS 437270540511608835
```

Scenario: This issue occurs when you initiate backup tasks using volumes in a large cluster (20+ TiKV nodes), after you perform large-scale data restore using BR.

Solution: Start the `grafana ${cluster-name}-TiKV-Details` panel. Check the Resolved-TS and confirm whether there is a large `Max Resolved TS gap`. Then restart the corresponding TiKV.

## Restore issues

You might encounter the following problems during EBS snapshot restore:

- [Failed to restore the cluster with the error `keepalive watchdog timeout`](#failed-to-restore-the-cluster-with-the-error-keepalive-watchdog-timeout)
- [Restore period is excessively long (longer than 2 hours)](#restore-period-is-excessively-long-longer-than-2-hours)

### Failed to restore the cluster with the error `keepalive watchdog timeout`

Symptom: The subtasks of BR data restore failed. The first restore subtask succeeded (volume complete) but the second subtask failed. Check the log of the failed task and find the following log information:

```shell
error="rpc error: code = Unavailable desc = keepalive watchdog timeout"
```

Scenario: This issue occurs when the data volume is large and the TiDB cluster version is v6.3.0.

Solution:

1. Upgrade the TiDB cluster to v6.4.0 or later.

2. Edit the configuration file of the TiDB cluster and increase the value of TiKV's `keepalive`:

    ```shell
    config: |
      [server]
        grpc-keepalive-time = "500s"
        grpc-keepalive-timeout = "10s"
    ```

## Restore period is excessively long (longer than 2 hours)

Scenario: This issue occurs when the TiDB cluster version is v6.3.0 or v6.4.0.

Solution:

1. Upgrade the TiDB cluster to v6.5.0.

2. In BR spec, temporarily increase the volume performance for restore, and then manually degrade the performance after the restore is completed. Specifically, you can specify parameters to get higher volume configuration, such as specifying `--volume-iops=8000`, `--volume-throughput=600`, or other configurations.

    ```yaml
    spec:
      backupType: full
      restoreMode: volume-snapshot
      serviceAccount: tidb-backup-manager
      toolImage: pingcap/br:v6.5.0
      br:
        cluster: basic
        clusterNamespace: tidb-cluster
        sendCredToTikv: false
    options:
    - --volume-type=gp3
    - --volume-iops=8000
    - --volume-throughput=600
    ```