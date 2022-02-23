---
title: TiDB Operator 1.3.1 Release Notes
---

# TiDB Operator 1.3.1 Release Notes

Release date: February 23, 2022

TiDB Operator version: 1.3.1

## Compatibility Change

- Due to issues [#4434](https://github.com/pingcap/tidb-operator/pull/4434) and [#4435](https://github.com/pingcap/tidb-operator/pull/4435), if you have deployed v5.4.0 version or later verion TiFlash when using v1.3.0 version or v1.3.0-beta.1 version TiDB Operator, you have to upgrade TiDB Operator by the following steps to **avoid TiFlash lose metadata**.

    1. If there isn't `storage.rafe.dir` or `raft.kvstore_path` field of TiFlash's config `spec.tiflash.config.config` in TidbCluster spec, you need to add the `storage.raft.dir` field.
    
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
      
    2. Upgrade TiDB Operator.

## New Features

- Add a new field `spec.dnsPolicy` to support configure `DNSPolicy` of Pod ([#4420](https://github.com/pingcap/tidb-operator/pull/4420), [@handlerww](https://github.com/handlerww))

## Improvements

- `tidb-lightning` Helm chart use `Local-backend` as default backend ([#4426](https://github.com/pingcap/tidb-operator/pull/4426), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue that if you don't set `raft.kvstore_path` field or `storage.raft.dir` field in TiFlash's config, TiFlash will lose metadata after upgrading TiFlash to v5.4.0 or later when using v1.3.0 or v1.3.0-beta.1 TiDB Operator ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))

- Fix the issue that can not use TiFlash if there isn't the `tmp_path` field in TiFlash's config ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))
