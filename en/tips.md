---
title: Tips for troubleshooting TiDB in Kubernetes
summary: Learn the commonly used tips for troubleshooting TiDB in Kubernetes.
---

# Tips for troubleshooting TiDB in Kubernetes

This document describes the commonly used tips for troubleshooting TiDB in Kubernetes.

## Use the diagnostic mode

When a Pod is in the `CrashLoopBackoff` state, the containers in the Pod exit continually. As a result, you cannot use `kubectl exec` normally, making it inconvenient to diagnose issues.

To solve this problem, TiDB Operator provides the Pod diagnostic mode for PD, TiKV, and TiDB components. In this mode, the containers in the Pod hang directly after they are started, and will not repeatedly crash. Then you can use `kubectl exec` to connect to the Pod containers for diagnosis.

To use the diagnostic mode for troubleshooting:

1. Add an annotation to the Pod to be diagnosed:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate pod ${pod_name} -n ${namespace} runmode=debug
    ```

    When the container in the Pod is restarted again, it will detect this annotation and enter the diagnostic mode.

    > **Note:**
    >
    > If Pod is running, restart the container forcedly by the following command.
    > 
    > ```shell
    > kubectl exec ${pod_name} -n ${namespace} -c ${container} -- kill -SIGTERM 1
    >

2. Wait for the Pod to enter the Running state.

    {{< copyable "shell-regular" >}}

    ```shell
    watch kubectl get pod ${pod_name} -n ${namespace}
    ```

    Here's an example of using `kubectl exec` to get into the container for diagnosis:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- /bin/sh
    ```

3. After finishing the diagnosis and resolving the problem, delete the Pod.

    ```shell
    kubectl delete pod ${pod_name} -n ${namespace}
    ```

After the Pod is rebuilt, it automatically returns to the normal mode.

## Modify the configuration of a TiKV

In some test scenarios, if you need to modify the configuration of a TiKV and not affect others, you can use the following methods.

### Modify online

Refer to the [document](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-online), you can use SQL to modify the configuration of a TiKV online.

> **Note:**
>
> The modification by this method is temporary and not persistent. When  the Pod is restarted, the original configuration will be used.

### Modify manually in diagnostic mode

After the TiKV Pod enter diagnostic mode, you can modify the configuration of TiKV, then specify the modified configuration and start the TiKV process manually.

The steps are as follows:

1. Get the start command from the TiKV log, it is used in following steps.
   
    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs pod ${pod_name} -n ${namespace} -c tikv | head -2 | tail -1
    ```

    The output is similar to the following, and this line is the start command.

    ```shell
    /tikv-server --pd=http://${tc_name}-pd:2379 --advertise-addr=${pod_name}.${tc_name}-tikv-peer.default.svc:20160 --addr=0.0.0.0:20160 --status-addr=0.0.0.0:20180 --data-dir=/var/lib/tikv --capacity=0 --config=/etc/tikv/tikv.toml
    ```

    > **Note:**
    >
    > If the TiKV Pod is in the `CrashLoopBackoff` state, can't get the start command from the log, you can splice the start command by using the above command format.

2. Turn on diagnostic mode for the Pod and restart the Pod.
   
    Add an annotation to the Pod and wait for the Pod restarted.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate pod ${pod_name} -n ${namespace} runmode=debug
    ```

    If Pod is running, restart the container forcedly by the following command.

    {{< copyable "shell-regular" >}}
  
    ```shell
    kubectl exec ${pod_name} -n ${namespace} -c tikv -- kill -SIGTERM 1
    ```

    Check the log of TiKV to ensure it is in diagnostic mode.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs ${pod_name} -n ${namespace} -c tikv
    ```

    The output is similar to the following:

    ```
    entering debug mode.
    ```

3. Enter the TiKV container by the following command.
   
    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -c tikv -- sh
    ```

4. In the TiKV container, copy the configuration file of TiKV to a new file, then modify the new file.
   
    {{< copyable "shell-regular" >}}

    ```shell
    cp /etc/tikv/tikv.toml /tmp/tikv.toml && vi /tmp/tikv.tmol
    ```

5. In the TiKV container, modify the `--config` flag as the new configuration file in the start command which is getted in step 1, then start the TiKV process.

    ```shell
    /tikv-server --pd=http://${tc_name}-pd:2379 --advertise-addr=${pod_name}.${tc_name}-tikv-peer.default.svc:20160 --addr=0.0.0.0:20160 --status-addr=0.0.0.0:20180 --data-dir=/var/lib/tikv --capacity=0 --config=/tmp/tikv.toml
    ```

After the test is completed, if you want to recover the TiKV Pod, you can delete the TiKV Pod and wait for the Pod to be started.

{{< copyable "shell-regular" >}}

```shell
kubectl delete ${pod_name} -n ${namespace}
```

## Configure forced upgrade for TiKV cluster

In normal scenarios, During TiKV rolling upgrade TiDB Operator evict all Region leaders for TiKV Pod before restarting TiKV Pod, it is used for minimize the impact of the rolling upgrade on user requests. In some test scenarios, if you do not need to wait for the Region leader to migrate during TiKV rolling upgrade, or if you want to speed up the rolling upgrade, you can configure the `spec.tikv.evictLeaderTimeout` field in the spec of TidbCluster to a small value.

```yaml
spec:
  tikv:
    evictLeaderTimeout: 10s
```

For more about this field, refer to the [document](configure-a-tidb-cluster.md#configure-graceful-upgrade-for-tikv-cluster).
