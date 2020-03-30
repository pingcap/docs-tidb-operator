---
title: Advanced StatefulSet Controller
summary: Learn how to enable and use advanced StatefulSet controller.
category: reference
---

# Advanced StatefulSet Controller

**Feature Stage**: Alpha

Kubernetes has a built-in [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) to allocate consecutive serial numbers to Pods. For example, when there are 3 replicas, the Pods are named as pod-0, pod-1, and pod-2. When scaling out or in, you must add or delete pods at the end. For example, when expanding to 4 copies, pod-3 will be added. When shrinking to 2 copies, pod-2 is deleted.

When using local storage, Pods are tied to Nodes storage resources and cannot be freely scheduled. If you want to delete one of the Pods in the middle to maintain its Node but no other Nodes can be migrated, or if you want to delete a Pod if it fails, another Pod with a different serial number cannot be implemented through the built-in StatefulSet.

[Enhanced StatefulSet Controller] (https://github.com/pingcap/advanced-statefulset) Based on the built-in StatefulSet implementation, added the ability to freely control the number of Pods. This article describes how to use it in TiDB Operator.

## On

1. Load the CRD file of the Advanced StatefulSet:

    * Prior to Kubernetes 1.16:

        {{<copyable "shell-regular">}}

        `` `shell
        kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/advanced-statefulset-crd.v1beta1.yaml
        `` `

    * After Kubernetes 1.16:

        {{<copyable "shell-regular">}}

        `` `
        kubectl apply -f https://raw.githubusercontent.com/pingcap/tidb-operator/master/manifests/advanced-statefulset-crd.v1.yaml
        `` `

2. Enable the `AdvancedStatefulSet` feature in` values.yaml` of the TiDB Operator chart:

    {{<copyable "shell-regular">}}

    `` `yaml
    features:
    -AdvancedStatefulSet = true
    advancedStatefulset:
      create: true
    `` `

    Then upgrade TiDB Operator, please refer to [Upgrade TiDB Operator Documentation] (upgrade-TiDB Operator.md).

> ** Note: **
>
> TiDB Operator turns the current StatefulSet object into an AdvancedStatefulSet object by enabling the AdvancedStatefulSet feature. However, TiDB Operator does not support automatic conversion from AdvancedStatefulSet to Kubernetes' built-in StatefulSet object after the AdvancedStatefulSet feature is turned off.
## use
### View AdvancedStatefulSet Objects via kubectl
The data format of `AdvancedStatefulSet` is exactly the same as` StatefulSet`, but it is implemented in CRD. The alias is `asts`. You can view the objects in the command space through the following methods.
{{<copyable "shell-regular">}}
`` `shell
kubectl get -n <namespace> asts
`` `
### Manipulating TidbCluster objects to specify pods to scale down

When using the enhanced StatefulSet, when scaling TidbCluster, in addition to reducing the number of copies, you can also specify the scaling of any Pod under the PD, TiDB, or TiKV component by configuring annotations.

such as:

{{<copyable "">}}

`` `yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  name: asts
spec:
  version: v3.0.12
  timezone: UTC
  pvReclaimPolicy: Delete
  pd:
    baseImage: pingcap / pd
    replicas: 3
    requests:
      storage: "1Gi"
    config: {}
  tikv:
    baseImage: pingcap / tikv
    replicas: 4
    requests:
      storage: "1Gi"
    config: {}
  tidb:
    baseImage: pingcap / tidb
    replicas: 2
    service:
      type: ClusterIP
    config: {}
`` `

The above configuration will deploy 4 TiKV instances, namely basic-tikv-0, basic-tikv-1, ..., basic-tikv-3. If you want to reduce basic-tikv-1, you need to modify `spec.tikv.replicas` to 3 and configure the following annotations:

{{<copyable "">}}

`` `yaml
metadata:
  annotations:
    tikv.tidb.pingcap.com/delete-slots: '[1]'
`` `

> ** Note: **
>
> Modification of `replicas` and` delete slot annotation` must be completed in the same operation, otherwise the controller will operate according to the general expectations of the modification.
The complete example is as follows:

{{<copyable "">}}

`` `yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  annotations:
    tikv.tidb.pingcap.com/delete-slots: '[1]'
  name: asts
spec:
  version: v3.0.12
  timezone: UTC
  pvReclaimPolicy: Delete
  pd:
    baseImage: pingcap / pd
    replicas: 3
    requests:
      storage: "1Gi"
    config: {}
  tikv:
    baseImage: pingcap / tikv
    replicas: 3
    requests:
      storage: "1Gi"
    config: {}
  tidb:
    baseImage: pingcap / tidb
    replicas: 2
    service:
      type: ClusterIP
    config: {}
`` `

The supported annotations are:

-`pd.tidb.pingcap.com / delete-slots`: Specify the serial numbers of the pods to be deleted by the PD component.
-`tidb.tidb.pingcap.com / delete-slots`: Specify the serial number of the pods that the TiDB component needs to be deleted.
-`tikv.tidb.pingcap.com / delete-slots`: Specify the serial number of the pods that the TiKV component needs to be deleted.

The Annotation value is an integer array of JSON, such as `[0]`, `[0,1]`, `[1,3]`, etc.

### Operate TidbCluster objects to expand capacity at specified locations

Reverse the previous reduction to restore pod-1.

> ** Note: **
>
> Same as regular StatefulSet scaling, it does not actively delete the PVC associated with the Pod. If you want to avoid using the previous data and expand the capacity at the original location, you need to actively delete the associated PVC.
Examples are as follows:

{{<copyable "">}}

`` `yaml
apiVersion: pingcap.com/v1alpha1
kind: TidbCluster
metadata:
  annotations:
    tikv.tidb.pingcap.com/delete-slots: '[]'
  name: asts
spec:
  version: v3.0.12
  timezone: UTC
  pvReclaimPolicy: Delete
  pd:
    baseImage: pingcap / pd
    replicas: 3
    requests:
      storage: "1Gi"
    config: {}
  tikv:
    baseImage: pingcap / tikv
    replicas: 4
    requests:
      storage: "1Gi"
    config: {}
  tidb:
    baseImage: pingcap / tidb
    replicas: 2
    service:
      type: ClusterIP
    config: {}
`` `

The delete slots annotations can be left blank or deleted completely.