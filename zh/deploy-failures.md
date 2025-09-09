---
title: Kubernetes 上的 TiDB 常见部署错误
summary: 介绍 Kubernetes 上 TiDB 部署的常见错误以及处理办法。
---

# Kubernetes 上的 TiDB 常见部署错误

本文介绍了 Kubernetes 上 TiDB 常见部署错误以及处理办法。

## Pod 未正常创建

创建备份恢复任务后，如果 Pod 没有创建，则可以通过以下方式进行诊断：

```shell
kubectl get backups -n ${namespace}
kubectl get jobs -n ${namespace}
kubectl describe backups -n ${namespace} ${backup_name}
kubectl describe jobs -n ${namespace} ${backupjob_name}
kubectl describe restores -n ${namespace} ${restore_name}
```

## Pod 处于 Pending 状态

Pod 处于 Pending 状态，通常都是资源不满足导致的，比如：

* 使用持久化存储的 PD、TiKV、TiFlash、Backup、Restore Pod 使用的 PVC 的 StorageClass 不存在或 PV 不足
* Kubernetes 集群中没有节点能满足 Pod 申请的 CPU 或内存
* TiDB、TiProxy 等组件使用的证书没有配置

此时，可以通过 `kubectl describe pod` 命令查看 Pending 的具体原因：

```shell
kubectl describe po -n ${namespace} ${pod_name}
```

### CPU 或内存资源不足

如果是 CPU 或内存资源不足，可以通过降低对应组件的 CPU 或内存资源申请，使其能够得到调度，或是增加新的 Kubernetes 节点。

### PVC 的 StorageClass 不存在

如果是 PVC 的 StorageClass 找不到，可采取以下步骤：

1. 通过以下命令获取集群中可用的 StorageClass：

    ```shell
    kubectl get storageclass
    ```

2. 将 `storageClassName` 修改为集群中可用的 StorageClass 名字。

3. 使用下述方式更新配置文件：

    如果是运行 backup/restore 的备份/恢复任务，首先需要运行 `kubectl delete bk ${backup_name} -n ${namespace}` 删掉老的备份/恢复任务，再运行 `kubectl apply -f backup.yaml` 重新创建新的备份/恢复任务。

4. 删除对应的 PVC：

    ```shell
    kubectl delete pvc -n ${namespace} ${pvc_name}
    ```

### 可用 PV 不足

如果集群中有 StorageClass，但可用的 PV 不足，则需要添加对应的 PV 资源。

## Pod 处于 CrashLoopBackOff 状态

Pod 处于 CrashLoopBackOff 状态意味着 Pod 内的容器重复地异常退出（异常退出后，容器被 Kubelet 重启，重启后又异常退出，如此往复）。定位方法有很多种。

### 查看 Pod 内当前容器的日志

```shell
kubectl -n ${namespace} logs -f ${pod_name}
```

### 查看 Pod 内容器上次启动时的日志信息

```shell
kubectl -n ${namespace} logs -p ${pod_name}
```

确认日志中的错误信息后，可以根据 [tidb-server 启动报错](https://docs.pingcap.com/zh/tidb/stable/troubleshoot-tidb-cluster/#tidb-server-启动报错 )、[tikv-server 启动报错](https://docs.pingcap.com/zh/tidb/stable/troubleshoot-tidb-cluster/#tikv-server-启动报错)、[pd-server 启动报错](https://docs.pingcap.com/zh/tidb/stable/troubleshoot-tidb-cluster/#pd-server-启动报错)中的指引信息进行进一步排查解决。

### ulimit 不足

另外，TiKV 在 ulimit 不足时也会发生启动失败的状况，对于这种情况，可以修改 Kubernetes 节点的 `/etc/security/limits.conf` 调大 ulimit：

```
root        soft        nofile        1000000
root        hard        nofile        1000000
root        soft        core          unlimited
root        soft        stack         10240
```
