---
title: TiDB Operator RBAC 规则
summary: 介绍 TiDB Operator 需要的 RBAC 规则。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/tidb-operator-rbac/']
---

# TiDB Operator 需要的 RBAC 规则

Kubernetes [基于角色的访问控制 (RBAC)](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) 规则是通过 Role 或者 ClusterRole 来进行管理的，使用 RoleBinding 可以将 Role 的权限赋予给一个用户，使用 ClusterRoleBinding 可以将 ClusterRole 的权限赋予给一组用户。

## Cluster 级别管理 TiDB 集群

默认配置 (`clusterScoped=true`) 下，TiDB Operator 能管理 Kubernetes 集群内所有 TiDB 集群。要查看为 TiDB Operator 创建的 ClusterRole，请使用以下命令：

{{< copyable "shell-regular" >}}

```shell
kubectl get clusterrole | grep tidb
```

输出结果如下：
```shell
tidb-operator:tidb-controller-manager                                  2021-05-04T13:08:55Z
tidb-operator:tidb-scheduler                                           2021-05-04T13:08:55Z
```

`tidb-operator:tidb-controller-manager` 是为 `tidb-controller-manager` Pod 创建的 ClusterRole，其对应的权限包括：

| 资源                                          | 非资源 URLs        | 资源名          | 动作                                             | 解释 |
| ---------                                     | ----------------- | -------------- | -----                                            | ------- |
| events                                        | -                 | -              | [*]                                              | 输出 Event 信息 |
| services                                      | -                 | -              | [*]                                              | 操作 Service 资源 |
| statefulsets.apps.pingcap.com/status          | -                 | -              | [*]                                              | AdvancedStatefulSet=true 时，需要操作此资源，详细信息可以参考[增强型 StatefulSet 控制器](advanced-statefulset.md) |
| statefulsets.apps.pingcap.com                 | -                 | -              | [*]                                              | AdvancedStatefulSet=true 时，需要操作此资源，详细信息可以参考[增强型 StatefulSet 控制器](advanced-statefulset.md) |
| controllerrevisions.apps                      | -                 | -              | [*]                                              | Kubernetes StatefulSet/Daemonset 版本控制 |
| deployments.apps                              | -                 | -              | [*]                                              | 操作 Deployment 资源 |
| statefulsets.apps                             | -                 | -              | [*]                                              | 操作 Statefulset 资源 |
| ingresses.extensions                          | -                 | -              | [*]                                              | 操作监控系统 Ingress 资源 |
| *.pingcap.com                                 | -                 | -              | [*]                                              | 操作 pingcap.com 下所有自定义资源 |
| configmaps                                    | -                 | -              | [create get list watch update delete]            | 操作 ConfigMap 资源 |
| endpoints                                     | -                 | -              | [create get list watch update delete]            | 操作 Endpoints 资源 |
| serviceaccounts                               | -                 | -              | [create get update delete]                       | 为 TidbMonitor/Discovery 服务创建 ServiceAccount |
| clusterrolebindings.rbac.authorization.k8s.io | -                 | -              | [create get update delete]                       | 为 TidbMonitor 服务创建 ClusterRoleBinding |
| rolebindings.rbac.authorization.k8s.io        | -                 | -              | [create get update delete]                       | 为 TidbMonitor/Discovery 服务创建 RoleBinding |
| secrets                                       | -                 | -              | [create update get list watch delete]            | 操作 Secret 资源 |
| clusterroles.rbac.authorization.k8s.io        | -                 | -              | [escalate create get update delete]              | 为 TidbMonitor 服务创建 ClusterRole |
| roles.rbac.authorization.k8s.io               | -                 | -              | [escalate create get update delete]              | 为 TidbMonitor/Discovery 服务创建 Role |
| persistentvolumeclaims                        | -                 | -              | [get list watch create update delete patch]      | 操作 PVC 资源 |
| jobs.batch                                    | -                 | -              | [get list watch create update delete]            | TiDB 集群初始化、备份、恢复操作使用 Job 进行 |
| persistentvolumes                             | -                 | -              | [get list watch patch update]                    | 为 PV 添加集群信息相关 Label、修改 `persistentVolumeReclaimPolicy` 等操作 |
| pods                                          | -                 | -              | [get list watch update delete]                   | 操作 Pod 资源 |
| nodes                                         | -                 | -              | [get list watch]                                 | 读取 Node Label 并根据 Label 信息为 TiKV、TiFlash 设置 Store Label |
| storageclasses.storage.k8s.io                 | -                 | -              | [get list watch]                                 | 扩展 PVC 存储之前确认 StorageClass 是否支持 `VolumeExpansion` |
| -                                             |[/metrics]         | -              | [get]                                            | 读取监控指标 |

`tidb-operator:tidb-scheduler` 是为 `tidb-scheduler` Pod 创建的 ClusterRole，其对应的权限包括：

| 资源                       | 非资源 URLs        | 资源名            | 动作                            | 解释 |
| ---------                  | ----------------- | --------------   | -----                           | ------- |
| leases.coordination.k8s.io | -                 | -                | [create]                        | leader 选举需要创建 Lease 资源锁 |
| endpoints                  | -                 | -                | [delete get patch update]       | 操作 Endpoints 资源 |
| persistentvolumeclaims     | -                 | -                | [get list update]               | 读取 PD/TiKV PVC 信息，更新调度信息到 PVC Label |
| configmaps                 | -                 | -                | [get list watch]                | 读取 ConfigMap 资源 |
| pods                       | -                 | -                | [get list watch]                | 读取 Pod 信息 |
| nodes                      | -                 | -                | [get list]                      | 读取 Node 信息 |
| leases.coordination.k8s.io | -                 | [tidb-scheduler] | [get update]                    | leader 选举需要读取/更新 Lease 资源锁 |
| tidbclusters.pingcap.com   | -                 | -                | [get]                           | 读取 Tidbcluster 信息 |

## Namespace 级别管理 TiDB 集群

如果部署时设置 `clusterScoped=false`，表示在 Namespace 级别管理 TiDB 集群，使用如下命令查看创建的 ClusterRole/Role：

{{< copyable "shell-regular" >}}

```shell
kubectl get clusterrole | grep tidb
```

```shell
tidb-operator:tidb-controller-manager                                  2021-05-04T13:08:55Z
```

{{< copyable "shell-regular" >}}

```shell
kubectl get role -n tidb-admin
```

```shell
tidb-admin    tidb-operator:tidb-controller-manager            2021-05-07T06:14:52Z
tidb-admin    tidb-operator:tidb-scheduler                     2021-05-07T06:14:52Z
```

`tidb-operator:tidb-controller-manager` ClusterRole 是为 `tidb-controller-manager` Pod 创建的 ClusterRole，其对应的权限包括：

| 资源                          | 非资源 URLs        | 资源名          | 动作                             | 解释 |
| ---------                     | ----------------- | -------------- | -----                            | ------- |
| persistentvolumes             | -                 | -              | [get list watch patch update]    | 为 PV 添加集群信息相关 Label、修改 `persistentVolumeReclaimPolicy` 等操作 |
| nodes                         | -                 | -              | [get list watch]                 | 读取 Node Label 并根据 Label 信息为 TiKV、TiFlash 设置 Store Label |
| storageclasses.storage.k8s.io | -                 | -              | [get list watch]                 | 扩展 PVC 存储之前确认 StorageClass 是否支持 `VolumeExpansion` |

`tidb-operator:tidb-controller-manager` Role 是为 `tidb-controller-manager` Pod 创建的 Role，其对应的权限包括：

| 资源                                          | 非资源 URLs        | 资源名          | 动作                                             | 解释 |
| ---------                                     | ----------------- | -------------- | -----                                            | ------- |
| events                                        | -                 | -              | [*]                                              | 输出 Event 信息 |
| services                                      | -                 | -              | [*]                                              | 操作 Service 资源 |
| statefulsets.apps.pingcap.com/status          | -                 | -              | [*]                                              | AdvancedStatefulSet=true 时，需要操作此资源，详细信息可以参考[增强型 StatefulSet 控制器](advanced-statefulset.md) |
| statefulsets.apps.pingcap.com                 | -                 | -              | [*]                                              | AdvancedStatefulSet=true 时，需要操作此资源，详细信息可以参考[增强型 StatefulSet 控制器](advanced-statefulset.md) |
| controllerrevisions.apps                      | -                 | -              | [*]                                              | Kubernetes StatefulSet/Daemonset 版本控制 |
| deployments.apps                              | -                 | -              | [*]                                              | 操作 Deployment 资源 |
| statefulsets.apps                             | -                 | -              | [*]                                              | 操作 Statefulset 资源 |
| ingresses.extensions                          | -                 | -              | [*]                                              | 操作监控系统 Ingress 资源 |
| *.pingcap.com                                 | -                 | -              | [*]                                              | 操作 pingcap.com 下所有自定义资源 |
| configmaps                                    | -                 | -              | [create get list watch update delete]            | 操作 ConfigMap 资源 |
| endpoints                                     | -                 | -              | [create get list watch update delete]            | 操作 Endpoints 资源 |
| serviceaccounts                               | -                 | -              | [create get update delete]                       | 为 TidbMonitor/Discovery 服务创建 ServiceAccount |
| rolebindings.rbac.authorization.k8s.io        | -                 | -              | [create get update delete]                       | 为 TidbMonitor/Discovery 服务创建 RoleBinding |
| secrets                                       | -                 | -              | [create update get list watch delete]            | 操作 Secret 资源 |
| roles.rbac.authorization.k8s.io               | -                 | -              | [escalate create get update delete]              | 为 TidbMonitor/Discovery 服务创建 Role |
| persistentvolumeclaims                        | -                 | -              | [get list watch create update delete patch]      | 操作 PVC 资源 |
| jobs.batch                                    | -                 | -              | [get list watch create update delete]            | TiDB 集群初始化、备份、恢复操作使用 Job 进行 |
| pods                                          | -                 | -              | [get list watch update delete]                   | 操作 Pod 资源 |

`tidb-operator:tidb-scheduler` Role 是为 `tidb-controller-manager` Pod 创建的 Role，其对应的权限包括：

| 资源                       | 非资源 URLs        | 资源名            | 动作                            | 解释 |
| ---------                  | ----------------- | --------------   | -----                           | ------- |
| leases.coordination.k8s.io | -                 | -                | [create]                        | leader 选举需要创建 Lease 资源锁 |
| endpoints                  | -                 | -                | [delete get patch update]       | 操作 Endpoints 资源 |
| persistentvolumeclaims     | -                 | -                | [get list update]               | 读取 PD/TiKV PVC 信息，更新调度信息到 PVC Label |
| configmaps                 | -                 | -                | [get list watch]                | 读取 Configmap 资源 |
| pods                       | -                 | -                | [get list watch]                | 读取 Pod 信息 |
| nodes                      | -                 | -                | [get list]                      | 读取 Node 信息 |
| leases.coordination.k8s.io | -                 | [tidb-scheduler] | [get update]                    | leader 选举需要读取/更新 Lease 资源锁 |
| tidbclusters.pingcap.com   | -                 | -                | [get]                           | 读取 Tidbcluster 信息 |

> **注意：**
>
> * `-` 表示为空。
> * 动作列中的 `*` 表示 Kubernetes 集群要求的所有动作。
