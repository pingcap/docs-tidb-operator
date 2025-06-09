---
title: Back Up TiDB Data to Amazon S3-Compatible Storage Using Dumpling
summary: Learn how to use Dumpling to back up TiDB cluster data to Amazon S3-compatible storage.
---

# Back Up TiDB Data to Amazon S3-Compatible Storage Using Dumpling

This document describes how to use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview/) to back up data from a TiDB cluster deployed on AWS EKS to Amazon S3-compatible storage. Dumpling is a data export tool that exports data from TiDB or MySQL in SQL or CSV format for full data backup or export.

## Prepare the Dumpling node pool

You can run Dumpling in an existing node pool or create a dedicated node pool. The following is a sample configuration for creating a new node pool. Replace the variables as needed:

- `${clusterName}`: EKS cluster name

```yaml
# eks_dumpling.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: ${clusterName}
  region: us-west-2
availabilityZones: ['us-west-2a', 'us-west-2b', 'us-west-2c']

nodeGroups:
  - name: dumpling
    instanceType: c5.xlarge
    desiredCapacity: 1
    privateNetworking: true
    availabilityZones: ["us-west-2a"]
    labels:
      dedicated: dumpling
```

Run the following command to create the node pool:

```shell
eksctl create nodegroup -f eks_dumpling.yaml
```

## Deploy the Dumpling job

This section describes how to configure, deploy, and monitor the Dumpling job.

### Configure the Dumpling job

The following is a sample configuration file (`dumpling_job.yaml`) for the Dumpling job. Replace the variables with your specific values as needed:

- `${name}`: job name
- `${namespace}`: Kubernetes namespace
- `${version}`: Dumpling image version
- For Dumpling parameters, refer to the [Option list of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview/#option-list-of-dumpling).

```yaml
# dumpling_job.yaml
---
apiVersion: batch/v1
kind: Job
metadata:
  name: ${name}
  namespace: ${namespace}
  labels:
    app.kubernetes.io/component: dumpling
spec:
  template:
    spec:
      nodeSelector:
        dedicated: dumpling
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app.kubernetes.io/component
                operator: In
                values:
                - dumpling
            topologyKey: kubernetes.io/hostname
      containers:
        - name: ${name}
          image: pingcap/dumpling:${version}
          command:
            - /bin/sh
            - -c
            - |
              /dumpling \
                  --host=basic-tidb \
                  --port=4000 \
                  --user=root \
                  --password='' \
                  --s3.region=${AWS_REGION} \
                  --threads=16 \
                  --rows=20000 \
                  --filesize=256MiB \
                  --database=test \
                  --filetype=csv \
                  --output=s3://bucket-path/
          env:
            - name: AWS_REGION
              value: ${AWS_REGION}
            - name: AWS_ACCESS_KEY_ID
              value: ${AWS_ACCESS_KEY_ID}
            - name: AWS_SECRET_ACCESS_KEY
              value: ${AWS_SECRET_ACCESS_KEY}
            - name: AWS_SESSION_TOKEN
              value: ${AWS_SESSION_TOKEN}
      restartPolicy: Never
  backoffLimit: 0
```

### Create the Dumpling job

Run the following commands to create the Dumpling job:

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=<your-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_SESSION_TOKEN=<your-session-token> # Optional

envsubst < dumpling_job.yaml | kubectl apply -f -
```

### Check the Dumpling job status

Run the following command to check the Pod status of the Dumpling job:

```shell
kubectl -n ${namespace} get pod ${name}
```

### View Dumpling job logs

Run the following command to view the logs of the Dumpling job:

```shell
kubectl -n ${namespace} logs pod ${name}
```