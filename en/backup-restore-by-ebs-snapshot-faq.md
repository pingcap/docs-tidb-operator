---
title: FAQs on EBS Snapshot Backup and Restore across Multiple Kubernetes
summary: Learn about the common questions and solutions for EBS snapshot backup and restore across multiple Kubernetes.
---

# FAQs on EBS Snapshot Backup and Restore across Multiple Kubernetes

## Backup Initialize Failed 

Symptom: You get the error that contains `GC safepoint 443455494791364608 exceed TS 0` when backup are initializing.

Solution: Probably you have forbidden the feature of "resolved ts" in TiKV or PD, so you should check the configuration of TiKV and PD.
For TiKV configuration, confirm if you set `resolved-ts.enable = false` or `raftstore.report-min-resolved-ts-interval = "0s"`. If you set, please remove the configuration.
For PD configuration, confirm if you set `pd-server.min-resolved-ts-persistence-interval = "0s"`. If you set, please remove the configuration.

## Backup Failed due to executed twice

Issue: [#5143](https://github.com/pingcap/tidb-operator/issues/5143)

Symptom: You get the error that contains `backup meta file exists`, and you can find the backup pod is scheduled twice.

Solution: Probably the first backup pod is evicted by Kubernetes due to node resource pressure. You can configure `PriorityClass` and `ResourceRequirements` to reduce the possibility of eviction. Please refer to the [comment of issue](https://github.com/pingcap/tidb-operator/issues/5143#issuecomment-1654916830).
