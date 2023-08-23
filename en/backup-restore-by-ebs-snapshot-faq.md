---
title: FAQs on EBS Snapshot Backup and Restore across Multiple Kubernetes
summary: Learn about the common questions and solutions for EBS snapshot backup and restore across multiple Kubernetes.
---

# FAQs on EBS Snapshot Backup and Restore across Multiple Kubernetes

## New tags on snapshots and restored volumes

Symptom: Some tags are automatically added to generated snapshots and restored EBS volumes

Explanation: Those new tags are added for traceability. Snapshots will inherit all tags from individual source EBS volumes, and restored EBS volumes inherit tags from source snapshots but prefix keys with `snapshot\`. Besides that, new tags like <TiDBCluster-BR: true>, <snapshot/createdFromSnapshotId, {source-snapshot-id}> are added to restored EBS volumes.

## Backup Initialize Failed 

Symptom: You get the error that contains `GC safepoint 443455494791364608 exceed TS 0` when backup are initializing.

Solution: Probably you have forbidden the feature of "resolved ts" in TiKV or PD, so you should check the configuration of TiKV and PD.
For TiKV configuration, confirm if you set `resolved-ts.enable = false` or `raftstore.report-min-resolved-ts-interval = "0s"`. If you set, please remove the configuration.
For PD configuration, confirm if you set `pd-server.min-resolved-ts-persistence-interval = "0s"`. If you set, please remove the configuration.

## Backup failed due to execution twice

**Issue:** [#5143](https://github.com/pingcap/tidb-operator/issues/5143)

Symptom: You get the error that contains `backup meta file exists`, and you can find the backup pod is scheduled twice.

Solution: Probably the first backup pod is evicted by Kubernetes due to node resource pressure. You can configure `PriorityClass` and `ResourceRequirements` to reduce the possibility of eviction. Please refer to the [comment of issue](https://github.com/pingcap/tidb-operator/issues/5143#issuecomment-1654916830).

## Save time for backup by controlling snapshot size calculation level

Symptom: Scheduled backup can't be finished in expected window due to the cost of snapshot size calculation.

Solution: By default, both full size and incremental size are calculated by calling AWS service. And the calculation might cost minutes of time. You can set `spec.template.calcSizeLevel` to `full` to skip incremental size calculation, set the value to `incremental` to skip full size calculation, and set the value to `none` to skip both.
