---
title: TiDB Operator 1.0 Beta.3 Release Notes
---

# TiDB Operator 1.0 Beta.3 Release Notes

Release date: June 6, 2019

TiDB Operator version: 1.0.0-beta.3

## v1.0.0-beta.3 What’s New

### Action Required

- ACTION REQUIRED: `nodeSelectorRequired` was removed from values.yaml.
- ACTION REQUIRED:  Comma-separated values support in `nodeSelector` has been dropped, please use new-added `affinity` field which has a more expressive syntax.

### A lot of stability cases added

- ConfigMap rollout
- One PD replicas
- Stop TiDB Operator itself
- TiDB stable scheduling
- Disaster tolerance and data regions disaster tolerance
- Fix many bugs of stability test

### Features added

- Introduce ConfigMap rollout management. With the feature gate open, configuration file changes will be automatically applied to the cluster via a rolling update. Currently, the `scheduler` and `replication` configurations of PD can not be changed via ConfigMap rollout. You can use `pd-ctl` to change these values instead, see [#487](https://github.com/pingcap/tidb-operator/pull/487) for details.
- Support stable scheduling for pods of TiDB members in tidb-scheduler.
- Support adding additional pod annotations for PD/TiKV/TiDB,  e.g. [fluentbit.io/parser](https://docs.fluentbit.io/manual/filter/kubernetes#kubernetes-annotations).
- Support the affinity feature of k8s which can define the rule of assigning pods to nodes
- Allow pausing during TiDB upgrade

### Documentation improved

- GCP one-command deployment
- Refine user guides
- Improve GKE, AWS, Aliyun guide

### Pass User Acceptance Tests

### Other improvements

- Upgrade default TiDB version to v3.0.0-rc.1
- fix bug in reporting assigned nodes of tidb members
- `tkctl get` can show cpu usage correctly now
- Adhoc backup now appends the start time to the PVC name by default.
- add the privileged option for TiKV pod
- `tkctl upinfo` can show nodeIP podIP port now
- get TS and use it before full backup using mydumper
- Fix capabilities issue for `tkctl debug` command

## Detailed Bug Fixes And Changes

- Add capabilities and privilege mode for debug container ([#537](https://github.com/pingcap/tidb-operator/pull/537))
- docs: note helm versions in deployment docs ([#553](https://github.com/pingcap/tidb-operator/pull/553))
- deploy/aws: split public and private subnets when using existing vpc ([#530](https://github.com/pingcap/tidb-operator/pull/530))
- release v1.0.0-beta.3 ([#557](https://github.com/pingcap/tidb-operator/pull/557))
- Gke terraform upgrade to 0.12 and fix bastion instance zone to be region agnostic ([#554](https://github.com/pingcap/tidb-operator/pull/554))
- get TS and use it before full backup using mydumper ([#534](https://github.com/pingcap/tidb-operator/pull/534))
- Add port podip nodeip to tkctl upinfo ([#538](https://github.com/pingcap/tidb-operator/pull/538))
- fix disaster tolerance of stability test ([#543](https://github.com/pingcap/tidb-operator/pull/543))
- add privileged option for tikv pod template ([#550](https://github.com/pingcap/tidb-operator/pull/550))
- use staticcheck instead of megacheck ([#548](https://github.com/pingcap/tidb-operator/pull/548))
- Refine backup and restore documentation ([#518](https://github.com/pingcap/tidb-operator/pull/518))
- Fix stability tidb pause case ([#542](https://github.com/pingcap/tidb-operator/pull/542))
- Fix tkctl get cpu info rendering ([#536](https://github.com/pingcap/tidb-operator/pull/536))
- Fix aliyun tf output rendering and refine documents ([#511](https://github.com/pingcap/tidb-operator/pull/511))
- make webhook configurable ([#529](https://github.com/pingcap/tidb-operator/pull/529))
- Add pods disaster tolerance and data regions disaster tolerance test cases ([#497](https://github.com/pingcap/tidb-operator/pull/497))
- Remove helm hook annotation for initializer job ([#526](https://github.com/pingcap/tidb-operator/pull/526))
- stability test: Add stable scheduling e2e test case ([#524](https://github.com/pingcap/tidb-operator/pull/524))
- upgrade tidb version in related documentations ([#532](https://github.com/pingcap/tidb-operator/pull/532))
- stable scheduling: fix bug in reporting assigned nodes of tidb members ([#531](https://github.com/pingcap/tidb-operator/pull/531))
- reduce wait time and fix stablity test ([#525](https://github.com/pingcap/tidb-operator/pull/525))
- tidb-operator: fix documentation usability issues in GCP document ([#519](https://github.com/pingcap/tidb-operator/pull/519))
- stability cases added: pd replicas 1 and stop tidb-operator ([#496](https://github.com/pingcap/tidb-operator/pull/496))
- pause-upgrade stability test ([#521](https://github.com/pingcap/tidb-operator/pull/521))
- fix restore script bug ([#510](https://github.com/pingcap/tidb-operator/pull/510))
- stability: retry truncating sst files upon failure ([#484](https://github.com/pingcap/tidb-operator/pull/484))
- upgrade default tidb to v3.0.0-rc.1 ([#520](https://github.com/pingcap/tidb-operator/pull/520))
- add --namespace when create backup secret ([#515](https://github.com/pingcap/tidb-operator/pull/515))
- New stability test case for ConfigMap rollout ([#499](https://github.com/pingcap/tidb-operator/pull/499))
- docs: Fix issues found in Queeny's test ([#507](https://github.com/pingcap/tidb-operator/pull/507))
- Pause rolling-upgrade process of tidb statefulset ([#470](https://github.com/pingcap/tidb-operator/pull/470))
- Gke terraform and guide ([#493](https://github.com/pingcap/tidb-operator/pull/493))
- support the affinity feature of k8s which define the rule of assigning pods to nodes ([#475](https://github.com/pingcap/tidb-operator/pull/475))
- Support adding additional pod annotations for PD/TiKV/TiDB ([#500](https://github.com/pingcap/tidb-operator/pull/500))
- Document about PD configuration issue ([#504](https://github.com/pingcap/tidb-operator/pull/504))
- Refine aliyun and aws cloud tidb configurations ([#492](https://github.com/pingcap/tidb-operator/pull/492))
- tidb-operator: update wording and add note ([#502](https://github.com/pingcap/tidb-operator/pull/502))
- Support stable scheduling for TiDB ([#477](https://github.com/pingcap/tidb-operator/pull/477))
- fix `make lint` ([#495](https://github.com/pingcap/tidb-operator/pull/495))
- Support updating configuraion on the fly ([#479](https://github.com/pingcap/tidb-operator/pull/479))
- docs/aws: update AWS deploy docs after testing ([#491](https://github.com/pingcap/tidb-operator/pull/491))
- add release-note to pull_request_template.md ([#490](https://github.com/pingcap/tidb-operator/pull/490))
- Design proposal of stable scheduling in TiDB ([#466](https://github.com/pingcap/tidb-operator/pull/466))
- Update DinD image to make it possible to configure HTTP proxies ([#485](https://github.com/pingcap/tidb-operator/pull/485))
- readme: fix a broken link ([#489](https://github.com/pingcap/tidb-operator/pull/489))
- Fixed typo ([#483](https://github.com/pingcap/tidb-operator/pull/483))
