---
title: 为使用本地存储的 TiDB 集群更换节点
summary: 介绍如何为使用本地存储的 TiDB 集群更换节点。
---

# 为使用本地存储的 TiDB 集群更换节点

本文介绍一种在不停机情况下为使用本地存储的 TiDB 集群更换、升级节点的方法。

> **注意：**
>
> * 如果你只需要维护 TiDB 集群中个别节点，可以参考[维护 TiDB 集群所在的 Kubernetes 节点](maintain-a-kubernetes-node.md)。

## 前置条件

- 已经存在一个原 TiDB 集群，可以参考[在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)进行部署。
- 新的节点准备就绪，并已加入原 TiDB Kubernetes 集群。

## 第一步：克隆原 TiDB 集群配置

1. 导出克隆集群文件 `tidb-cluster-clone.yaml`，可以执行下面命令：

    {{< copyable "shell-regular" >}}
    
    ```bash
    kubectl get tidbcluster ${origin_cluster_name} -n ${namespace} -oyaml > tidb-cluster-clone.yaml
    ```

   其中 `${origin_cluster_name}` 是原集群名字，`${namespace}` 是原集群命名空间。

2. 修改 `tidb-cluster-clone.yaml`，让新克隆集群加入原 TiDB 集群：

    ```yaml
    kind: TidbCluster
    metadata:
      name: ${clone_cluster_name}
    spec:
      cluster:
        name: ${origin_cluster_name}
    ...
    ```

    其中 `${clone_cluster_name}` 是克隆集群的新名字，`${origin_cluster_name}` 是原集群名字。

## 第二步：为克隆集群签发证书

如果原集群开启了 TLS，你需要为克隆集群签发证书。如果原集群没有开启 TLS，请忽略此步骤，直接执行第三步。

### 使用 cfssl 系统签发

如果你使用 cfssl，必须使用和原集群相同的 CA (Certification Authority) 颁发。你需要执行[使用 cfssl 系统颁发证书](enable-tls-between-components.md#使用-cfssl-系统颁发证书)文档中 5~7 步，完成新集群组件间证书签发。

### 使用 cert-manager 系统签发

如果你使用 cert-manager，必须使用和原集群相同的 Issuer (`${cluster_name}-tidb-issuer`) 来创建 Certificate。你需要执行[使用 cert-manager 系统颁发证书](enable-tls-between-components.md#使用-cert-manager-系统颁发证书)文档中第 3 步，完成新集群组件间证书签发。

## 第三步：标记需要更换的节点为不可调度

使用 `kubectl cordon` 命令把需要更换的节点标记为不可调度，防止新的 Pod 调度上去：

{{< copyable "shell-regular" >}}

```bash
kubectl cordon ${replace_nodename1} ${replace_nodename2} ...
```

## 第四步：创建克隆 TiDB 集群

1. 执行命令：

    {{< copyable "shell-regular" >}}
    
    ```bash
    kubectl apply -f tidb-cluster-clone.yaml
    ```

2. 确认克隆 TiDB 集群与原 TiDB 集群组成的新集群正常运行：

   - 获取新集群 store 个数、状态：

     {{< copyable "shell-regular" >}}

       ```bash
       # store 个数
       pd-ctl -u http://<address>:<port> store | jq '.count'
       # store 状态
       pd-ctl -u http://<address>:<port> store | jq '.stores | .[] | .store.state_name'
       ```

   - 通过 MySQL 客户端[访问 Kubernetes 上的 TiDB 集群](access-tidb.md)。

## 第五步：缩容原集群 TiDB 节点

将原集群的 TiDB 节点缩容至 0 个，参考[水平扩缩容](scale-a-tidb-cluster.md#水平扩缩容)一节。

> **注意：**
>
> 若通过负载均衡或数据库访问层中间件的方式接入待迁移 TiDB 集群，则需要在缩容原集群 TiDB 之前，先修改配置，将业务流量迁移至目标 TiDB 集群，避免影响业务。

## 第六步：缩容待迁移集群 TiKV 节点

将原集群的 TiKV 节点缩容至 0 个，参考[水平扩缩容](scale-a-tidb-cluster.md#水平扩缩容)一节。

## 第七步：缩容原集群 PD 节点

将原集群的 PD 节点缩容至 0 个，参考[水平扩缩容](scale-a-tidb-cluster.md#水平扩缩容)一节。

## 第八步：删除克隆集群中 `spec.cluster` 字段

{{< copyable "shell-regular" >}}

```bash
kubectl patch -n ${namespace} tc ${clone_cluster_name} --type=json -p '[{"op":"remove", "path":"/spec/cluster"}]'
```

其中 `${namespace}` 是克隆集群的命名空间（不变），`${clone_cluster_name}` 是克隆集群名字。

## 第九步：删除原 TiDB 集群、数据、节点

1. 删除原集群 `TidbCluster`：

    {{< copyable "shell-regular" >}}
    
    ```bash
    kubectl delete -n ${namespace} tc ${origin_cluster_name}
    ```
    
    其中 `${namespace}` 是原集群的命名空间（不变），`${origin_cluster_name}` 是原集群名字。

2. 删除原集群数据，请参考[删除 PV 以及对应的数据](configure-storage-class.md)一节。
3. 将需要更换的节点从 Kubernetes 集群中删除：

    {{< copyable "shell-regular" >}}

    ```bash
    kubectl delete node ${replace_nodename1} ${replace_nodename2} ...
    ```
