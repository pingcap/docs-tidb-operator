---
title: Back Up TiDB Data to Google Cloud Storage (GCS) Using Dumpling
summary: Learn how to use Dumpling to back up TiDB cluster data to Google Cloud Storage (GCS).
---

# Back Up TiDB Data to Google Cloud Storage (GCS) Using Dumpling

This document describes how to use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview/) to back up data from a TiDB cluster deployed on Google GKE to [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs). Dumpling is a data export tool that can export data from TiDB or MySQL in SQL or CSV format for full data backup or export.

## Prepare the Dumpling node pool

You can run Dumpling in an existing node pool or create a dedicated node pool. The following example shows how to create a new node pool. Replace the variables as needed:

- `${clusterName}`: GKE cluster name

```shell
gcloud container node-pools create dumpling \
    --cluster ${clusterName} \
    --machine-type n2-standard-4 \
    --num-nodes=1 \
    --node-labels=dedicated=dumpling
```

## Deploy the Dumpling job

### Create a credential ConfigMap

Save the `service account key` file downloaded from the Google Cloud Console as `google-credentials.json`, and then create a ConfigMap with the following command:

```shell
kubectl -n ${namespace} create configmap google-credentials --from-file=google-credentials.json
```

### Configure the Dumpling job

The following is a sample configuration file (`dumpling_job.yaml`) for the Dumpling job. Replace the variables as needed:

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
                  --threads=16 \
                  --rows=20000 \
                  --filesize=256MiB \
                  --database=test \
                  --filetype=csv \
                  --output=gcs://external/testfolder?credentials-file=/etc/config/google-credentials.json
          volumeMounts:
            - name: google-credentials
              mountPath: /etc/config
      volumes:
        - name: google-credentials
          configMap:
            name: google-credentials
      restartPolicy: Never
  backoffLimit: 0
```

### Create the Dumpling job

Run the following commands to create the Dumpling job:

```shell
export name=dumpling
export version=v8.5.1
export namespace=tidb-cluster

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