---
title: Persistent Storage Class Configuration on Kubernetes
summary: Learn how to configure local PVs and network PVs.
aliases: ['/docs/tidb-in-kubernetes/dev/configure-storage-class/','/docs/dev/tidb-in-kubernetes/reference/configuration/local-pv/']
---

# Persistent Storage Class Configuration on Kubernetes

TiDB cluster components such as PD, TiKV, TiDB monitoring, TiDB Binlog, and `tidb-backup` require persistent storage for data. To achieve this on Kubernetes, you need to use [PersistentVolume (PV)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/). Kubernetes supports different types of [storage classes](https://kubernetes.io/docs/concepts/storage/volumes/), which can be categorized into two main types:

- Network storage

    Network storage is not located on the current node but is mounted to the node through the network. It usually has redundant replicas to ensure high availability. In the event of a node failure, the corresponding network storage can be remounted to another node for continued use.

- Local storage

    Local storage is located on the current node and typically provides lower latency compared to network storage. However, it does not have redundant replicas, so data might be lost if the node fails. If the node is an IDC server, data can be partially restored, but if it is a virtual machine using local disk on a public cloud, data cannot be retrieved after a node failure.

PVs are automatically created by the system administrator or volume provisioner. PVs and Pods are bound by [PersistentVolumeClaim (PVC)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims). Instead of creating a PV directly, users request to use a PV through a PVC. The corresponding volume provisioner creates a PV that meets the requirements of the PVC and then binds the PV to the PVC.

> **Warning:**
>
> Do not delete a PV under any circumstances unless you are familiar with the underlying volume provisioner. Manually deleting a PV can result in orphaned volumes and unexpected behavior.

## Recommended storage classes for TiDB clusters

TiKV uses the Raft protocol to replicate data. When a node fails, PD automatically schedules data to fill the missing data replicas. TiKV requires low read and write latency, so it is strongly recommended to use local SSD storage in a production environment.

PD also uses Raft to replicate data. PD is not an I/O-intensive application, but rather a database for storing cluster meta information. Therefore, a local SAS disk or network SSD storage such as EBS General Purpose SSD (gp2) volumes on AWS or SSD persistent disks on Google Cloud can meet the requirements.

To ensure availability, it is recommended to use network storage for components such as TiDB monitoring, TiDB Binlog, and `tidb-backup` because they do not have redundant replicas. TiDB Binlog's Pump and Drainer components are I/O-intensive applications that require low read and write latency, so it is recommended to use high-performance network storage such as EBS Provisioned IOPS SSD (io1) volumes on AWS or SSD persistent disks on Google Cloud.

When deploying TiDB clusters or `tidb-backup` with TiDB Operator, you can configure the `StorageClass` for the components that require persistent storage via the corresponding `storageClassName` field in the `values.yaml` configuration file. The `StorageClassName` is set to `local-storage` by default.

## Network PV configuration

To enable volume expansion for the corresponding `StorageClass`, run the following command:

```shell
kubectl patch storageclass ${storage_class} -p '{"allowVolumeExpansion": true}'
```

After enabling volume expansion, you can expand the PV using the following method:

1. Edit the PersistentVolumeClaim (PVC) object:

    Suppose the PVC is currently 10 Gi and you need to expand it to 100 Gi.

    ```shell
    kubectl patch pvc -n ${namespace} ${pvc_name} -p '{"spec": {"resources": {"requests": {"storage": "100Gi"}}}}'
    ```

2. View the size of the PV:

    After the expansion, the size displayed by running `kubectl get pvc -n ${namespace} ${pvc_name}` still shows the original size. However, if you run the following command to view the size of the PV, it shows that the size has been expanded to the expected value.

    ```shell
    kubectl get pv | grep ${pvc_name}
    ```

## Local PV configuration

Currently, Kubernetes supports statically allocated local storage. To create a local storage object, use `local-volume-provisioner` in the [local-static-provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner) repository.

### Step 1: Pre-allocate local storage

- For a disk that stores TiKV data, you can [mount](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/docs/operations.md#use-a-whole-disk-as-a-filesystem-pv) the disk into the `/mnt/ssd` directory.

    To achieve high performance, it is recommended to allocate a dedicated disk for TiDB, with SSD being the recommended disk type.

- For a disk that stores PD data, follow the [steps](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/docs/operations.md#sharing-a-disk-filesystem-by-multiple-filesystem-pvs) to mount the disk. First, create multiple directories on the disk and bind mount the directories into the `/mnt/sharedssd` directory.

    >**Note:**
    >
    > The number of directories you create depends on the planned number of TiDB clusters and the number of PD servers in each cluster. Each directory has a corresponding PV created, and each PD server uses one PV.

- For a disk that stores monitoring data, follow the [steps](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/docs/operations.md#sharing-a-disk-filesystem-by-multiple-filesystem-pvs) to mount the disk. First, create multiple directories on the disk and bind mount the directories into the `/mnt/monitoring` directory.

    >**Note:**
    >
    > The number of directories you create depends on the planned number of TiDB clusters. Each directory has a corresponding PV created, and each TiDB cluster's monitoring data uses one PV.

- For a disk that stores TiDB Binlog and backup data, follow the [steps](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/docs/operations.md#sharing-a-disk-filesystem-by-multiple-filesystem-pvs) to mount the disk. First, create multiple directories on the disk and bind mount the directories into the `/mnt/backup` directory.

    >**Note:**
    >
    > The number of directories you create depends on the planned number of TiDB clusters, the number of Pumps in each cluster, and your backup method. Each directory has a corresponding PV created, and each Pump and Drainer use one PV. All [Ad-hoc full backup](backup-to-s3.md#ad-hoc-full-backup-to-s3-compatible-storage) tasks and [scheduled full backup](backup-to-s3.md#scheduled-full-backup-to-s3-compatible-storage) tasks share one PV.

The `/mnt/ssd`, `/mnt/sharedssd`, `/mnt/monitoring`, and `/mnt/backup` directories mentioned above are discovery directories used by local-volume-provisioner. For each subdirectory in the discovery directory, local-volume-provisioner creates a corresponding PV.

### Step 2: Deploy local-volume-provisioner

#### Online deployment

1. Download the deployment file for the local-volume-provisioner.

    ```shell
    wget https://raw.githubusercontent.com/pingcap/tidb-operator/v1.6.1/examples/local-pv/local-volume-provisioner.yaml
    ```

2. If you are using the same discovery directory as described in [Step 1: Pre-allocate local storage](#step-1-pre-allocate-local-storage), you can skip this step. If you are using a different path for the discovery directory than in the previous step, you need to modify the ConfigMap and DaemonSet spec.

    * Modify the `data.storageClassMap` field in the ConfigMap spec:

        ```yaml
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: local-provisioner-config
          namespace: kube-system
        data:
          # ...
          storageClassMap: |
            ssd-storage:
              hostDir: /mnt/ssd
              mountDir: /mnt/ssd
            shared-ssd-storage:
              hostDir: /mnt/sharedssd
              mountDir: /mnt/sharedssd
            monitoring-storage:
              hostDir: /mnt/monitoring
              mountDir: /mnt/monitoring
            backup-storage:
              hostDir: /mnt/backup
              mountDir: /mnt/backup
        ```

        For more configuration options for the local-volume-provisioner, refer to the [Configuration](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/docs/provisioner.md#configuration) document.

    * Modify the `volumes` and `volumeMounts` fields in the DaemonSet spec to ensure that the discovery directory can be mounted to the corresponding directory in the Pod:

        ```yaml
        ......
              volumeMounts:
                - mountPath: /mnt/ssd
                  name: local-ssd
                  mountPropagation: "HostToContainer"
                - mountPath: /mnt/sharedssd
                  name: local-sharedssd
                  mountPropagation: "HostToContainer"
                - mountPath: /mnt/backup
                  name: local-backup
                  mountPropagation: "HostToContainer"
                - mountPath: /mnt/monitoring
                  name: local-monitoring
                  mountPropagation: "HostToContainer"
          volumes:
            - name: local-ssd
              hostPath:
                path: /mnt/ssd
            - name: local-sharedssd
              hostPath:
                path: /mnt/sharedssd
            - name: local-backup
              hostPath:
                path: /mnt/backup
            - name: local-monitoring
              hostPath:
                path: /mnt/monitoring
        ......
        ```

3. Deploy the `local-volume-provisioner`.

    ```shell
    kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/v1.6.1/manifests/local-dind/local-volume-provisioner.yaml
    ```

4. Check the status of the Pod and PV.

    ```shell
    kubectl get po -n kube-system -l app=local-volume-provisioner && \
    kubectl get pv | grep -e ssd-storage -e shared-ssd-storage -e monitoring-storage -e backup-storage
    ```

    The `local-volume-provisioner` creates a PV for each mounting point under the discovery directory.

    > **Note:**
    >
    > If there are no mount points in the discovery directory, no PV is created and the output is empty.

For more information, refer to the [Kubernetes local storage](https://kubernetes.io/docs/concepts/storage/volumes/#local) and [local-static-provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner#overview) documents.

#### Offline deployment

The steps for offline deployment are the same as for online deployment, except for the following:

* Download the `local-volume-provisioner.yaml` file on a machine with Internet access, then upload it to the server and install it.

* The `local-volume-provisioner` is a DaemonSet that starts a Pod on every Kubernetes worker node. The Pod uses the `quay.io/external_storage/local-volume-provisioner:v2.5.0` image. If the server does not have access to the Internet, download this Docker image on a machine with Internet access:

    ``` shell
    docker pull quay.io/external_storage/local-volume-provisioner:v2.5.0
    docker save -o local-volume-provisioner-v2.5.0.tar quay.io/external_storage/local-volume-provisioner:v2.5.0
    ```

    Copy the `local-volume-provisioner-v2.5.0.tar` file to the server, and execute the `docker load` command to load the file on the server:

    ```shell
    docker load -i local-volume-provisioner-v2.5.0.tar
    ```

### Best practices

- The unique identifier for a local PV is its path. To avoid conflicts, it is recommended to generate a unique path using the UUID of the device.
- To ensure I/O isolation, it is recommended to use a dedicated physical disk per PV for hardware-based isolation.
- For capacity isolation, it is recommended to use either a partition per PV or a physical disk per PV.

For more information on local PV on Kubernetes, refer to the [Best Practices](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/docs/best-practices.md) document.

## Data safety

In general, when a PVC is deleted and no longer in use, the PV bound to it is reclaimed and placed in the resource pool for scheduling by the provisioner. To prevent accidental data loss, you can configure the reclaim policy of the `StorageClass` to `Retain` globally or change the reclaim policy of a single PV to `Retain`. With the `Retain` policy, a PV is not automatically reclaimed.

- To configure globally:

    The reclaim policy of a `StorageClass` is set at creation time and cannot be updated once created. If it is not set during creation, you can create another `StorageClass` with the same provisioner. For example, the default reclaim policy of the `StorageClass` for persistent disks on Google Kubernetes Engine (GKE) is `Delete`. You can create another `StorageClass` named `pd-standard` with a reclaim policy of `Retain` and change the `storageClassName` of the corresponding component to `pd-standard` when creating a TiDB cluster.

    ```yaml
    apiVersion: storage.k8s.io/v1
    kind: StorageClass
    metadata:
      name: pd-standard
    parameters:
       type: pd-standard
    provisioner: kubernetes.io/gce-pd
    reclaimPolicy: Retain
    volumeBindingMode: Immediate
    ```

- To configure a single PV:

    ```shell
    kubectl patch pv ${pv_name} -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
    ```

> **Note:**
>
> By default, to ensure data safety, TiDB Operator automatically changes the reclaim policy of the PVs of PD and TiKV to `Retain`.

### Delete PV and data

When the reclaim policy of PVs is set to `Retain`, if you have confirmed that the data of a PV can be deleted, you can delete the PV and its corresponding data by following these steps:

1. Delete the PVC object corresponding to the PV:

    ```shell
    kubectl delete pvc ${pvc_name} --namespace=${namespace}
    ```

2. Set the reclaim policy of the PV to `Delete`. This automatically deletes and reclaims the PV.

    ```shell
    kubectl patch pv ${pv_name} -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
    ```

For more details, refer to the [Change the Reclaim Policy of a PersistentVolume](https://kubernetes.io/docs/tasks/administer-cluster/change-pv-reclaim-policy/) document.
