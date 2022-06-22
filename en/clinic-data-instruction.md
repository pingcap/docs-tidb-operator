---
title: PingCAP Clinic Diagnostic Data
summary: Learn what diagnostic data can be collected by PingCAP Clinic Diagnostic Service on a TiDB cluster deployed by TiDB Operator.
---

# PingCAP Clinic Diagnostic Data

This document provides the types of diagnostic data that can be collected by PingCAP Clinic Diagnostic Service (PingCAP Clinic) from the TiDB clusters deployed using TiDB Operator. Also, the document lists the parameters for data collection corresponding to each data type. When running a command to [collect data using Diag client (Diag)](clinic-user-guide.md), you can add the required parameters to the command according to the types of data to be collected.

The diagnostic data collected by PingCAP Clinic is **only** used for troubleshooting cluster problems.

Clinic Server is a diagnostic service deployed in the cloud. Currently, you can upload the collected diagnostic data to Clinic Server China only. The uploaded data is stored in the AWS S3 China (Beijing) region server set up by PingCAP. PingCAP strictly controls permissions for data access and only allows authorized in-house technical support staff to access the uploaded data.

## TiDB cluster information

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Basic information of the cluster, including the cluster ID | `cluster.json` | The data is collected per run by default. |
| Detailed information of the cluster | `tidbcluster.json` | The data is collected per run by default. |

## TiDB diagnostic data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` | `collectors:config` |

## TiKV diagnostic data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` | `collectors:config` |

## PD diagnostic data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` |`collectors:config` |
| Outputs of the command `tiup ctl pd -u http://${pd IP}:${PORT} store` | `store.json` | `collectors:config` |
| Outputs of the command `tiup ctl pd -u http://${pd IP}:${PORT} config placement-rules show` | `placement-rule.json` | `collectors:config` |

## TiFlash diagnostic data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` |`collectors:config` |

## TiCDC diagnostic data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| Real-time configuration | `config.json` |`collectors:config` |
| Debug data | `info.txt`, `status.txt`, `changefeeds.txt`, `captures.txt`, `processors.txt` | `collectors:debug` (Diag does not collect this data type by default)  |

## Prometheus monitoring data

| Data type | Exported file | Parameter for data collection by PingCAP Clinic |
| :------ | :------ |:-------- |
| All Metrics data | `{metric_name}.json` | `collectors:monitor` |
| Alert configuration | `alerts.json` | `collectors:monitor` |
