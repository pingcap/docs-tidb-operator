---
title: 使用 PD Recover 恢复 PD 集群
summary: 了解如何使用 PD Recover 恢复 PD 集群。
---

# 使用 PD Recover 恢复 PD 集群

PD Recover 是对 PD 进行灾难性恢复的工具，用于恢复无法正常启动或服务的 PD 集群。该工具的详细介绍参见 [TiDB 文档 - PD Recover](https://pingcap.com/docs-cn/stable/reference/tools/pd-recover)。本文档介绍如何下载 PD Recover 工具，以及如何使用该工具恢复 PD 集群。

## 下载 PD Recover

1. 下载 TiDB 官方安装包：

    {{< copyable "shell-regular" >}}

    ```shell
    wget https://download.pingcap.org/tidb-community-toolkit-${version}-linux-amd64.tar.gz
    ```

    `${version}` 是 TiDB 集群版本，例如，`v5.3.0`。

2. 解压安装包：

    {{< copyable "shell-regular" >}}

    ```shell
    tar -xzf tidb-community-toolkit-${version}-linux-amd64.tar.gz
    tar -xzf tidb-community-toolkit-${version}-linux-amd64/pd-recover-${version}-linux-amd64.tar.gz
    ```

    `pd-recover` 在当前目录下。

## 场景 1：集群中有可用 PD 节点

本小节详细介绍如何使用 PD Recover 并通过可用的 PD 节点来恢复 PD 集群。本小节内容仅适用于集群中有可用的 PD 节点，如集群中所有 PD 节点均故障且无法恢复，请参考[这篇文档](#场景 2：所有 PD 节点都故障且无法恢复)。

> **提示：**
>
> 通过可用 PD 节点来恢复集群，可以保留之前 PD 已生效的所有配置信息。

### 第 1 步：恢复 PD 集群 Pod

> **提示：**
>
> 这里以 pd-0 为例，若使用其他 PD pod，请调整对应的命令。

使用一个可用 PD 节点 `pd-0` 强制重建 PD 集群。具体步骤如下：

1. 让 pd-0 pod 进入 Debug 模式：

    ```shell
    kubectl annotate pod ${cluster_name}-pd-0 -n ${namespace} runmode=debug
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -- kill -SIGTERM 1
    ```

2. 进入 pd-0 pod：

    ```shell
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -it -- sh
    ```

3. 参考默认启动脚本 [`pd-start-script`](https://github.com/pingcap/tidb-operator/blob/91f4edf549c9a268972dfe1aaf8e7f89feec65ff/pkg/manager/member/startscript/v1/template.go#L116)，或者参考其他可用 PD 节点的启动脚本，在 pd-0 里配置环境变量：

    ```shell
    # Use HOSTNAME if POD_NAME is unset for backward compatibility.
    POD_NAME=${POD_NAME:-$HOSTNAME}
    # the general form of variable PEER_SERVICE_NAME is: "<clusterName>-pd-peer"
    cluster_name=`echo ${PEER_SERVICE_NAME} | sed 's/-pd-peer//'`
    domain="${POD_NAME}.${PEER_SERVICE_NAME}.${NAMESPACE}.svc"
    discovery_url="${cluster_name}-discovery.${NAMESPACE}.svc:10261"
    encoded_domain_url=`echo ${domain}:2380 | base64 | tr "\n" " " | sed "s/ //g"`
    elapseTime=0
    period=1
    threshold=30
    while true; do
    sleep ${period}
    elapseTime=$(( elapseTime+period ))

    if [[ ${elapseTime} -ge ${threshold} ]]
    then
    echo "waiting for pd cluster ready timeout" >&2
    exit 1
    fi

    if nslookup ${domain} 2>/dev/null
    then
    echo "nslookup domain ${domain}.svc success"
    break
    else
    echo "nslookup domain ${domain} failed" >&2
    fi
    done

    ARGS="--data-dir=/var/lib/pd \
    --name=${POD_NAME} \
    --peer-urls=http://0.0.0.0:2380 \
    --advertise-peer-urls=http://${domain}:2380 \
    --client-urls=http://0.0.0.0:2379 \
    --advertise-client-urls=http://${domain}:2379 \
    --config=/etc/pd/pd.toml \
    "

    if [[ -f /var/lib/pd/join ]]
    then
    # The content of the join file is:
    #   demo-pd-0=http://demo-pd-0.demo-pd-peer.demo.svc:2380,demo-pd-1=http://demo-pd-1.demo-pd-peer.demo.svc:2380
    # The --join args must be:
    #   --join=http://demo-pd-0.demo-pd-peer.demo.svc:2380,http://demo-pd-1.demo-pd-peer.demo.svc:2380
    join=`cat /var/lib/pd/join | tr "," "\n" | awk -F'=' '{print $2}' | tr "\n" ","`
    join=${join%,}
    ARGS="${ARGS} --join=${join}"
    elif [[ ! -d /var/lib/pd/member/wal ]]
    then
    until result=$(wget -qO- -T 3 http://${discovery_url}/new/${encoded_domain_url} 2>/dev/null); do
    echo "waiting for discovery service to return start args ..."
    sleep $((RANDOM % 5))
    done
    ARGS="${ARGS}${result}"
    fi
    ```

4. 使用原始的 pd-0 数据目录强制启动一个新的 PD 集群：

    ```shell
    echo "starting pd-server ..."
    sleep $((RANDOM % 10))
    echo "/pd-server --force-new-cluster ${ARGS}"
    exec /pd-server --force-new-cluster ${ARGS} &
    ```

5. 退出 pd-0 pod：

    ```shell
    exit
    ```

6. 确认 pd-0 已启动：

    ```shell
    kubectl logs -f ${cluster_name}-pd-0 -n ${namespace} | grep "Welcome to Placement Driver (PD)"
    ```

### 第 2 步：使用 PD Recover 恢复 PD 集群

1. 拷贝 `pd-recover` 到 PD pod：

    ```shell
    kubectl cp ./pd-recover ${namespace}/${cluster_name}-pd-0:./
    ```

2. 使用 `pd-recover` 恢复 PD 集群：

    这里使用上一步创建的新集群：

    ```shell
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -- ./pd-recover --from-old-member -endpoints http://127.0.0.1:2379
    ```

    ```
    recover success! please restart the PD cluster
    ```

### 第 3 步：重启 PD Pod

1. 删除 PD Pod：

    ```shell
    kubectl delete pod ${cluster_name}-pd-0 -n ${namespace}
    ```

2. 通过如下命令确认 Cluster ID 已生成：

    ```shell
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- wget -q http://127.0.0.1:2379/pd/api/v1/cluster
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- cat cluster
    ```

### 第 4 步：重建其他故障和可用的 PD 节点

这里以 pd-1 和 pd-2 为例：

```shell
kubectl -n ${namespace} delete pvc pd-${cluster_name}-pd-1 --wait=false
kubectl -n ${namespace} delete pvc pd-${cluster_name}-pd-2 --wait=false

kubectl -n ${namespace} delete pod ${cluster_name}-pd-1
kubectl -n ${namespace} delete pod ${cluster_name}-pd-2
```

### 第 5 步：检查 PD 健康情况和配置信息

检查健康情况：

```shell
kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- ./pd-ctl health
```

检查配置信息，这里以 placement rules 为例：

```shell
kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- ./pd-ctl config placement-rules show
```

### 第 6 步：重启 TiDB 和 TiKV

使用以下命令重启 TiDB 和 TiKV 实例：

```shell
kubectl delete pod -l app.kubernetes.io/component=tidb,app.kubernetes.io/instance=${cluster_name} -n ${namespace} &&
kubectl delete pod -l app.kubernetes.io/component=tikv,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
```

## 场景 2：所有 PD 节点都故障且无法恢复

本小节详细介绍如何使用 PD Recover 并通过新建 PD 的方式来恢复 PD 集群。本小节内容仅适用于集群中所有 PD 节点均故障且无法恢复的情况，如集群中有可用的 PD 节点，请参考[这篇文档](#场景 1：集群中有可用 PD 节点)。

> **警告：**
>
> 通过新建 PD 的方式来恢复集群，会丢失之前 PD 已生效的所有配置信息。

### 第 1 步：获取 Cluster ID

使用以下命令获取 PD 集群的 Cluster ID：

{{< copyable "shell-regular" >}}

```shell
kubectl get tc ${cluster_name} -n ${namespace} -o='go-template={{.status.clusterID}}{{"\n"}}'
```

示例：

```
kubectl get tc test -n test -o='go-template={{.status.clusterID}}{{"\n"}}'
6821434242797747735
```

### 第 2 步：获取 Alloc ID

使用 `pd-recover` 恢复 PD 集群时，需要指定 `alloc-id`。`alloc-id` 的值是一个比当前已经分配的最大的 `Alloc ID` 更大的值。

1. 参考[访问 Prometheus 监控数据](monitor-a-tidb-cluster.md#访问-prometheus-监控数据)打开 TiDB 集群的 Prometheus 访问页面。

2. 在输入框中输入 `pd_cluster_id` 并点击 `Execute` 按钮查询数据，获取查询结果中的最大值。

3. 将查询结果中的最大值乘以 `100`，作为使用 `pd-recover` 时指定的 `alloc-id`。

### 第 3 步：恢复 PD 集群 Pod

1. 删除 PD 集群 Pod。

    通过如下命令设置 `spec.pd.replicas` 为 `0`：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": 0}}}'
    ```

    由于此时 PD 集群异常，TiDB Operator 无法将上面的改动同步到 PD StatefulSet，所以需要通过如下命令设置 PD StatefulSet `spec.replicas` 为 `0`：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch sts ${cluster_name}-pd -n ${namespace} -p '{"spec":{"replicas": 0}}'
    ```

    通过如下命令确认 PD Pod 已经被删除：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod -n ${namespace}
    ```

2. 确认所有 PD Pod 已经被删除后，通过如下命令删除 PD Pod 绑定的 PVC：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete pvc -l app.kubernetes.io/component=pd,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
    ```

3. PVC 删除完成后，扩容 PD 集群至一个 Pod。

    通过如下命令设置 `spec.pd.replicas` 为 `1`：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": 1}}}'
    ```

    由于此时 PD 集群异常，TiDB Operator 无法将上面的改动同步到 PD StatefulSet，所以需要通过如下命令设置 PD StatefulSet `spec.replicas` 为 `1`：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch sts ${cluster_name}-pd -n ${namespace} -p '{"spec":{"replicas": 1}}'
    ```

    通过如下命令确认 PD 已经启动：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs -f ${cluster_name}-pd-0 -n ${namespace} | grep "Welcome to Placement Driver (PD)"
    ```

### 第 4 步：使用 PD Recover 恢复 PD 集群

1. 拷贝 `pd-recover` 到 PD pod：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cp ./pd-recover ${namespace}/${cluster_name}-pd-0:./
    ```

2. 使用 `pd-recover` 恢复 PD 集群：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -- ./pd-recover -endpoints http://127.0.0.1:2379 -cluster-id ${cluster_id} -alloc-id ${alloc_id}
    ```

    `${cluster_id}` 是[获取 Cluster ID](#第-1-步获取-cluster-id) 步骤中获取的 Cluster ID，`${alloc_id}` 是[获取 Alloc ID](#第-2-步获取-alloc-id) 步骤中获取的 `pd_cluster_id` 的最大值再乘以 `100`。

    `pd-recover` 命令执行成功后，会打印如下输出：

    ```shell
    recover success! please restart the PD cluster
    ```

### 第 5 步：重启 PD Pod

1. 删除 PD Pod：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete pod ${cluster_name}-pd-0 -n ${namespace}
    ```

2. 通过如下命令确认 Cluster ID 为[获取 Cluster ID](#第-1-步获取-cluster-id) 步骤中获取的 Cluster ID：

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- wget -q http://127.0.0.1:2379/pd/api/v1/cluster
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- cat cluster
    ```

### 第 6 步：扩容 PD 集群

通过如下命令设置 `spec.pd.replicas` 为期望的 Pod 数量：

{{< copyable "shell-regular" >}}

```shell
kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": $replicas}}}'
```

### 第 7 步：重启 TiDB 和 TiKV

使用以下命令重启 TiDB 和 TiKV 实例：

{{< copyable "shell-regular" >}}

```shell
kubectl delete pod -l app.kubernetes.io/component=tidb,app.kubernetes.io/instance=${cluster_name} -n ${namespace} &&
kubectl delete pod -l app.kubernetes.io/component=tikv,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
```
