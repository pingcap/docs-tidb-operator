---
title: 为使用云存储的 TiDB 集群更换节点
summary: 介绍如何为使用云存储的 TiDB 集群更换节点。
---

# 为使用云存储的 TiDB 集群更换节点

本文介绍一种在不停机情况下为使用云存储的 TiDB 集群更换、升级节点的方法。你可以为 TiDB 集群更换更高节点规格，也可以为节点升级新版本 Kubernetes。

本文以 `Amazon EKS` 为例，介绍了如何创建新的节点组，然后使用滚动重启迁移 TiDB 集群到新节点组，用于 TiKV 或者 TiDB 更换计算资源更多的节点组，EKS 升级等场景。

> **注意：**
>
> 其它公有云环境请参考 [Google Cloud GKE](deploy-on-gcp-gke.md)、[Azure AKS](deploy-on-azure-aks.md) 或[阿里云 ACK](deploy-on-alibaba-cloud.md) 操作节点组。

## 前置条件

- 云上已经存在一个 TiDB 集群。如果没有，可参考 [Amazon EKS](deploy-on-aws-eks.md) 进行部署。
- TiDB 集群使用云存储作为数据盘。

## 第一步：创建新的节点组

1. 找到 TiDB 集群所在的 EKS 集群的配置文件 `cluster.yaml`，将其拷贝保存为 `cluster-new.yaml`。

2. 在 `cluster-new.yaml` 中加入新节点组 `tidb-1b-new`、`tikv-1a-new`：

    ```yaml
    apiVersion: eksctl.io/v1alpha5
    kind: ClusterConfig
    metadata:
      name: your-eks-cluster
      region: ap-northeast-1

    nodeGroups:
    ...
      - name: tidb-1b-new
        desiredCapacity: 1
        privateNetworking: true
        availabilityZones: ["ap-northeast-1b"]
        instanceType: c5.4xlarge
        labels:
          dedicated: tidb
        taints:
          dedicated: tidb:NoSchedule
      - name: tikv-1a-new
        desiredCapacity: 1
        privateNetworking: true
        availabilityZones: ["ap-northeast-1a"]
        instanceType: r5b.4xlarge
        labels:
          dedicated: tikv
        taints:
          dedicated: tikv:NoSchedule
    ```

    > **注意：**
    >
    > * `availabilityZones` 需要和要替换的节点组保持一致。
    > * 本例仅以 `tidb-1b-new`、`tikv-1a-new` 节点组为例，请自行配置参数。

    如果要升级节点规格，修改 `instanceType`。如果要升级节点 Kubernetes 版本，请先升级 `Kubernetes Control Plane` 版本，可以参考[更新集群](https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html)

3. 从 `cluster-new.yaml` 中删除要更换的原节点组。

    本例中删除 `tidb-1b`、`tikv-1a` 节点组，请根据情况自行删除。

4. 从 `cluster.yaml` 中删除**无需更换**的节点组，保留要更换的原节点组，这些节点组将从集群中被删除。

   本例中留下 `tidb-1b`、`tikv-1a` 节点组，删除其他节点组。请根据情况自行调整。

5. 执行以下命令，创建新的节点组：

    {{< copyable "shell-regular" >}}

    ```bash
    eksctl create nodegroup -f cluster_new.yml
    ```

    > **注意：**
    >
    > 该命令只创建新的节点组，已经存在的节点组会忽略，不会重复创建，更不会删除不存在的节点组。

6. 执行下面命令，确认新节点已加入：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl get no -l alpha.eksctl.io/nodegroup-name=${new_nodegroup1}
    kubectl get no -l alpha.eksctl.io/nodegroup-name=${new_nodegroup2}
    ...
    ```

    其中 `${new_nodegroup}` 是新节点组名称，本例中是 `tidb-1b-new`、`tikv-1a-new`，请根据情况自行调整。

## 第二步：标记原节点组的节点为不可调度

使用 `kubectl cordon` 命令标记原节点组节点为不可调度，防止新的 Pod 调度上去：

{{< copyable "shell-regular" >}}

```bash
kubectl cordon -l alpha.eksctl.io/nodegroup-name=${origin_nodegroup1}
kubectl cordon -l alpha.eksctl.io/nodegroup-name=${origin_nodegroup2}
...
```

其中 `${origin_nodegroup}` 是原节点组名称，本例中是 `tidb-1b`、`tikv-1a`，请根据情况自行调整。

## 第三步：滚动重启 TiDB 集群

参考[重启 Kubernetes 上的 TiDB 集群](restart-a-tidb-cluster.md#优雅滚动重启-tidb-集群组件的所有-pod)滚动重启 TiDB 集群。

## 第四步：删除原来节点组

通过下面命令确认是否有 TiDB/PD/TiKV Pod 遗留在原节点组节点上：

{{< copyable "shell-regular" >}}

```bash
kubectl get po -n ${namespace} -owide
```

确认没有 TiDB/PD/TiKV Pod 遗留后，运行下面命令删除原节点组：

{{< copyable "shell-regular" >}}

```bash
eksctl delete nodegroup -f cluster.yaml --approve
```
