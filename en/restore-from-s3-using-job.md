---
title: Restore Backup Data from Amazon S3-Compatible Storage Using TiDB Lightning
summary: Learn how to use TiDB Lightning to restore backup data stored in Amazon S3-compatible storage to a TiDB cluster.
---

# Restore Backup Data from Amazon S3-Compatible Storage Using TiDB Lightning

This document describes how to use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning-overview/) to restore backup data from Amazon S3-compatible storage to a TiDB cluster. TiDB Lightning is a tool for fast full data import into a TiDB cluster. This document uses the [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning-physical-import-mode/). For detailed usage and configuration items of TiDB Lightning, refer to the [official documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning-overview/).

The following example shows how to restore backup data from Amazon S3-compatible storage to a TiDB cluster.

## Prepare a node pool for TiDB Lightning

You can run TiDB Lightning in an existing node pool or create a dedicated node pool. The following is a sample configuration for creating a new node pool. Replace the variables with your specific values as needed:

- `${clusterName}`: EKS cluster name

```yaml
# eks_lightning.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: ${clusterName}
  region: us-west-2
availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c']

nodeGroups:
  - name: lightning
    instanceType: c5.xlarge
    desiredCapacity: 1
    privateNetworking: true
    availabilityZones: ["us-west-2a"]
    labels:
      dedicated: lightning
```

Run the following command to create the node pool:

```shell
eksctl create nodegroup -f eks_lightning.yaml
```

## Deploy the TiDB Lightning job

This section describes how to configure, deploy, and monitor the TiDB Lightning job.

### Configure the TiDB Lightning job

The following is a sample configuration file (`lightning_job.yaml`) for the TiDB Lightning job. Replace the variables with your specific values as needed:

- `${name}`: Job name
- `${namespace}`: Kubernetes namespace
- `${version}`: TiDB Lightning image version
- `${storageClassName}`: Storage class name
- `${storage}`: Storage size
- For TiDB Lightning parameters, refer to [TiDB Lightning Configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning-configuration/).

```yaml
# lightning_job.yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ${name}-sorted-kv
  namespace: ${namespace}
spec:
  storageClassName: ${storageClassName}
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: ${storage}
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${name}
  namespace: ${namespace}
data:
  config-file: |
    [lightning]
    level = "info"
    
    [checkpoint]
    enable = true
  
    [tidb]
    host = "basic-tidb"
    port = 4000
    user = "root"
    password = ""
    status-port = 10080
    pd-addr = "basic-pd:2379"
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ${name}
  namespace: ${namespace}
  labels:
    app.kubernetes.io/component: lightning
spec:
  template:
    spec:
      nodeSelector:
        dedicated: lightning
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app.kubernetes.io/component
                operator: In
                values:
                - lightning
            topologyKey: kubernetes.io/hostname
      containers:
        - name: tidb-lightning
          image: pingcap/tidb-lightning:${version}
          command:
            - /bin/sh
            - -c
            - |
              /tidb-lightning \
                  --status-addr=0.0.0.0:8289 \
                  --backend=local \
                  --sorted-kv-dir=/var/lib/sorted-kv \
                  --d=s3://external/testfolder \
                  --config=/etc/tidb-lightning/tidb-lightning.toml \
                  --log-file="-"
          env:
            - name: AWS_REGION
              value: ${AWS_REGION}
            - name: AWS_ACCESS_KEY_ID
              value: ${AWS_ACCESS_KEY_ID}
            - name: AWS_SECRET_ACCESS_KEY
              value: ${AWS_SECRET_ACCESS_KEY}
            - name: AWS_SESSION_TOKEN
              value: ${AWS_SESSION_TOKEN}
          volumeMounts:
            - name: config
              mountPath: /etc/tidb-lightning
            - name: sorted-kv
              mountPath: /var/lib/sorted-kv
      volumes:
        - name: config
          configMap:
            name: ${name}
            items:
            - key: config-file
              path: tidb-lightning.toml
        - name: sorted-kv
          persistentVolumeClaim:
            claimName: ${name}-sorted-kv
      restartPolicy: Never
  backoffLimit: 0
```

### Create the TiDB Lightning job

Run the following commands to create the TiDB Lightning job:

```shell
export name=lightning
export version=v8.5.1
export namespace=tidb-cluster
export storageClassName=<your-storage-class>
export storage=250G
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=<your-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_SESSION_TOKEN=<your-session-token> # Optional

envsubst < lightning_job.yaml | kubectl apply -f -
```

### Check the TiDB Lightning job status

Run the following command to check the status of the Pod associated with the TiDB Lightning job:

```shell
kubectl -n ${namespace} get pod ${name}
```

### View TiDB Lightning job logs

Run the following command to retrieve and view the logs of the TiDB Lightning job:

```shell
kubectl -n ${namespace} logs pod ${name}
```