---
title: 为使用本地存储的 TiDB 集群更换节点
summary: 介绍如何为使用本地存储的 TiDB 集群更换节点。
---

# 为使用本地存储的 TiDB 集群更换节点

本文介绍一种在不停机情况下为使用本地存储的 TiDB 集群更换、升级节点的方法。

## 前置条件

- 已经存在一个原 TiDB 集群，可以参考 [在标准 Kubernetes 上部署 TiDB 集群](deploy-on-general-kubernetes.md)进行部署。
- 新的节点准备就绪，并已加入原 TiDB Kubernetes 集群。

## 第一步：克隆原 TiDB 集群配置

1. 克隆原 TiDB 集群 `tidb-cluster.yaml` 为 `tidb-cluster-clone.yaml`。
2. 为 `tidb-cluster-clone.yaml` 中 `metadata.name` 换一个新名字。

    > **注意：**
    >
    > * 可能需要修改克隆集群中的 TiKV replicas，因为克隆集群中 TiKV 副本数应大于 PD 中设置的 max-replicas 数量，默认情况下 TiKV 副本数量需要大于等于 3。
    > * 克隆集群 namespace 保持不变。

3. 在 `tidb-cluster-clone.yaml` 中 `spec` 下加入如下内容，先加入原 TiDB 集群：

```yaml
kind: TidbCluster
metadata:
  name: ${clone-cluster-name}
spec:
   cluster:
   name: ${origin-cluster-name}
...
```

其中 `${clone-cluster-name}` 是克隆集群的新名字，`${origin-cluster-name}` 是原集群名字。

## 第二步：如果原集群开启了 TLS，为克隆集群签发证书

如果原集群没有开启 TLS 请忽略此步骤。

### 使用 cfssl 系统签发

如果你使用 cfssl，必须使用和原集群相同的 CA (Certification Authority) 颁发。你需要执行为 TiDB 组件间开启 TLS 文档中 5 ～ 7 步，完成新集群组件间证书签发。

其他 TLS 相关信息，可参考以下文档：

- [为 TiDB 组件间开启 TLS](enable-tls-between-components.md)
- [为 MySQL 客户端开启 TLS](enable-tls-for-mysql-client.md)

### 使用 cert-manager 系统签发

如果你使用 cert-manager，必须使用和原集群相同的 Issuer（${cluster_name}-tidb-issuer） 来创建 Certificate。你需要执行为 TiDB 组件间开启 TLS 文档中第 3 步，完成新集群组件间证书签发。

## 第三步：创建克隆 TiDB 集群

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

## 第四步：缩容原集群 TiDB 节点

将原集群的 TiDB 节点缩容至 0 个，参考[水平扩缩容](scale-a-tidb-cluster.md#水平扩缩容)一节

> **注意：**
>
> 若通过负载均衡或数据库访问层中间件的方式接入待迁移 TiDB 集群，则先修改配置，将业务流量迁移至目标 TiDB 集群，避免影响业务。

## 第五步：缩容待迁移集群 TiKV 节点

将原集群的 TiKV 节点缩容至 0 个，参考[水平扩缩容](scale-a-tidb-cluster.md#水平扩缩容)一节

> **注意：**
>
> * 依次缩容待迁移集群的 TiKV 节点，等待上一个 TiKV 节点对应的 store 状态变为 "tombstone" 后，再执行下一个 TiKV 节点的缩容操作。
> * 可通过 PD Control 工具查看 store 状态。

## 第六步：缩容原集群 PD 节点

将原集群的 PD 节点缩容至 0 个，参考[水平扩缩容](scale-a-tidb-cluster.md#水平扩缩容)一节

## 第七步：删除克隆集群中 `spec.cluster` 字段

{{< copyable "shell-regular" >}}

```bash
kubectl patch -n ${namespace} tc ${clone-cluster-name} --type=json -p '[{"op":"remove", "path":"/spec/cluster"}]'
```

其中 `${namespace}` 是克隆集群的命名空间（不变），`${clone-cluster-name}` 是克隆集群名字。

## 第八步：删除原 TiDB 集群及数据

1. 删除原集群 `TidbCluster`：

    {{< copyable "shell-regular" >}}
    
    ```bash
    kubectl delete -n ${namespace} tc ${origin-cluster-name}
    ```
    
    其中 `${namespace}` 是原集群的命名空间（不变），`${origin-cluster-name}` 是原集群名字。

2. 删除原集群数据，请参考[删除 PV 以及对应的数据](configure-storage-class.md)一节。