---
title: TiDB Operator 1.1.6 Release Notes
---

# TiDB Operator 1.1.6 Release Notes

发布日期：2020 年 10 月 16 日

TiDB Operator 版本：1.1.6

## 新功能

- 添加 `spec.br.options` 支持 Backup 跟 Restore CR 自定义 BR 命令行参数 ([#3360](https://github.com/pingcap/tidb-operator/pull/3360), [@lichunzhu](https://github.com/lichunzhu))
- 添加 `spec.tikv.evictLeaderTimeout` 支持配置 tikv evict leader 超时时间 ([#3344](https://github.com/pingcap/tidb-operator/pull/3344), [@lichunzhu](https://github.com/lichunzhu))
- TLS 没开启时支持使用一个 TidbMonitor 监控多个 TiDB clusters.  TidbMonitor CR 添加`spec.clusterScoped` ，监控多个集群时需要设置为 `true` ([#3308](https://github.com/pingcap/tidb-operator/pull/3308), [@mikechengwei](https://github.com/mikechengwei))
- 所有 initcontainers 支持配置 `spec.helper.requests` and  `spec.helper.limits`  ([#3305](https://github.com/pingcap/tidb-operator/pull/3305), [@shonge](https://github.com/shonge))

## 优化提升

- 支持透传 tiflash 的 toml 格式配置 ([#3355](https://github.com/pingcap/tidb-operator/pull/3355), [@july2993](https://github.com/july2993))
- 支持透传 tikv/pd 的 toml 格式配置 ([#3342](https://github.com/pingcap/tidb-operator/pull/3342), [@july2993](https://github.com/july2993))
- 支持透传 tidb 的 toml 格式配置 ([#3327](https://github.com/pingcap/tidb-operator/pull/3327), [@july2993](https://github.com/july2993))
- 支持透传 pump 的 toml 格式配置 ([#3312](https://github.com/pingcap/tidb-operator/pull/3312), [@july2993](https://github.com/july2993))
- TiFlash proxy 的日志输出到 stdout ([#3345](https://github.com/pingcap/tidb-operator/pull/3345), [@lichunzhu](https://github.com/lichunzhu))
- 定时备份到 GCS 时目录名称添加相应备份时间  ([#3340](https://github.com/pingcap/tidb-operator/pull/3340), [@lichunzhu](https://github.com/lichunzhu))
- 删除 apiserver 跟相关的 packages ([#3298](https://github.com/pingcap/tidb-operator/pull/3298), [@lonng](https://github.com/lonng))
- 删除 PodRestarter controller 相关的支持 ([#3296](https://github.com/pingcap/tidb-operator/pull/3296), [@lonng](https://github.com/lonng))

## Bug 修复

- 修复 discovery 可能导致启动多个 pd cluster 的 bug ([#3365](https://github.com/pingcap/tidb-operator/pull/3365), [@lichunzhu](https://github.com/lichunzhu))
