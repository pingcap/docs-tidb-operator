---
title: Architecture of Backup and Restore Based on EBS Volume Snapshots across Multiple Kubernetes
summary: Learn the architecture of backup and restore based on EBS volume snapshots in TiDB cluster deployed across multiple Kubernetes.
---

# Architecture of BR Federation

We support [deploying TiDB clusters across multiple Kubernetes](deploy-tidb-cluster-across-multiple-kubernetes.md). BR Federation is designed to enable back up and restore the TiDB cluster deployed across multiple Kubernetes using EBS snapshots. Since we need to take snapshots of EBS volumes, only the TiDB Operator can access EBS volume information.
But the TiDB Operator can only access the Kubernetes where it's deployed, it means a TiDB Operator can only back up TiKV data within its own Kubernetes. As a result, to complete EBS snapshot backup and restore across multiple Kubernetes, a coordinator role is required, and it is what the BR Federation plays. The overall architecture is as follows:

![BR Federation architecture](/media/br-federation-architecture.png)

In this architecture, BR Federation serves as the control plane, while each Kubernetes where TiDB components are deployed serves as the data plane. The control plane (BR Federation) and the data plane interact with each other through the Kubernetes API Server.
BR Federation orchestrates `Backup` and `Restore` CRs in the data plane to complete backup and restore across multiple Kubernetes.

# Backup Process

## Backup Process in Data Plane

The backup process in the data plane is mainly divided into three phases:

Phase One: Make requests to PD to pause region scheduling and GC. This action suspends TiDB cluster region scheduling and GC to prevent data inconsistencies between TiKV instances at the moment of taking snapshot, because each TiKV instance may take snapshot at different time.
Since TiDB components are interconnected across multiple Kubernetes clusters, this operation affects the entire TiDB cluster and only needs to be executed in one Kubernetes.

Phase Two: Collect meta information such as `TidbCluster` CR and EBS volumes, and then request AWS API to create EBS snapshots. This phase needs to be executed in each Kubernetes.

Phase Three: After EBS snapshots are completed, resume TiDB cluster region scheduling and GC. This operation is required only in the Kubernetes where the Phase One was executed.

![backup process in data plane](/media/volume-backup-process-data-plane.png)

## Backup Orchestration Process

The orchestration process of `Backup` from the control plane to the data plane is as follows:

![backup orchestration process](/media/volume-backup-process-across-multiple-kubernetes-overall.png)

# Restore Process

## Restore Process in Data Plane

The restore process in the data plane is mainly divided into three phases:

Phase One: Call the AWS API to restore the EBS volumes by EBS snapshots based on the backup information. The volumes are then mounted onto the TiKV nodes, and TiKV instances are started in recovery mode. This phase needs to be executed in each Kubernetes.

Phase Two: Using BR restores all raft logs and KV data in TiKV instances to a consistent state, and then makes TiKV instances to exit recovery mode. Since TiKV instances are interconnected across multiple Kubernetes, this operation can restore all TiKV data and only needs to be executed in one Kubernetes.

Phase Three: Restart all TiKV instances to run in normal mode, and start TiDB finally. This phase needs to be executed in each Kubernetes.

![restore process in data plane](/media/volume-restore-process-data-plane.png)

## Restore Orchestration Process

The orchestration process of `Restore` from the control plane to the data plane is as follows:

![restore orchestration process](/media/volume-restore-process-across-multiple-kubernetes-overall.png)
