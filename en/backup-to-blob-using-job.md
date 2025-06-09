---
title: Back Up TiDB Data to Azure Blob Storage Using Dumpling
summary: Learn how to use Dumpling to back up TiDB cluster data to Azure Blob Storage.
---

# Back Up TiDB Data to Azure Blob Storage Using Dumpling

This document describes how to use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview/) to back up data from a TiDB cluster deployed on Azure AKS to Azure Blob Storage. Dumpling is a data export tool that exports data from TiDB or MySQL in SQL or CSV format for full data backup or export.

## Prepare the Dumpling node pool

You can run Dumpling in an existing node pool or create a dedicated node pool. The following example shows how to create a new node pool. Replace the variables as needed:

- `${clusterName}`: AKS cluster name
- `${resourceGroup}`: Resource group name

```shell
az aks nodepool add --name dumpling \
    --cluster-name ${clusterName} \
    --resource-group ${resourceGroup} \
    --zones 1 2 3 \
    --node-count 1 \
    --labels dedicated=dumpling
```

## Deploy the Dumpling job

This section describes how to configure, deploy, and monitor Dumpling jobs.

### Configure the Dumpling job

The following is a sample configuration for the Dumpling job. Replace the variables with your specific values as needed:

- `${name}`: Job name
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
                  --s3.region=us-west-2 \
                  --threads=16 \
                  --rows=20000 \
                  --filesize=256MiB \
                  --database=test \
                  --filetype=csv \
                  --output=azure://external/testfolder?account-name=${accountname}&account-key=${accountkey}
      restartPolicy: Never
  backoffLimit: 0
```

### Create the Dumpling job

Run the following commands to create the Dumpling job. Replace the variables with your specific values as needed:

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster
export accountname=<your-account-name>
export accountkey=<your-account-key>

envsubst < dumpling_job.yaml | kubectl apply -f -
```

### Check the Dumpling job status

Run the following command to check the Pod status of the Dumpling job. Replace the variables with your specific values as needed:

```shell
kubectl -n ${namespace} get pod ${name}
```

### View Dumpling job logs

Run the following command to view the logs of the Dumpling job. Replace the variables with your specific values as needed:

```shell
kubectl -n ${namespace} logs pod ${name}
```