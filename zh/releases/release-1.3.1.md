---
title: TiDB Operator 1.3.1 Release Notes
---

# TiDB Operator 1.3.1 Release Notes

发布日期: 2022 年 2 月 24 日

TiDB Operator 版本：1.3.1

## 兼容性改动

- 由于 [#4434](https://github.com/pingcap/tidb-operator/pull/4434) 和 [#4435](https://github.com/pingcap/tidb-operator/pull/4435) 的问题，如果已经使用 v1.3.0 或者 v1.3.0-beta.1 版本 TiDB Operator 部署了 v5.4.0 及以后版本的 TiFlash，你需要执行以下步骤来升级 TiDB Operator，以防止 TiFlash **丢失元数据**：

    1. 如果 TidbCluster 定义中**没有显式**配置 TiFlash 配置 `spec.tiflash.config.config` 中的 `storage.raft.dir` 和 `raft.kvstore_path` 字段，则显式添加 `storage.raft.dir` 字段。如果 `storage.main.dir` 没有显式配置，也需要显式添加。
        
        ```yaml
        spec:
          # ...
          tiflash:
            config:
              config: |
                # ...
                [storage]
                  [storage.main]
                    dir = ["/data0/db"]
                  [storage.raft]
                    dir = ["/data0/db/kvstore/"]
        ```

        配置后，等待 TiFlash 滚动更新结束。
        
    2. 升级 TiDB Operator。

## 新功能

- 添加新的 `spec.dnsPolicy` 字段，以支持配置 Pod 的 DNSPolicy ([#4420](https://github.com/pingcap/tidb-operator/pull/4420), [@handlerww](https://github.com/handlerww))

## 优化提升

- `tidb-lightning` Helm chart 使用 `local` 后端作为默认后端 ([#4426](https://github.com/pingcap/tidb-operator/pull/4426), [@KanShiori](https://github.com/KanShiori))

## Bug 修复

- 修复当没有显式设置 TiFlash 配置 `raft.kvstore_path` 或 `storage.raft.dir` 字段的情况下，使用 v1.3.0 或者 v1.3.0-beta.1 版本 TiDB Operator 升级 TiFlash 到 v5.4.0 及以后版本后，TiFlash 丢失元数据的问题 ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))

- 修复 TiFlash 配置中缺少 `tmp_path` 字段时，使用 v1.3.0 或者 v1.3.0-beta.1 版本 TiDB Operator 无法使用 TiFlash v5.4.0 及以后版本的问题 ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))
