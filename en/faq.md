---
title: TiDB FAQs on Kubernetes
summary: Learn about TiDB FAQs on Kubernetes.
---

# TiDB FAQs on Kubernetes

This document collects frequently asked questions (FAQs) about the TiDB cluster on Kubernetes.

## How to modify time zone settings?

The default time zone setting for each component container of a TiDB cluster on Kubernetes is UTC. To change the timezone configuration, you can use the [Overlay](overlay.md) feature:

```yaml
apiVersion: core.pingcap.com/v1alpha1
kind: TiDBGroup
metadata:
  name: tidb
spec:
  template:
    spec:
      overlay:
        pod:
          spec:
            containers:
              - name: tidb
                env:
                  - name: "TZ"
                    value: "Asia/Shanghai"
```

## Can HPA or VPA be configured on TiDB components?

Currently, the TiDB cluster does not support HPA (Horizontal Pod Autoscaling) or VPA (Vertical Pod Autoscaling), because it is difficult to achieve autoscaling on stateful applications such as a database. Autoscaling can not be achieved merely by the monitoring data of CPU and memory.

## What scenarios require manual intervention when I use TiDB Operator to orchestrate a TiDB cluster?

Besides the operation of the Kubernetes cluster itself, TiDB Operator might require manual intervention in the following scenario:

* Maintaining or dropping the specified Kubernetes nodes. For more information, see [Maintaining Nodes](maintain-a-kubernetes-node.md).

## What is the recommended deployment topology when I use TiDB Operator to orchestrate a TiDB cluster on a public cloud?

To achieve high availability and data safety, it is recommended that you deploy the TiDB cluster in at least three availability zones in a production environment.

In terms of the deployment topology relationship between the TiDB cluster and TiDB services, TiDB Operator supports the following three deployment modes. Each mode has its own merits and demerits, so your choice must be based on actual application needs.

* Deploy the TiDB cluster and TiDB services in the same Kubernetes cluster of the same VPC.
* Deploy the TiDB cluster and TiDB services in different Kubernetes clusters of the same VPC.
* Deploy the TiDB cluster and TiDB services in different Kubernetes clusters of different VPCs.

## Does TiDB Operator support TiSpark?

TiDB Operator does not yet support automatically orchestrating TiSpark.

If you want to add the TiSpark component to TiDB on Kubernetes, you must maintain Spark on your own in **the same** Kubernetes cluster. You must ensure that Spark can access the IPs and ports of PD and TiKV instances, and install the TiSpark plugin for Spark. [TiSpark](https://docs.pingcap.com/tidb/stable/tispark-overview) offers a detailed guide for you to install the TiSpark plugin.

To maintain Spark on Kubernetes, refer to [Spark on Kubernetes](http://spark.apache.org/docs/latest/running-on-kubernetes.html).

## How to check the configuration of the TiDB cluster?

To check the configuration of the PD, TiKV, and TiDB components of the current cluster, run the following command:

* Check the PD configuration file:

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- cat /etc/pd/config.toml
    ```

* Check the TiKV configuration file:

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- cat /etc/tikv/config.toml
    ```

* Check the TiDB configuration file:

    ```shell
    kubectl exec -it ${pod_name} -n ${namespace} -- cat /etc/tidb/config.toml
    ```

## Why does TiDB Operator fail to schedule Pods when I deploy the TiDB clusters?

Two possible reasons:

* Insufficient resource or HA Policy causes the Pod stuck in the `Pending` state. For more information, see [Common Deployment Failures of TiDB on Kubernetes](deploy-failures.md#the-pod-is-in-the-pending-state).

* `taint` is applied to some nodes, which prevents the Pod from being scheduled to these nodes unless the Pod has the matching `toleration`. For more information, see [Taints and Tolerations](https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/).

## How does TiDB ensure data safety and reliability?

To ensure persistent storage of data, TiDB clusters deployed by TiDB Operator use [Persistent Volume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) provided by Kubernetes cluster as the storage.

To ensure data safety in case one node is down, PD and TiKV use [Raft Consistency Algorithm](https://raft.github.io/) to replicate the stored data as multiple replicas across nodes.

In the bottom layer, TiKV replicates data using the log replication and State Machine model. For write requests, data is written to the Leader node first, and then the Leader node replicates the command to its Follower nodes as a log. When most of the Follower nodes in the cluster receive this log from the Leader node, the log is committed and the State Machine changes accordingly.
