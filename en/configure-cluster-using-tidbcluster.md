---
title: Configure a TiDB Cluster Using TidbCluster
summary: This document introduces how to use TidbCluster to configure a TiDB cluster.
category: how-to
---

# Configure a TiDB Cluster Using TidbCluster

This document introduces how to configure the parameters of TiDB/TiKV/PD using TidbCluster.

The current TiDB Operator v1.1 supports all parameters of TiDB v3.1. For parameters of different components, refer to [TiDB documentation](https://pingcap.com/docs/).

## Configure TiDB parameters

TiDB parameters can be configured by `TidbCluster.Spec.Tidb.Config`.

For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
....
  tidb:
    image: pingcap.com/tidb:v3.1.0
    imagePullPolicy: IfNotPresent
    replicas: 1
    service:
      type: ClusterIP
    config:
      split-table: true
      oom-action: "log"
    requests:
      cpu: 1
```

For all the configurable parameters of TiDB, refer to [TiDB Configuration File](https://pingcap.com/docs/v3.1/reference/configuration/tidb-server/configuration-file/).

> **Note:**
>
> If you deploy your TiDB cluster using CR, make sure that `Config: {}` is set, no matter you want to modify `config` or not. Otherwise, TiDB components might not be started successfully. This step is meant to be compatible with `Helm` deployment.

## Configure TiKV parameters

TiKV parameters can be configured by `TidbCluster.Spec.Tikv.Config`.

For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
....
  tikv:
    image: pingcap.com/tikv:v3.1.0
    config:
      grpc-concurrenc: 4
      sync-log: true
    replicas: 1
    requests:
      cpu: 2
```

For all the configurable parameters of TiKV, refer to [TiKV Configuration File](https://pingcap.com/docs/v3.1/reference/configuration/tikv-server/configuration-file/).

> **Note:**
>
> If you deploy your TiDB cluster using CR, make sure that `Config: {}` is set, no matter you want to modify `config` or not. Otherwise, TiKV components might not be started successfully. This step is meant to be compatible with `Helm` deployment.

## Configure PD parameters

PD parameters can be configured by `TidbCluster.Spec.Pd.Config`.

For example:

```yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: basic
spec:
.....
  pd:
    image: pingcap.com/pd:v3.1.0
    config:
      format: "format"
      disable-timestamp: false
```

For all the configurable parameters of PD, refer to [PD Configuration File](https://pingcap.com/docs/v3.1/reference/configuration/pd-server/configuration-file/).

> **Note:**
>
> If you deploy your TiDB cluster using CR, make sure that `Config: {}` is set, no matter you want to modify `config` or not. Otherwise, PD components might not be started successfully. This step is meant to be compatible with `Helm` deployment.
