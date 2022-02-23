---
title: TiDB Operator 1.3.1 Release Notes
---

# TiDB Operator 1.3.1 Release Notes

Release date: February 23, 2022

TiDB Operator version: 1.3.1

## Compatibility Change

- Due to the issues in [#4434](https://github.com/pingcap/tidb-operator/pull/4434) and [#4435](https://github.com/pingcap/tidb-operator/pull/4435), if you have deployed TiFlash v5.4.0 or later versions when using TiDB Operator v1.3.0 or v1.3.0-beta.1, you must upgrade TiDB Operator by taking the following steps to **avoid TiFlash losing metadata**.

    1. In TidbCluster spec, if the `storage.rafe.dir` and `raft.kvstore_path` fields in TiFlash's config `spec.tiflash.config.config` are not explicitly configured, you need to add the `storage.raft.dir` field.
    
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

## New Feature

- Add a new field `spec.dnsPolicy` to support configuring `DNSPolicy` for Pods ([#4420](https://github.com/pingcap/tidb-operator/pull/4420), [@handlerww](https://github.com/handlerww))

## Improvement

- `tidb-lightning` Helm chart uses `local` backend as the default backend ([#4426](https://github.com/pingcap/tidb-operator/pull/4426), [@KanShiori](https://github.com/KanShiori))

## Bug fixes

- Fix the issue that if the `raft.kvstore_path` field or the `storage.raft.dir` field is not set in TiFlash's config, TiFlash will lose metadata after upgrading TiFlash to v5.4.0 or later versions when using TiDB Operator v1.3.0 or v1.3.0-beta.1 ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))

- Fix the issue that TiFlash v5.4.0 or later versions does not work if the `tmp_path` field is not set in TiFlash's config when using TiDB Operator v1.3.0 or v1.3.0-beta.1 ([#4430](https://github.com/pingcap/tidb-operator/pull/4430), [@KanShiori](https://github.com/KanShiori))
