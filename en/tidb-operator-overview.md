---
title: TiDB Operator Overview
summary: Learn the overview of TiDB Operator.
---

# TiDB Operator Overview

[TiDB Operator](https://github.com/pingcap/tidb-operator) is an automated operating system for TiDB clusters on Kubernetes. It provides a full management life-cycle for TiDB including deployment, upgrades, scaling, backup, fail-over, and configuration changes. With TiDB Operator, TiDB can run seamlessly in the Kubernetes clusters deployed on a public cloud or in a self-managed environment.

## Compatibility between TiDB Operator and TiDB

The corresponding relationship between TiDB Operator and TiDB versions is as follows:

| TiDB versions | Compatible TiDB Operator versions |
|:---|:---|
| dev               | dev                 |
| TiDB >= 8.0       | 2.0, 1.6 (recommended), 1.5 |
| 7.1 <= TiDB < 8.0 | 1.5 (recommended), 1.4 |
| 6.5 <= TiDB < 7.1 | 1.5, 1.4 (recommended), 1.3     |
| 5.4 <= TiDB < 6.5 | 1.4, 1.3 (recommended)   |
| 5.1 <= TiDB < 5.4 | 1.4, 1.3 (recommended), 1.2 (end of support)      |
| 3.0 <= TiDB < 5.1 | 1.4, 1.3 (recommended), 1.2 (end of support), 1.1 (end of support) |
| 2.1 <= TiDB < v3.0| 1.0 (end of support)       |

## Differences between TiDB Operator v2 and v1

With the rapid development of TiDB and the Kubernetes ecosystem, TiDB Operator releases v2, which is incompatible with v1. For a detailed comparison between v2 and v1, see [Comparison Between TiDB Operator v2 and v1](tidb-operator-v2-vs-v1.md).

## Manage TiDB clusters using TiDB Operator

In Kubernetes environments, you can use TiDB Operator to efficiently deploy and manage TiDB clusters. You can choose from the following deployment methods based on your requirements:

- To quickly deploy TiDB Operator and set up a TiDB cluster in a test environment, see [Get Started with TiDB on Kubernetes](get-started.md).
- To deploy TiDB Operator with custom configurations, see [Deploy TiDB Operator](deploy-tidb-operator.md).

Before deploying in any environment, you can customize TiDB configurations using the following guides:

+ [Configure storage volumes](volume-configuration.md)
+ [Customize pods](overlay.md)

After the deployment is complete, see the following documents to use, operate, and maintain TiDB clusters on Kubernetes:

+ [Deploy a TiDB Cluster](deploy-tidb-cluster.md)
+ [Access a TiDB Cluster](access-tidb.md)
+ [Scale a TiDB Cluster](scale-a-tidb-cluster.md)
+ [View TiDB Logs on Kubernetes](view-logs.md)

When a problem occurs and the cluster needs diagnosis, you can:

+ See [TiDB FAQs on Kubernetes](faq.md) for any available solution;
+ See [Troubleshoot TiDB on Kubernetes](tips.md) to shoot troubles.

Some of TiDB's tools are used differently on Kubernetes. You can see [Tools on Kubernetes](tidb-toolkit.md) to understand how TiDB tools are used on Kubernetes.

Finally, when a new version of TiDB Operator is released, you can refer to [Upgrade TiDB Operator](upgrade-tidb-operator.md) to upgrade to the latest version.
