---
title: 在 GCP GKE 上部署 TiDB 集群
summary: 了解如何在 GCP GKE 上部署 TiDB 集群。
aliases: ['/docs-cn/tidb-in-kubernetes/dev/deploy-on-gcp-gke/']
---

# 在 GCP GKE 上部署 TiDB 集群

<!-- markdownlint-disable MD029 -->

本文介绍了如何在 GCP GKE 上部署 TiDB 集群。

> **警告：**
>
> 当前多磁盘聚合功能[存在一些已知问题](https://github.com/pingcap/tidb-operator/issues/684)，不建议在生产环境中每节点配置一块以上磁盘。我们正在修复此问题。

## 环境准备

部署前，请确认已安装以下软件：

* [helm](https://helm.sh/docs/intro/install/) 用于安装 TiDB Operator
* [gcloud](https://cloud.google.com/sdk/gcloud) 用于命令行下创造和管理 GCP 服务
* 完成 [GKE 快速入门](https://cloud.google.com/kubernetes-engine/docs/quickstart) 中"准备工作"

该教程包含以下内容：

* 启用 Kubernetes API
* 配置足够的配额等

### 创建 GKE 集群
### 创建 GKE 集群
