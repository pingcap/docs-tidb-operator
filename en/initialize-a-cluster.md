---
title: Initialize a TiDB Cluster in Kubernetes
summary: Learn how to initialize a TiDB cluster in K8s.
category: how-to
---

# Initialize a TiDB Cluster in Kubernetes

This document describes how to initialize a TiDB cluster in Kubernetes (K8s), specifically, how to configure the initial account and password and how to initialize the database by executing SQL statements automatically in batch.

> **Note:**
>
> - After creating the TiDB cluster, if you manually change the password of the `root` account, the initialization will fail.
> - The following steps apply only when you have created a cluster for the first time. Further configuration or modification after the initial cluster creation is not valid.

## Step 1: Configure TidbInitializer

Refer to [TidbInitializer example](https://github.com/pingcap/tidb-operator/blob/master/manifests/initializer/tidb-initializer.yaml), [API documentation](api-references.md), and the following steps to complete TidbInitializer Custom Resource (CR), and save it to the `<cluster-name>/tidb-initializer.yaml` file. Please switch the TidbInitializer example and API documentation to the currently used version of TiDB Operator.

### Set initial account and password

When a cluster is created, a default account `root` is created with no password. This might cause security issues. You can set a password for the `root` account in the following methods:

- Create a [`secret`](https://kubernetes.io/docs/concepts/configuration/secret/) to specify the password for `root`:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic tidb-secret --from-literal=root=<root-password> --namespace=<namespace>
    ```

- If you want to create more than one user, add the desired username and the password in the above command. For example:

    {{< copyable "shell-regular" >}}

    ```shell
    kubectl create secret generic tidb-secret --from-literal=root=<root-password> --from-literal=developer=<developer-passowrd> --namespace=<namespace>
    ```

    This command creates `root` and `developer` users with their passwords, which are saved in the `tidb-secret` object. By default, the regular `developer` user is only granted with the `USAGE` privilege. You can set other privileges in the `initSql` configuration item.

## Step 2: Set a host that has access to TiDB

To set a host that has access to TiDB, modify the `permitHost: <mysql-client-host-name>` configuration item in `<cluster-name>/tidb-initializer.yaml`. If it is not set, all hosts have access to TiDB. For details, refer to [Mysql GRANT host name](https://dev.mysql.com/doc/refman/5.7/en/grant.html).

## Step 3: Initialize SQL statements in batch

The cluster can also automatically execute the SQL statements in batch in `initSql` during the initialization. This function can be used to create some databases or tables for the cluster and perform user privilege management operations.

For example, the following configuration automatically creates a database named `app` after the cluster creation, and grants the `developer` account full management privileges on `app`:

{{< copyable "yaml" >}}

```yaml
spec:
...
initSql: |-
    CREATE DATABASE app;
    GRANT ALL PRIVILEGES ON app.* TO 'developer'@'%';
```

> **Note:**
>
> Currently no verification has been implemented for `initSql`. You can create accounts and set passwords in `initSql`, but it is not recommended to do so because passwords created this way are saved as plaintext in the initializer job object.

## Step 4: Initialize the cluster

{{< copyable "shell-regular" >}}

```shell
kubectl apply -f <cluster-name>/tidb-initializer.yaml --namespace=<namespace>
```

The above command automatically creates an initialized Job. This Job tries to set the initial password for the `root` account using the `secret` object provided. It also tries to create other accounts and passwords, if they are specified.

After the initialization, the Pod state becomes `Completed`. If you log in via MySQL client later, you need to specify the password created by the Job.
