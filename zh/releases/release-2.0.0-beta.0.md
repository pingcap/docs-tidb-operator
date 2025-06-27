---
title: TiDB Operator 2.0.0-beta.0 Release Notes
summary: TiDB Operator 2.0.0-beta.0 版本发布。v2 版本对 v1.x 版本进行了大幅重构，主要改动包括将 `TidbCluster` 拆分为多个 CRD、移除对 StatefulSet 的依赖，并引入 Overlay 功能以实现更灵活的自定义配置。
---

# TiDB Operator 2.0.0-beta.0 Release Notes

发布日期：2025 年 7 月 x 日

TiDB Operator 版本：2.0.0-beta.0

随着 TiDB 和 Kubernetes 生态的快速发展，TiDB Operator 发布了与 v1 不兼容的 v2 版本。关于 v2 与 v1 的详细差异，请参考 [TiDB Operator v2 与 v1 版本对比](tidb-operator-v2-vs-v1.md)。

## 新功能

- 将 `TidbCluster` CRD 拆分为多个 CRD，提升了可维护性和管理效率。
- 移除对 StatefulSet 的依赖，改为直接管理 Pod，增强了扩缩容的灵活性。
- 支持 [Overlay](overlay.md) 功能，你无需修改 TiDB Operator 源代码，就可以自定义 Kubernetes 集群中原生资源的配置。
- 支持拓扑感知调度，确保 Pod 在拓扑域（如可用区 `zone`）中均匀分布。
- 通过[合法性检查规则 (Validation Rule)](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) 和[验证准入策略 (Validating Admission Policy)](https://kubernetes.io/zh-cn/docs/reference/access-authn-authz/validating-admission-policy/)，增强了 CRD 字段的校验能力，提高了系统的易用性与健壮性。
- 支持 [CRD 子资源](https://kubernetes.io/zh-cn/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#subresources)，可与 Kubernetes 提供的 [HorizontalPodAutoscaler (HPA)](https://kubernetes.io/zh-cn/docs/tasks/run-application/horizontal-pod-autoscale/) 集成，实现自动化扩缩容。