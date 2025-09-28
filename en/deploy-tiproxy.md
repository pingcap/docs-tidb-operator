---
title: Deploy TiProxy Load Balancer for an Existing TiDB Cluster
summary: Learn how to deploy TiProxy for an existing TiDB cluster on Kubernetes.
---

# Deploy TiProxy Load Balancer for an Existing TiDB Cluster

This topic describes how to deploy or remove the TiDB load balancer [TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy-overview) for an existing TiDB cluster on Kubernetes. TiProxy is placed between the client and TiDB server to provide load balancing, connection persistence, and service discovery for TiDB.

> **Note:**
>
> If you have not deployed a TiDB cluster, you can add TiProxy configurations when [configuring a TiDB cluster](configure-a-tidb-cluster.md) and then [deploy a TiDB cluster](deploy-on-general-kubernetes.md). In that case, you do not need to refer to this topic.

## Deploy TiProxy

If you need to deploy TiProxy for an existing TiDB cluster, follow these steps:

> **Note:**
>
> If your server does not have access to the internet, refer to [Deploy a TiDB Cluster](deploy-on-general-kubernetes.md#deploy-the-tidb-cluster) to download the `pingcap/tiproxy` Docker image to a machine with access to the internet and then upload the Docker image to your server. Then, use `docker load` to install the Docker image on your server.

1. Edit the TidbCluster Custom Resource (CR):

    ``` shell
    kubectl edit tc ${cluster_name} -n ${namespace}
    ```

2. Add the TiProxy configuration as shown in the following example:

    ```yaml
    spec:
      tiproxy:
        baseImage: pingcap/tiproxy
        replicas: 3
    ```

3. Configure the related parameters in `spec.tiproxy.config` of the TidbCluster CR. For example:

    ```yaml
    spec:
      tiproxy:
        config: |
          [log]
          level = "info"
    ```

    For more information about TiProxy configuration, see [TiProxy Configuration](https://docs.pingcap.com/tidb/stable/tiproxy-configuration).

4. Configure the related parameters in `spec.tidb` of the TidbCluster CR. For example:

    + It is recommended to configure `graceful-wait-before-shutdown` to a value greater than the maximum duration of the transactions in your application. This is used together with TiProxy's connection migration feature. For more information, see [TiProxy Limitations](https://docs.pingcap.com/tidb/stable/tiproxy-overview#limitations).

        ```yaml
          spec:
            tidb:
              config: |
                graceful-wait-before-shutdown = 30
       ```

    + If [TLS is enabled for the cluster](enable-tls-between-components.md), skip this step. If TLS is not enabled for the cluster, you need to generate a self-signed certificate and manually configure [`session-token-signing-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#session-token-signing-cert-new-in-v640) and [`session-token-signing-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#session-token-signing-key-new-in-v640) for TiDB:

        ```yaml
        spec:
          tidb:
            additionalVolumes:
              - name: sessioncert
                secret:
                  secretName: sessioncert-secret
            additionalVolumeMounts:
              - name: sessioncert
                mountPath: /var/session
            config: |
              session-token-signing-cert = "/var/session/tls.crt"
              session-token-signing-key = "/var/session/tls.key"
        ```

        For more information, see [`session-token-signing-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#session-token-signing-cert-new-in-v640).

After TiProxy is started, you can find the corresponding `tiproxy-sql` load balancer service by running the following command.

``` shell
kubectl get svc -n ${namespace}
```

## Access TiProxy

TiProxy exposes a `NodePort` type service, which provides two endpoints:

- `tiproxy-api`: for API access.
- `tiproxy-sql`: for the MySQL protocol access.

To get the service ports, run the following command:

```shell
kubectl -n tidb-cluster get service basic-tiproxy
```

The output is as follows:

```
NAME            TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                         AGE
basic-tiproxy   NodePort   10.101.114.216   <none>        3080:31006/TCP,6000:31539/TCP   3h19m
```

To show details for the `tiproxy-sql` endpoint only, append a `jq` filter to the command:

```shell
kubectl -n tidb-cluster get service basic-tiproxy -o json | jq '.spec.ports[]|select(.name == "tiproxy-sql")'
```

The output is as follows:

```json
{
  "name": "tiproxy-sql",
  "nodePort": 31539,
  "port": 6000,
  "protocol": "TCP",
  "targetPort": 6000
}
```

Use this information to connect to TiProxy with a MySQL client:

```shell
mysql -h <clusterIP> -P <nodePort>
```

If you use [minikube](https://minikube.sigs.k8s.io/docs/start/), run the following command to get the correct IP address and port:

```shell
minikube service basic-tiproxy -n tidb-cluster
```

The output is as follows:

```
┌──────────────┬───────────────┬──────────────────┬───────────────────────────┐
│  NAMESPACE   │     NAME      │   TARGET PORT    │            URL            │
├──────────────┼───────────────┼──────────────────┼───────────────────────────┤
│ tidb-cluster │ basic-tiproxy │ tiproxy-api/3080 │ http://192.168.49.2:31006 │
│              │               │ tiproxy-sql/6000 │ http://192.168.49.2:31539 │
└──────────────┴───────────────┴──────────────────┴───────────────────────────┘
[tidb-cluster basic-tiproxy tiproxy-api/3080
tiproxy-sql/6000 http://192.168.49.2:31006
http://192.168.49.2:31539]
```

From the output, find the row with `tiproxy-sql/6000` and use the hostname and port number in the `URL` column to connect.

## Remove TiProxy

If your TiDB cluster no longer needs TiProxy, follow these steps to remove it.

1. Modify `spec.tiproxy.replicas` to `0` to remove the TiProxy Pod by running the following command.

    ```shell
    kubectl patch tidbcluster ${cluster_name} -n ${namespace} --type merge -p '{"spec":{"tiproxy":{"replicas": 0}}}'
    ```

2. Check the status of the TiProxy Pod.

    ```shell
    kubectl get pod -n ${namespace} -l app.kubernetes.io/component=tiproxy,app.kubernetes.io/instance=${cluster_name}
    ```

    If the output is empty, the TiProxy Pod has been successfully removed.

3. Delete the TiProxy StatefulSet.

    1. Modify the TidbCluster CR and delete the `spec.tiproxy` field by running the following command:

        ```shell
        kubectl patch tidbcluster ${cluster_name} -n ${namespace} --type json -p '[{"op":"remove", "path":"/spec/tiproxy"}]'
        ```

    2. Delete the TiProxy StatefulSet by running the following command:

        ```shell
        kubectl delete statefulsets -n ${namespace} -l app.kubernetes.io/component=tiproxy,app.kubernetes.io/instance=${cluster_name}
        ```

    3. Check whether the TiProxy StatefulSet has been successfully deleted by running the following command:

        ```shell
        kubectl get sts -n ${namespace} -l app.kubernetes.io/component=tiproxy,app.kubernetes.io/instance=${cluster_name}
        ```

        If the output is empty, the TiProxy StatefulSet has been successfully deleted.
