---
title: TiDB Operator 2.0 Beta.0 Release Notes
summary: TiDB Operator 2.0 Beta.0 版本发布，它是对 1.0 版本的一次大幅重构，主要变化包括将 `TidbCluster` 拆分为多个 CRD，移除 StatefulSet 依赖，并提供 `Overlay` 字段以实现更灵活的定制等。
---

# TiDB Operator 2.0 Beta.0 Release Notes

发布日期：2025 年 7 月

TiDB Operator 版本: 2.0.0-beta.0

## 重大变化

- 将 `TidbCluster` CRD 拆分成了多个 CRD，提高了可维护性和管理性。
- 移除了对 StatefulSet 依赖，改成直接管理 Pod，获得了更大的灵活性。
- 提供了 `Overlay` 字段，允许用户在不修改源码的情况下，灵活地为 Pod 指定 Kubernetes 支持的所有字段。
- 实现了拓扑感知调度，确保 Pod 在拓扑域（如可用区 `zone`）中均匀分布。
- 通过[合法性检查规则 (Validation Rule)](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) 和[验证准入策略 (Validating Admission Policy)](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/validating-admission-policy/) 增强 CRD 字段校验能力，提高了系统的易用性与健壮性。
- 支持 [CRD 子资源](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#subresources)，可与 Kubernetes 提供的 [HorizontalPodAutoscaler (HPA)](https://kubernetes.io/zh-cn/docs/tasks/run-application/horizontal-pod-autoscale/) 集成，实现自动化扩缩容。