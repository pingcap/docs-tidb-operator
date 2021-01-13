---
title: 灰度部署 TiDB Operator
summary: 介绍如何灰度部署 TiDB Operator。
aliases:
---
# 灰度部署 TiDB Operator

## 适用场景

1. 灰度升级TiDB-Operator
2. 部署多套TiDB-Operator controller-manager

## Values新增参数

1. appendReleaseSuffix  
说明：自动为资源名称添加后缀，后缀为：xxx-{{ .Release.Name }}，在同一namespace下部署多套Operator时需要开启此参数  
默认值：false  

2. controllerManager.create  
  说明：是否创建controllerManager  
  默认值： true  
3. controllerManager.selector  
  说明：配置controller-manager selector参数，基于tidbcluster label选择管控集群,多个标签之间为and关系。默认为`[]`时会管控所有tidbcluster  
  默认值： []  
  样例：

    ```yaml
    selector:
    - canary-release=v1
    - k1==v1
    - k2!=v2
    ```

4. scheduler.create  
  说明：是否创建tidb-scheduler  
  默认值：true  

## 部署多套Operator步骤

1. 部署第一套Operator

    ```shell
    helm install --name tidb-operator --namespace tidb-admin charts/tidb-operator \
    -f charts/tidb-operator/values.yaml \
    --set-string operatorImage=pingcap/tidb-operator:v1.2-nightly
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    NAME:   tidb-operator
    LAST DEPLOYED: Wed Jan 13 10:28:30 2021
    NAMESPACE: tidb-admin
    STATUS: DEPLOYED

    RESOURCES:
    ==> v1/ClusterRole
    NAME                                   CREATED AT
    tidb-operator:tidb-controller-manager  2021-01-13T02:28:30Z
    tidb-operator:tidb-scheduler           2021-01-13T02:28:30Z

    ==> v1/ClusterRoleBinding
    NAME                                   ROLE                                               AGE
    tidb-operator:kube-scheduler           ClusterRole/system:kube-scheduler                  0s
    tidb-operator:tidb-controller-manager  ClusterRole/tidb-operator:tidb-controller-manager  0s
    tidb-operator:tidb-scheduler           ClusterRole/tidb-operator:tidb-scheduler           0s
    tidb-operator:volume-scheduler         ClusterRole/system:volume-scheduler                0s

    ==> v1/ConfigMap
    NAME                   DATA  AGE
    tidb-scheduler-policy  1     0s

    ==> v1/Deployment
    NAME                     READY  UP-TO-DATE  AVAILABLE  AGE
    tidb-controller-manager  0/1    1           0          0s
    tidb-scheduler           0/1    1           0          0s

    ==> v1/Pod(related)
    NAME                                      READY  STATUS             RESTARTS  AGE
    tidb-controller-manager-59b4c56cff-5h45t  0/1    ContainerCreating  0         0s
    tidb-scheduler-8bf9976fb-x45cr            0/2    ContainerCreating  0         0s

    ==> v1/ServiceAccount
    NAME                     SECRETS  AGE
    tidb-controller-manager  1        0s
    tidb-scheduler           1        0s

    NOTES:
    Make sure tidb-operator components are running:
    kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator
    </code></pre>
    </details>

2. 查看Operator部署情况

    ```shell
    kubectl -n tidb-admin get po
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    NAME                                       READY   STATUS    RESTARTS   AGE
    tidb-controller-manager-59b4c56cff-5h45t   1/1     Running   0          10s
    tidb-scheduler-8bf9976fb-x45cr             2/2     Running   0          10s
    </code></pre>
    </details>

3. 部署TiDBCluster

    ```shell
    kubectl -n tidb-cluster-1 create -f examples/basic/tidb-cluster.yaml
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    kubectl -n tidb-cluster-1 get po
    NAME                               READY   STATUS    RESTARTS   AGE
    basic-discovery-54f9f8bc7c-mm2nh   1/1     Running   0          2m24s
    basic-pd-0                         1/1     Running   0          2m24s
    basic-tidb-0                       2/2     Running   0          99s
    basic-tikv-0                       1/1     Running   0          2m11s
    </code></pre>
    </details>

4. 查看tidb集群部署情况

    ```shell
    kubectl -n tidb-cluster-1 get tc
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    NAME    READY   PD                  STORAGE   READY   DESIRE   TIKV                  STORAGE   READY   DESIRE   TIDB                  READY   DESIRE   AGE
    basic   True    pingcap/pd:v4.0.9   1Gi       1       1        pingcap/tikv:v4.0.9   1Gi       1       1        pingcap/tidb:v4.0.9   1       1        12m
    </code></pre>
    </details>

5. 标记TiDBCluster

    ```
    kubectl -n tidb-cluster-1 label tidbcluster basic canary-release=v1 canary-deployment=true
    ```

6. 配置第一套Operator仅管理标签为`canary-release=v1,canary-deployment=true`的tidbcluster
    配置values.yaml:

    ```yaml
    controllerManager:
        selector:
        - canary-release=v1
        - canary-deployment=true
    ```

    或直接通过`--set`命令：

    ```shell
    helm upgrade tidb-operator . --reuse-values --set controllerManager.selector="{canary-release=v1,canary-deployment=true}"
    ```

7. 验证controller已启动selector

    ```shell
    kubectl  -n tidb-admin get deploy tidb-controller-manager -o yaml
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: tidb-controller-manager
      namespace: tidb-admin
    spec:
      template:
        spec:
          containers:
          - command:
            ...
            - -selector=canary-release=v1,canary-deployment=true
            ...
    </code></pre>
    </details>

8. 查看Operator日志

    ```shell
    kubectl  -n tidb-admin logs tidb-controller-manager-55b887bdc9-lzdwv
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    ...
    I0113 02:50:13.195779       1 main.go:69] FLAG: --selector="canary-release=v1,canary-deployment=true"
    ...
    I0113 02:50:32.409378       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    I0113 02:50:32.773635       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    I0113 02:51:00.294241       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    I0113 02:51:00.680001       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    I0113 02:51:30.306216       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    I0113 02:51:30.686362       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    </code></pre>
    </details>

9. 部署第二套Operator
    配置values.yaml:

    ```yaml
    controllerManager:
        selector:
        - canary-release=v2
        - canary-deployment=true
    appendReleaseSuffix: true
    scheduler:
      create: false
    ```

    或直接通过`--set`命令：

    ```shell
    helm install --name tidb-operator-v2 --namespace tidb-admin charts/tidb-operator \
    -f charts/tidb-operator/values.yaml \
    --set operatorImage=pingcap/tidb-operator:v1.2-nightly \
    --set controllerManager.selector="{canary-release=v2,canary-deployment=true}" \
    --set appendReleaseSuffix=true,scheduler.create=false
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    NAME:   tidb-operator-v2
    LAST DEPLOYED: Wed Jan 13 11:17:27 2021
    NAMESPACE: tidb-admin
    STATUS: DEPLOYED

    RESOURCES:
    ==> v1/ClusterRole
    NAME                                      CREATED AT
    tidb-operator-v2:tidb-controller-manager  2021-01-13T03:17:27Z

    ==> v1/ClusterRoleBinding
    NAME                                      ROLE                                                  AGE
    tidb-operator-v2:tidb-controller-manager  ClusterRole/tidb-operator-v2:tidb-controller-manager  0s

    ==> v1/Deployment
    NAME                                      READY  UP-TO-DATE  AVAILABLE  AGE
    tidb-controller-manager-tidb-operator-v2  0/1    0           0          0s

    ==> v1/Pod(related)

    ==> v1/ServiceAccount
    NAME                                      SECRETS  AGE
    tidb-controller-manager-tidb-operator-v2  1        0s

    NOTES:
    Make sure tidb-operator components are running:
        kubectl get pods --namespace tidb-admin -l app.kubernetes.io/instance=tidb-operator-v2
    </code></pre>
    </details>

10. 确认第二套Operator部署情况

    ```shell
    kubectl -n tidb-admin get deploy tidb-controller-manager-tidb-operator-v2 -o yaml
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: tidb-controller-manager-tidb-operator-v2
      namespace: tidb-admin
    spec:
      template:
        spec:
          containers:
          - command:
            ...
            - -selector=canary-release=v2,canary-deployment=true
            ...
    </code></pre>
    </details>

11. 部署第二套tidbcluster

    ```shell
    kubectl -n tidb-cluster-2 create -f examples/basic/tidb-cluster.yaml
    ```

12. 标记第二套tidbcluster

    ```shell
    kubectl -n tidb-cluster-2 label tidbcluster basic canary-release=v2 canary-deployment=true
    ```

13. 验证

    查看第一套Operator controller-manager日志

    ```shell
    kubectl -n tidb-admin logs -f tidb-controller-manager-55b887bdc9-7jjzr
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    I0113 03:37:35.330277       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    I0113 03:38:04.948813       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    I0113 03:38:05.325378       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-1/basic] updated successfully
    </code></pre>
    </details>

    查看第二套Operator controller-manager日志

    ```shell
    tidb-controller-manager-tidb-operator-v2-5dfcd7f9-vll4c
    ```

    <details>
    <summary>Output</summary>
    <pre><code>
    I0113 03:38:43.859387       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-2/basic] updated successfully
    I0113 03:38:45.060028       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-2/basic] updated successfully
    I0113 03:38:46.261045       1 tidbcluster_control.go:69] TidbCluster: [tidb-cluster-2/basic] updated successfully
    </code></pre>
    </details>

    通过对比两套tidb-operator controller-manager日志，第一套Operator仅管理tidb-cluster-1/basic集群，第二套Operator仅管理tidb-cluster-1/basic集群。