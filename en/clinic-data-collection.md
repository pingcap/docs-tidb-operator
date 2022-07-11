---
title: PingCAP Clinic Diagnostic Data
summary: Learn what diagnostic data can be collected by PingCAP Clinic Diagnostic Service on a TiDB cluster deployed using TiDB Operator.
---

# PingCAP Clinic Diagnostic Data

PingCAP Clinic Diagnostic Service (PingCAP Clinic) collects diagnostic data from TiDB clusters that are deployed using TiDB Operator. This document lists the types of data collected and their corresponding parameters.

When you [collect data using Diag client (Diag)](clinic-user-guide.md), you can add the required parameters to the command according to your needs.

The diagnostic data collected by PingCAP Clinic is **only** used for troubleshooting cluster problems.

Clinic Server is a diagnostic service deployed in the cloud. There are two independent services based on different storage locations:

- [Clinic Server in Chinese mainland](https://clinic.pingcap.com.cn): If you upload the collected data to Clinic Server in Chinese mainland, the data will be stored in the Amazon S3 set up by PingCAP in AWS China (Beijing). PingCAP strictly controls permissions for data and only allows authorized internal technical support staff to access the data.
- [Clinic Server in US](https://clinic.pingcap.com): If you upload the collected data to Clinic Server in US, the data will be stored in the Amazon S3 set up by PingCAP in AWS US. PingCAP strictly controls permissions for data and only allows authorized internal technical support staff to access the data.

## TiDB cluster information

| Data type | Exported file | Parameter for PingCAP Clinic |
| :------ | :------ |:-------- |
| Basic information of the cluster, including the cluster ID | `cluster.json` | The data is collected per run by default. |
| Detailed information of the cluster | `tidbcluster.json` | The data is collected per run by default. |

## TiDB diagnostic data

| Data type | Exported file | Parameter for PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` | `collectors:config` |

## TiKV diagnostic data

| Data type | Exported file | Parameter for PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` | `collectors:config` |

## PD diagnostic data

| Data type | Exported file | Parameter for PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` |`collectors:config` |
| Outputs of the command `tiup ctl pd -u http://${pd IP}:${PORT} store` | `store.json` | `collectors:config` |
| Outputs of the command `tiup ctl pd -u http://${pd IP}:${PORT} config placement-rules show` | `placement-rule.json` | `collectors:config` |

## TiFlash diagnostic data

| Data type | Exported file | Parameter for PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` |`collectors:config` |

## TiCDC diagnostic data

| Data type | Exported file | Parameter for PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` |`collectors:config` |
| Debug data | `info.txt`, `status.txt`, `changefeeds.txt`, `captures.txt`, `processors.txt` | `collectors:debug` (Diag does not collect this data type by default)  |

## Prometheus monitoring data

| Data type | Exported file | Parameter for PingCAP Clinic |
| :------ | :------ |:-------- |
| All Metrics data | `{metric_name}.json` | `collectors:monitor` |
| Alert configuration | `alerts.json` | `collectors:monitor` |
