---
title: Tips for troubleshooting TiDB in Kubernetes
summary: Learn the commonly used tips for troubleshooting TiDB in Kubernetes.
---

# Tips for troubleshooting TiDB in Kubernetes

This document describes the commonly used tips for troubleshooting TiDB in Kubernetes.

## Use the debug mode

When a Pod is in the `CrashLoopBackoff` state, the containers in the Pod exit continually. As a result, you cannot use `kubectl exec` normally, making it inconvenient to diagnose issues.

To solve this problem, TiDB Operator provides the Pod debug mode for PD, TiKV, and TiDB components. In this mode, the containers in the Pod hang directly after they are started, and will not repeatedly crash. Then you can use `kubectl exec` to connect to the Pod containers for diagnosis.

To use the debug mode for troubleshooting:

1. Add an annotation to the Pod to be diagnosed:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate pod ${pod_name} -n ${namespace} runmode=debug
    ```

    When the container in the Pod is restarted again, it will detect this annotation and enter the debug mode.

    > **Note:**
    >
    > If Pod is running, you can force restart the container by running the following command.
    >
    > ```shell
    > kubectl exec ${pod_name} -n ${namespace} -c ${container} -- kill -SIGTERM 1
    > ```

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

## Modify the configuration of a TiKV instance

In some test scenarios, if you need to modify the configuration of a TiKV instance and do not want the configuration to affect other instances, you can use the following methods.

### Modify online

Refer to the [document](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-online) and use SQL to online modify the configuration of a single TiKV instance.

> **Note:**
>
> The modification made by this method is temporary and not persistent. After the Pod is restarted, the original configuration will be used.

### Modify manually in debug mode

After the TiKV Pod enters debug mode, you can modify the TiKV configuration file and then manually start the TiKV process using the modified configuration file.

The steps are as follows:

1. Get the start command from the TiKV log, which will be used in a subsequent step.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs pod ${pod_name} -n ${namespace} -c tikv | head -2 | tail -1
    ```

    You can see a similar output as follows, which is the start command of TiKV.

    ```shell
    /tikv-server --pd=http://${tc_name}-pd:2379 --advertise-addr=${pod_name}.${tc_name}-tikv-peer.default.svc:20160 --addr=0.0.0.0:20160 --status-addr=0.0.0.0:20180 --data-dir=/var/lib/tikv --capacity=0 --config=/etc/tikv/tikv.toml
    ```

    > **Note:**
    >
    > If the TiKV Pod is in the `CrashLoopBackoff` state, you cannot get the start command from the log. In such cases, you might splice the start command according to the above command format.

2. Turn on debug mode for the Pod and restart the Pod.

    Add an annotation to the Pod and wait for the Pod to restart.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl annotate pod ${pod_name} -n ${namespace} runmode=debug
    ```

    If the Pod keeps running, you can force restart the container by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec ${pod_name} -n ${namespace} -c tikv -- kill -SIGTERM 1
    ```

    Check the log of TiKV to ensure that the Pod is in debug mode.

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl logs ${pod_name} -n ${namespace} -c tikv
    ```

    The output is similar to the following:

    ```
    entering debug mode.
    ```

3. Enter the TiKV container by running the following command:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -c tikv -- sh
    ```

4. In the TiKV container, copy the configuration file of TiKV to a new file, and modify the new file.

    {{< copyable "shell-regular" >}}

    ```shell
    cp /etc/tikv/tikv.toml /tmp/tikv.toml && vi /tmp/tikv.tmol
    ```

5. In the TiKV container, modify the start command obtained in Step 1 and configure the `--config` flag as the new configuration file. Run the modified start command to start the TiKV process:

    ```shell
    /tikv-server --pd=http://${tc_name}-pd:2379 --advertise-addr=${pod_name}.${tc_name}-tikv-peer.default.svc:20160 --addr=0.0.0.0:20160 --status-addr=0.0.0.0:20180 --data-dir=/var/lib/tikv --capacity=0 --config=/tmp/tikv.toml
    ```

After the test is completed, if you want to recover the TiKV Pod, you can delete the TiKV Pod and wait for the Pod to be automatically started.

{{< copyable "shell-regular" >}}

```shell
kubectl delete ${pod_name} -n ${namespace}
```

## Configure forceful upgrade for the TiKV cluster

Normally, during TiKV rolling update, TiDB Operator evicts all Region leaders for TiKV Pods before restarting the TiKV Pods. This is meant for minimizing the impact of the rolling update on user requests.

In some test scenarios, if you do not need to wait for the Region leader to migrate during TiKV rolling upgrade, or if you want to speed up the rolling upgrade, you can configure the `spec.tikv.evictLeaderTimeout` field in the spec of TidbCluster to a small value.

```yaml
spec:
  tikv:
    evictLeaderTimeout: 10s
```

For more information about this field, refer to [Configure graceful upgrade](configure-a-tidb-cluster.md#configure-graceful-upgrade-for-tikv-cluster).

> **Warning:**
>
> Configuring forceful upgrade causes some user requests to fail. It is not recommended for a production environment.
