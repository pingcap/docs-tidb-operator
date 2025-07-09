---
title: TiDB Operator v2 和 v1 的对比
summary: 介绍 TiDB Operator v2 与 v1 的主要差异。
---

# TiDB Operator v2 和 v1 的对比

由于 Kubernetes 和 TiDB 生态的快速发展，TiDB Operator v1 现有的架构和实现遇到了一些挑战。为了更好地适配 Kubernetes 和 TiDB 生态，TiDB Operator v2 对 TiDB Operator v1 进行了大幅重构。

## TiDB Operator v2 的核心变更

### 拆分 `TidbCluster` CRD

最初 TiDB 集群只有 3 个核心组件：PD、TiKV、TiDB。为了尽可能简化部署，降低用户心智负担，最初的设计将所有 TiDB 集群的组件定义在了同一个 CRD `TidbCluster` 中。然而，随着 TiDB 的发展，这种设计迎来了一些挑战。

- TiDB 集群的组件不断增加，目前已经有 8 个组件定义在 `TidbCluster` CRD 中
- 为了实现状态展示，所有节点的状态都定义在了 `TidbCluster` CRD 中
- 缺乏原生对异构集群对支持，只能通过引入额外的 `TidbCluster` CR 实现异构集群
- 无法支持 `/scale` API，无法与 Kubernetes 的 [HorizontalPodAutoscaler (HPA)](https://kubernetes.io/zh-cn/docs/tasks/run-application/horizontal-pod-autoscale/) 生态集成
- 一个巨大的 CR/CRD 可能带来难以解决的性能问题

为解决上述问题，TiDB Operator v2 将 `TidbCluster` CRD 按组件拆分为多个独立的 CRD。

### 移除 StatefulSet 依赖，直接管理 Pod

由于 TiDB 集群本身的复杂性，Kubernetes 原生的 Deployment 和 StatefulSet 控制器无法完美适配 TiDB 的部署和运维需求。TiDB Operator v1 通过 StatefulSet 管理所有 TiDB 组件，然而 StatefulSet 的一些限制无法最大化 Kubernetes 能够提供的能力，比如：

- StatefulSet 限制了 `VolumeClaimTemplate` 的修改，无法原生支持扩容
- StatefulSet 限制了缩容和滚动更新的顺序，导致 leader 的反复调度
- StatefulSet 限制了同一个控制器下的 Pod 配置必须相同，不得不通过复杂的启动脚本来差异化同一组 Pod 的启动参数
- 没有 API 提供 Raft member 的定义，导致重启 Pod 和移除 Raft member 的语义冲突，没有直观的方法可以移除某一个 TiKV 节点

TiDB Operator v2 移除了对 StatefulSet 的依赖，并引入了以下 CRD：

- `Cluster`
- `ComponentGroup`
- `Instance`

这三层 CRD 可以直接管理 Pod。TiDB Operator v2 通过 `ComponentGroup` CRD 来管理具有共同特性的节点，降低复杂度，通过 `Instance` CRD 来方便对单个有状态实例进行管理，提供实例级别的运维操作，保证了灵活性。

这带来了如下好处：

- 能够更好的支持 Volume 的变更
- 能够支持更合理的滚动更新顺序，比如最后重启 leader，防止 leader 的反复迁移
- 能够支持非核心组件（例如 log tail 和 istio）的原地升级，降低 TiDB Operator 升级以及 infra 变更对 TiDB 集群的影响
- 能够通过 `kubectl delete ${pod}` 优雅重启 Pod，也能通过 `kubectl delete ${instance}` 重建特定的 TiKV 节点
- 更加直观的状态展示

### 引入 Overlay 机制，不再直接管理 TiDB 无关的 Kubernetes 字段

每个 Kubernetes 的新版本都可能会引入一些用户需要的新字段，然而这些字段可能 TiDB Operator 并不关心。TiDB Operator v1 的开发过程中花了大量的时间在支持快速发展的 Kubernetes 的新功能，包括手动在 `TidbCluster` CRD 中添加新字段，并将新字段层层下发。TiDB Operator v2 引入了 Overlay 机制，通过统一的方式支持所有 Kubernetes 资源（尤其是 Pod）上的新字段，详情见 [Overlay](overlay.md)。

### 其他 TiDB Operator v2 的新特性

#### 增强验证能力

TiDB Operator v2 通过合法性检查规则 (Validation Rule) 和验证准入策略 (Validating Admission Policy) 增强配置校验能力，提高了系统的易用性与健壮性。

#### 支持 `/status` 和 `/scale` 子资源

TiDB Operator v2 支持 CRD 子资源，可与 Kubernetes 提供的 HPA 集成，实现自动化扩缩容。

#### 移除 `tidb scheduler` 组件并支持 Evenly Spread Policy

TiDB Operator v2 支持配置 Evenly Spread Policy 来将组件按需均匀分布到不同的 Region 和 Zone 上，并移除了 `tidb scheduler` 组件。

## TiDB Operator v2 暂不支持的组件和功能

### 组件

#### `Binlog` (Pump + Drainer)

`Binlog` 组件已经废弃，详见 [TiDB Binlog 简介](https://docs.pingcap.com/zh/tidb/v8.3/tidb-binlog-overview/)。

#### Dumpling + TiDB Lightning

TiDB Operator 不再提供对 Dumpling 和 TiDB Lightning 的直接支持，建议使用 Kubernetes 原生 Job 的方式运行。

#### `TidbInitializer`

TiDB Operator v2 不再支持 `TidbInitializer` CRD，你可以使用 BootstrapSQL 的方式运行初始化的 SQL。

#### `TidbMonitor`

TiDB Operator v2 不再支持 `TidbMonitor` CRD。由于用户的监控系统通常比较复杂并且方案众多，`TidbMonitor` 往往无法很好地集成到生产级别的监控系统中。TiDB 通过更灵活的方式直接为你提供集成常用监控系统的方案，不再通过 CRD 的方式运行 Prometheus + Grafana + Alert-Manager 的组合。详情请参阅 [TiDB 集群的监控与告警](monitor-a-tidb-cluster.md)。

#### `TidbNgMonitoring`

暂不支持 `TidbNgMonitoring`。

#### `TidbDashboard`

暂不支持通过 CRD 部署 `TidbDashboard`。你可以使用内置的 Dashboard 或者通过 Deployment 自行部署。

### 功能

#### 跨 Namespace 部署

考虑到跨 Namespace 可能带来的安全性问题以及尚不明确的用户场景，暂不支持。

#### 跨 Kubernetes 集群部署

考虑到跨 Kubernetes 集群可能带来的安全性问题以及尚不明确的用户场景，暂不支持。

#### 基于 EBS 卷快照的备份恢复

基于 EBS 卷快照的备份存在以下难以解决的问题：

- **成本过高**：EBS 卷快照的成本非常高。
- **RTO 过长**：从 EBS 卷快照恢复的时间非常长。

随着持续的优化，TiDB BR 的性能提升显著，基于 EBS 卷快照的备份恢复不再是必需的。因此，TiDB Operator v2 不再支持该功能。
