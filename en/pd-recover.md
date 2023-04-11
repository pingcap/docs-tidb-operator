---
title: Use PD Recover to Recover the PD Cluster
summary: Learn how to use PD Recover to recover the PD cluster.
---

# Use PD Recover to Recover the PD Cluster

PD Recover is a disaster recovery tool of [PD](https://pingcap.com/docs/stable/architecture/#placement-driver-server), used to recover the PD cluster which cannot start or provide services normally. For detailed introduction of this tool, see [TiDB documentation - PD Recover](https://pingcap.com/docs/stable/reference/tools/pd-recover). This document introduces how to download PD Recover and how to use it to recover a PD cluster.

## Download PD Recover

1. Download the official TiDB package:

    {{< copyable "shell-regular" >}}

    ```shell
    wget https://download.pingcap.org/tidb-community-toolkit-${version}-linux-amd64.tar.gz
    ```

    In the command above, `${version}` is the version of the TiDB cluster, such as `v5.3.0`.

2. Unpack the TiDB package:

    {{< copyable "shell-regular" >}}

    ```shell
    tar -xzf tidb-community-toolkit-${version}-linux-amd64.tar.gz
    tar -xzf tidb-community-toolkit-${version}-linux-amd64/pd-recover-${version}-linux-amd64.tar.gz
    ```

    `pd-recover` is in the current directory.

## Scenario 1: At least one PD node is alive

This section introduces how to recover the PD cluster using PD Recover and alive PD nodes. This section is only applicable to the scenario where the PD cluster has alive PD nodes. If all PD nodes are unavailable, refer to [Scenario 2](#scenario-2-all-pd-nodes-are-unavailable).

> **Note:**
>
> If you restore the cluster by using alive PD, the cluster can keep all the configuration information that has taken effect in PD before the restoration.

### Step 1. Recover the PD Pod

> **Note:**
>
> This document takes pd-0 as an example. If you use other PD pods, modify the corresponding command.

Use an alive PD node `pd-0` to force recreate the PD cluster. The detailed steps are as follows:

1. Let pd-0 pod enter debug mode:

    ```shell
    kubectl annotate pod ${cluster_name}-pd-0 -n ${namespace} runmode=debug
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -- kill -SIGTERM 1
    ```

2. Enter the pd-0 pod:

    ```shell
    kubectl -n ${cluster_name} exec -it basic-pd-0 -- sh
    ```

3. Refer to the default startup script [`_start_pd.sh.tpl`](https://github.com/pingcap/tidb-operator/blob/master/charts/tidb-cluster/templates/scripts/_start_pd.sh.tpl) and configure environment variables in pd-0:

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

4. Use original pd-0 data directory to force start a new PD cluster:

    ```shell
    echo "starting pd-server ..."
    sleep $((RANDOM % 10))
    echo "/pd-server --force-new-cluster ${ARGS}"
    exec /pd-server --force-new-cluster ${ARGS} &
    ```

5. Exit pd-0 pod:

    ```shell
    exit
    ```

6. Execute the following command to confirm that PD is started:

    ```shell
    kubectl logs -f ${cluster_name}-pd-0 -n ${namespace} | grep "Welcome to Placement Driver (PD)"
    ```

### Step 2. Recover the PD cluster

1. Copy `pd-recover` to the PD pod:

    ```shell
    kubectl cp ./pd-recover ${namespace}/${cluster_name}-pd-0:./
    ```

2. Recover the PD cluster by running the `pd-recover` command:

    In the command, use the newly created cluster in the previous step:

    ```shell
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -- ./pd-recover --from-old-member -endpoints http://127.0.0.1:2379
    ```

    ```
    recover success! please restart the PD cluster
    ```

### Step 3. Restart the PD Pod

1. Delete the PD Pod:

    ```shell
    kubectl delete pod ${cluster_name}-pd-0 -n ${namespace}
    ```

2. Confirm the Cluster ID is generated:

    ```shell
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- wget -q http://127.0.0.1:2379/pd/api/v1/cluster
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- cat cluster
    ```

### Step 4. Recreate other failed or available PD nodes

In this example, recreate pd-1 and pd-2:

```shell
kubectl -n ${namespace} delete pvc pd-${cluster_name}-pd-1 --wait=false
kubectl -n ${namespace} delete pvc pd-${cluster_name}-pd-2 --wait=false

kubectl -n ${namespace} delete pod ${cluster_name}-pd-1
kubectl -n ${namespace} delete pod ${cluster_name}-pd-2
```

### Step 5. Check PD health and configuration

Check health:

```shell
kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- ./pd-ctl health
```

Check configuration. The following command uses placement rules as an example:

```shell
kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- ./pd-ctl config placement-rules show
```

### Step 6. Restart TiDB and TiKV

Use the following commands to restart the TiDB and TiKV clusters:

```shell
kubectl delete pod -l app.kubernetes.io/component=tidb,app.kubernetes.io/instance=${cluster_name} -n ${namespace} &&
kubectl delete pod -l app.kubernetes.io/component=tikv,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
```

## Scenarios 2: All PD nodes are down and cannot be recovered

This section introduces how to recover the PD cluster by using PD Recover and creating new PD nodes. This section is only applicable when all PD nodes in the cluster have failed and cannot be recovered. If there are alive PD nodes in the cluster, refer to [Scenario 1](#scenario-1-at-least-one-pd-node-is-alive).

> **Warning:**
>
> If you restore the cluster by creating new PD nodes, the cluster will lose all the configuration information that has taken effect in PD before the restoration.

### Step 1: Get Cluster ID

{{< copyable "shell-regular" >}}

```shell
kubectl get tc ${cluster_name} -n ${namespace} -o='go-template={{.status.clusterID}}{{"\n"}}'
```

Example:

```
kubectl get tc test -n test -o='go-template={{.status.clusterID}}{{"\n"}}'
6821434242797747735
```

### Step 2. Get Alloc ID

When you use `pd-recover` to recover the PD cluster, you need to specify `alloc-id`. The value of `alloc-id` must be larger than the largest allocated ID (`Alloc ID`) of the original cluster.

1. Access the Prometheus monitoring data of the TiDB cluster by taking steps in [Access the Prometheus monitoring data](monitor-a-tidb-cluster.md#access-the-prometheus-monitoring-data).

2. Enter `pd_cluster_id` in the input box and click the `Execute` button to make a query. Get the largest value in the query result.

3. Multiply the largest value in the query result by `100`. Use the multiplied value as the `alloc-id` value specified when using `pd-recover`.

### Step 3. Recover the PD Pod

1. Delete the Pod of the PD cluster.

    Execute the following command to set the value of `spec.pd.replicas` to `0`:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": 0}}}'
    ```

    Because the PD cluster is in an abnormal state, TiDB Operator cannot synchronize the change above to the PD StatefulSet. You need to execute the following command to set the `spec.replicas` of the PD StatefulSet to `0`.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch sts ${cluster_name}-pd -n ${namespace} -p '{"spec":{"replicas": 0}}'
    ```

    Execute the following command to confirm that the PD Pod is deleted:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl get pod -n ${namespace}
    ```

2. After confirming that all PD Pods are deleted, execute the following command to delete the PVCs bound to the PD Pods:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete pvc -l app.kubernetes.io/component=pd,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
    ```

3. After the PVCs are deleted, scale out the PD cluster to one Pod:

    Execute the following command to set the value of `spec.pd.replicas` to `1`:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": 1}}}'
    ```

    Because the PD cluster is in an abnormal state, TiDB Operator cannot synchronize the change above to the PD StatefulSet. You need to execute the following command to set the `spec.replicas` of the PD StatefulSet to `1`.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl patch sts ${cluster_name}-pd -n ${namespace} -p '{"spec":{"replicas": 1}}'
    ```

    Execute the following command to confirm that the PD cluster is started:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs -f ${cluster_name}-pd-0 -n ${namespace} | grep "Welcome to Placement Driver (PD)"
    ```

### Step 4. Recover the cluster

1. Copy `pd-recover` command to the PD pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl cp ./pd-recover ${namespace}/${cluster_name}-pd-0:./
    ```

2. Execute the `pd-recover` command to recover the PD cluster:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec ${cluster_name}-pd-0 -n ${namespace} -- ./pd-recover -endpoints http://127.0.0.1:2379 -cluster-id ${cluster_id} -alloc-id ${alloc_id}
    ```

    In the command above, `${cluster_id}` is the cluster ID got in [Get Cluster ID](#step-1-get-cluster-id). `${alloc_id}` is the largest value of `pd_cluster_id` (got in [Get Alloc ID](#step-2-get-alloc-id)) multiplied by `100`.

    After the `pd-recover` command is successfully executed, the following result is printed:

    ```shell
    recover success! please restart the PD cluster
    ```

### Step 5. Restart the PD Pod

1. Delete the PD Pod:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl delete pod ${cluster_name}-pd-0 -n ${namespace}
    ```

2. Execute the following command to confirm the Cluster ID is the one got in [Get Cluster ID](#step-1-get-cluster-id).

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- wget -q http://127.0.0.1:2379/pd/api/v1/cluster
    kubectl -n ${namespace} exec -it ${cluster_name}-pd-0 -- cat cluster
    ```

### Step 6. Scale out the PD cluster

Execute the following command to set the value of `spec.pd.replicas` to the desired number of Pods:

{{< copyable "shell-regular" >}}

```shell
kubectl patch tc ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"pd":{"replicas": $replicas}}}'
```

### Step 7. Restart TiDB and TiKV

Use the following commands to restart the TiDB and TiKV clusters:

{{< copyable "shell-regular" >}}

```shell
kubectl delete pod -l app.kubernetes.io/component=tidb,app.kubernetes.io/instance=${cluster_name} -n ${namespace} &&
kubectl delete pod -l app.kubernetes.io/component=tikv,app.kubernetes.io/instance=${cluster_name} -n ${namespace}
```
