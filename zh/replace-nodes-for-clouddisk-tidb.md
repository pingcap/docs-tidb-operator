---
title: 为使用云上存储的 TiDB 集群更换节点
summary: 介绍如何为使用云上存储的 TiDB 集群更换节点。
---

# 为使用云上存储的 TiDB 集群更换节点

本文介绍一种在不停机情况下为使用云上存储的 TiDB 集群更换、升级节点的方法。

本文以 `Amazon EKS` 为例，介绍了如何创建新的节点组，然后使用滚动重启迁移 TiDB 集群到新节点组。

> **注意：**
>
> 其它公有云环境请参考[GCP GKE](deploy-on-gcp-gke.md)、[Azure AKS](deploy-on-azure-aks.md)、[阿里云 ACK](deploy-on-alibaba-cloud.md) 操作节点组。

## 前置条件

- 云上已经存在一个 TiDB 集群。如果没有，可参考 [Amazon EKS](deploy-on-aws-eks.md) 进行部署。
- TiDB 集群使用云上存储作为数据盘。

## 第一步：创建新的节点组

1. 找到云上 TiDB 集群的 `eksctl` 部署配置文件 `cluster.yaml`, 并拷贝保存为 `cluster-new.yaml`

2. `cluster-new.yaml` 加入新节点组 `tidb-1b-new`、`tikv-1a-new`：

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
    > * `availabilityZones` 不能修改。
    > * 本例仅以 `tidb-1b-new`、`tikv-1a-new` 节点组为例，请自行配置参数。

3. `cluster-new.yaml` 中删除要更换的原节点组

    本例中删除 `tidb-1b`、`tikv-1a` 节点组，请根据情况自行删除。

4. `cluster.yaml` 中删除需要保留的节点组（留下要更换的原节点组，因为这些最后要被删除）

5. 执行命令：

    {{< copyable "shell-regular" >}}

    ```bash
    eksctl create nodegroup -f cluster_new.yml
    ```

    > **注意：**
    >
    > 该命令只创建新的节点组，已经存在的节点组会忽略，不会重复创建，更不会删除不存在的节点组。

## 第二步：使用 `kubectl cordon` 命令标记原节点组节点为不可调度，防止新的 Pod 调度上去

{{< copyable "shell-regular" >}}

```bash
kubectl cordon -l alpha.eksctl.io/nodegroup-name=${origin_nodegroup1}
kubectl cordon -l alpha.eksctl.io/nodegroup-name=${origin_nodegroup2}
...
```

其中 `${origin_nodegroup}` 是原节点组名称，本例中是 `tidb-1b`、`tikv-1a`，请根据情况自行删除。

## 第三步：滚动重启 TiDB 集群

参考[重启 Kubernetes 上的 TiDB 集群](restart-a-tidb-cluster.md)滚动重启 TiDB 集群。

## 第四步：删除原来节点组

{{< copyable "shell-regular" >}}

```bash
eksctl delete nodegroup -f cluster.yaml
```
