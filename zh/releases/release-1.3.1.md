---
title: TiDB Operator 1.3.0 Release Notes
---

# TiDB Operator 1.3.0 Release Notes

发布日期: 2022 年 2 月 15 日

TiDB Operator 版本：1.3.0

## 兼容性改动

- 由于 [#4434](https://github.com/pingcap/tidb-operator/pull/4434) 和 [#4435](https://github.com/pingcap/tidb-operator/pull/4435) 的问题，如果已经使用 v1.3.0 和 v1.3.0-beta.1 版本 TiDB Operator 部署了 v5.4.0 及以后版本的 TiFlash，你需要执行以下步骤来升级 Operator，以防止 TiFlash 丢失数据：

    1. 如果 TidbCluster 定义中未配置 TiFlash 配置中的 `storage.raft.dir` 和 `raft.kvstore_path` 字段，则添加 `storage.raft.dir` 字段。
        
        ```yaml
        spec:
          # ...
          tiflash:
            config:
              config: |
                # ...
                [storage]
                  [storage.raft]
                    dir = ["/data0/db/kvstore/"]
        ```

        配置后，等待 TiFlash 会滚动重建结束。
        
    2. 升级 TiDB Operator

## 新功能

- 添加新的 `spec.dnsPolicy` 字段，以支持配置 Pod 的 DNSPolicy ([#4420](https://github.com/pingcap/tidb-operator/pull/4420), [@handlerww](https://github.com/handlerww))

## Bug 修复

- 修复当没有手动设置 TiFlash 配置 `raft.kvstore_path` 或 `storage.raft.dir` 字段的情况下，使用 v1.3.0 和 v1.3.0-beta.1 版本 Operator 升级旧版本 TiFlash 到 v5.4.0 及以后版本后，TiFlash 会丢失数据的问题 ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))

- 修复不配置 TiFlash 配置 `tmp_path` 字段无法使用 TiFlash 的问题 ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))
