---
title: FAQs on EBS Snapshot Backup and Restore across Multiple Kubernetes
summary: Learn about the common questions and solutions for EBS snapshot backup and restore across multiple Kubernetes.
---

# FAQs on EBS Snapshot Backup and Restore across Multiple Kubernetes

This document addresses common questions and solutions related to EBS snapshot backup and restore across multiple Kubernetes environments.

## New tags on snapshots and restored volumes

**Symptom:** Some tags are automatically added to generated snapshots and restored EBS volumes

**Explanation:** The new tags are added for traceability. Snapshots inherit all tags from the individual source EBS volumes, while restored EBS volumes inherit tags from the source snapshots but prefix keys with `snapshot\`. Additionally, new tags such as `<TiDBCluster-BR: true>`, `<snapshot/createdFromSnapshotId, {source-snapshot-id}>` are added to restored EBS volumes.

## Backup Initialize Failed 

**Symptom:** You get the error that contains `GC safepoint 443455494791364608 exceed TS 0` when the backup is initializing.

**Solution:** This issue might occur if you have disabled the feature of "resolved ts" in TiKV or PD. Check the configuration of TiKV and PD:

- For TiKV, confirm if you set `resolved-ts.enable = false` or `raftstore.report-min-resolved-ts-interval = "0s"`. If so, remove these configurations.
- For PD, confirm if you set `pd-server.min-resolved-ts-persistence-interval = "0s"`. If so, remove this configuration.

## Backup failed due to execution twice

**Issue:** [#5143](https://github.com/pingcap/tidb-operator/issues/5143)

**Symptom:** You get the error that contains `backup meta file exists`, and the backup pod is scheduled twice.

**Solution:** This issue might occur if the first backup pod is evicted by Kubernetes due to node resource pressure. You can configure `PriorityClass` and `ResourceRequirements` to reduce the possibility of eviction. For more details, refer to the [comment of issue](https://github.com/pingcap/tidb-operator/issues/5143#issuecomment-1654916830).

## Save time for backup by controlling snapshot size calculation level

**Symptom:** Scheduled backup can't be completed in the expected window due to the cost of snapshot size calculation.

**Solution:** By default, both full size and incremental size are calculated by calling the AWS service, which might take several minutes. You can set `spec.template.calcSizeLevel` to `full` to skip incremental size calculation, set it to `incremental` to skip full size calculation, and set it to `none` to skip both calculations.
