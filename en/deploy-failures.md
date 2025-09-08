---
title: Common Deployment Failures of TiDB on Kubernetes
summary: Learn the common deployment failures of TiDB on Kubernetes and their solutions.
---

# Common Deployment Failures of TiDB on Kubernetes

This document describes the common deployment failures of TiDB on Kubernetes and their solutions.

## The Pod is not created normally

After creating a backup/restore task, if the Pod is not created, you can perform a diagnostic operation by executing the following commands:

```shell
kubectl get backups -n ${namespace}
kubectl get jobs -n ${namespace}
kubectl describe backups -n ${namespace} ${backup_name}
kubectl describe jobs -n ${namespace} ${backupjob_name}
kubectl describe restores -n ${namespace} ${restore_name}
```

## The Pod is in the Pending state

The Pending state of a Pod is usually caused by conditions of insufficient resources, for example:

- The `StorageClass` of the PVC used by PD, TiKV, TiFlash, Backup, and Restore Pods does not exist or the PV is insufficient.
- No nodes in the Kubernetes cluster can satisfy the CPU or memory resources requested by the Pod.
- The certificates used by TiDB or TiProxy components are not configured.

You can check the specific reason for Pending by using the `kubectl describe pod` command:

```shell
kubectl describe po -n ${namespace} ${pod_name}
```

### CPU or memory resources are insufficient

If the CPU or memory resources are insufficient, you can lower the CPU or memory resources requested by the corresponding component for scheduling, or add a new Kubernetes node.

### StorageClass of the PVC does not exist

If the `StorageClass` of the PVC cannot be found, take the following steps:

1. Get the available `StorageClass` in the cluster:

    ```shell
    kubectl get storageclass
    ```

2. Change `storageClassName` to the name of the `StorageClass` available in the cluster.

3. Update the configuration file:

    If you want to run a backup/restore task, first execute `kubectl delete bk ${backup_name} -n ${namespace}` to delete the old backup/restore task, and then execute `kubectl apply -f backup.yaml` to create a new backup/restore task.

4. Delete the corresponding PVCs:

    ```shell
    kubectl delete pvc -n ${namespace} ${pvc_name}
    ```

### Insufficient available PVs

If a `StorageClass` exists in the cluster but the available PVs are insufficient, you need to add PV resources correspondingly.

## The Pod is in the `CrashLoopBackOff` state

A Pod in the `CrashLoopBackOff` state means that the container in the Pod repeatedly aborts (in the loop of abort - restart by `kubelet` - abort). There are many potential causes of `CrashLoopBackOff`.

### View the log of the current container

```shell
kubectl -n ${namespace} logs -f ${pod_name}
```

### View the log when the container was last restarted

```shell
kubectl -n ${namespace} logs -p ${pod_name}
```

After checking the error messages in the log, you can refer to [Cannot start `tidb-server`](https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-cluster#cannot-start-tidb-server), [Cannot start `tikv-server`](https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-cluster#cannot-start-tikv-server), and [Cannot start `pd-server`](https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-cluster#cannot-start-pd-server) for further troubleshooting.

### `ulimit` is not large enough

TiKV might fail to start when `ulimit` is not large enough. In this case, you can modify the `/etc/security/limits.conf` file of the Kubernetes node to increase the `ulimit`:

```
root soft nofile 1000000
root hard nofile 1000000
root soft core unlimited
root soft stack 10240
```
