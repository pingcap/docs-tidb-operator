---
title: Enable TidbCluster Auto-scaling
summary: Learn how to use the TidbCluster auto-scaling feature.
category: how-to
---

# Enable TidbCluster Auto-scaling

Kubernetes provides [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/), a native API based on CPU utilization. Correspondingly, in TiDB Operator 1.1 and later versions, you can enable the auto-scaling feature in a TiDB cluster based on the features of Kubernetes. This document introduces how to enable and use the auto-scaling feature of TidbCluster.

## Enable the auto-scaling feature

> **Warning:**
>
> * The auto-scaling feature is in the alpha stage. It is highly **not recommended** to enable this feature in the critical production environment.
> * It is recommended to try this feature in a test environment on the internal network. PingCAP welcomes your comments and suggestions to help improve this feature.

To turn this feature on, you need to enable some related configurations in TiDB Operator. The auto-scaling feature is disabled by default. Take the following steps to manually turn it on.

1. Edit the `values.yaml` file in TiDB Operator.

    Enable `AutoScaling` in the `features` option:

    ```yaml
    features:
      - AutoScaling=true
    ```

    Enable the `Operator Webhook` feature:

    ```yaml
    admissionWebhook:
      create: true
      mutation:
        pods: true
    ```

    For more information about `Operator Webhook`, see [Enable Admission Controller in TiDB Operator](enable-admission-webhook.md).

2. Install or update TiDB Operator.

    To install or update TiDB Operator, see [Deploy TiDB Operator in Kubernetes](deploy-tidb-operator.md).

## TidbClusterAutoScaler

The `TidbClusterAutoScaler` CR object is used to control the behavior of the auto-scaling in the TiDB cluster. If you have used [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/), presumably you are familiar with the notion `TidbClusterAutoScaler`. The following is an auto-scaling example in TiKV.

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbClusterAutoScaler
metadata:
  name: auto-scaling-demo
spec:
  cluster:
    name: auto-scaling-demo
    namespace: default
  monitor:
    name: auto-scaling-demo
    namespace: default
  tikv:
    minReplicas: 3
    maxReplicas: 4
    metrics:
      - type: "Resource"
        resource:
          name: "cpu"
          target:
            type: "Utilization"
            averageUtilization: 80
```

The TiDB component can be configured using `spec.tidb`. Currently, the auto-scaling API of TiDB is the same as that of TiKV.

In a `TidbClusterAutoScaler` object, the `cluster` attribute specifies the TiDB clusters to be auto-scaled. These clusters are marked by `name` and `namespace`. You need to provide the metrics collection and query service to `TidbClusterAutoScaler` because it captures resource usage through the metrics collection component. The `monitor` attribute refers to the `TidbMonitor` object. For more information, see [Monitor TiDB Clusters using TidbMonitor](monitor-using-tidbmonitor.md).

For the external `Prometheus` other than `TidbMonitor`, you can fill in the Host by configuring `spec.metricsUrl` to specify the monitoring metrics collection service for the TiDB cluster. If you deploy the monitoring of the TiDB cluster using `Helm`, take the following steps to specify `spec.metricsUrl`.

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbClusterAutoScaler
metadata:
  name: auto-scaling-demo
spec:
  cluster:
    name: auto-scaling-demo
    namespace: default
  metricsUrl: "http://<release-name>-prometheus.<release-namespace>.svc:9090"
  ......
```

## Quick start

Run the following commands to quickly deploy a TiDB cluster with 3 PD instances, 3 TiKV instances, 2 TiDB instances, and the monitoring and the auto-scaling features.

```shell
$ kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/auto-scale/tidb-cluster.yaml -n <namespace>
tidbcluster.pingcap.com/auto-scaling-demo created

$ kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/auto-scale/tidb-monitor.yaml -n <namespace>
tidbmonitor.pingcap.com/auto-scaling-demo created

$ kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/examples/auto-scale/tidb-cluster-auto-scaler.yaml  -n <namespace>
tidbclusterautoscaler.pingcap.com/auto-scaling-demo created
```

After the TiDB cluster is created, you can stress test the auto-scaling feature through database stress test tools such as [sysbench](https://www.percona.com/blog/tag/sysbench/).

Run the following commands to destroy the environment:

```shell
kubectl delete tidbcluster auto-scaling-demo -n <namespace>
kubectl delete tidbmonitor auto-scaling-demo -n <namespace>
kubectl delete tidbclusterautoscaler auto-scaling-demo -n <namespace>
```

## TidbClusterAutoScaler configurations

1. Set the auto-scaling interval.

    Compared with the stateless web service, a distributed database software is often sensitive to the instance auto-scaling. You need to make sure that there is a certain interval between each auto-scaling in case scaling operations are too frequent.
    You can set the interval (in seconds) between each auto-scaling by configuring `spec.tikv.scaleInIntervalSeconds` and `spec.tikv.ScaleOutIntervalSeconds` in TiTV. This also applies to TiDB.

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbClusterAutoScaler
    metadata:
      name: auto-sclaer
    spec:
      tidb:
        scaleInIntervalSeconds: 500
        ScaleOutIntervalSeconds: 300
      tikv:
        scaleInIntervalSeconds: 500
        ScaleOutIntervalSeconds: 300
    ```

2. Set the maximum value and the minimum value.

    You can set the maximum value and the minimum value of each component in `TidbClusterAutoScaler` to control the scaling range of `TiDB` and `TiKV`, which is similar to [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbClusterAutoScaler
    metadata:
      name: auto-scaling-demo
    spec:
      tikv:
        minReplicas: 3
        maxReplicas: 4
      tidb:
        minReplicas: 2
        maxReplicas: 3
    ```

3. Set the CPU auto-scaling configurations.

    Currently, `TidbClusterAutoScaler` only supports CPU utilization based auto-scaling. The descriptive API is as follows. `averageUtilization` refers to the threshold of CPU utilization. If the utilization exceeds 80%, the auto-scaling is triggered.

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbClusterAutoScaler
    metadata:
      name: auto-scaling-demo
    spec:
      tikv:
        minReplicas: 3
        maxReplicas: 4
        metrics:
          - type: "Resource"
            resource:
              name: "cpu"
              target:
                type: "Utilization"
                averageUtilization: 80
    ```

4. Set the time window configurations

    The CPU utilization based auto-scaling allows `TidbClusterAutoScaler` to get the CPU metrics of `TiDB` and `TiKV` from the specified monitoring system. You can specify the time window of metrics collection.

    ```yaml
    apiVersion: pingcap.com/v1alpha1
    kind: TidbClusterAutoScaler
    metadata:
      name: basic
      tidb:
        metricsTimeDuration: "1m"
        metrics:
          - type: "Resource"
            resource:
              name: "cpu"
              target:
                type: "Utilization"
                averageUtilization: 60
    ```
