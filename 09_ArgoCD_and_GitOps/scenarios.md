# ArgoCD and GitOps — Production Scenarios

## Scenario 1: App Stuck OutOfSync — Cannot Sync

**Symptom**: Application shows `OutOfSync` status but every sync attempt immediately fails or returns to OutOfSync. The UI shows resources that appear identical.

### Diagnosis

```bash
# Get detailed sync status and last operation
argocd app get my-app --show-operation

# Check what ArgoCD thinks the diff is
argocd app diff my-app --refresh

# Look at the specific resource that is out of sync
argocd app resources my-app

# Get Kubernetes events for the namespace
kubectl get events -n production --sort-by='.lastTimestamp'

# Check application controller logs
kubectl logs -n argocd deploy/argocd-application-controller \
  --tail=100 | grep -i "my-app"
```

### Common Root Causes and Fixes

**Cause 1: Ignored fields with defaulted values**

Kubernetes controllers mutate resources after apply (e.g., `spec.selector` gets set by the Deployment controller). ArgoCD sees the controller-defaulted value as a diff.

```yaml
# Fix: add ignoreDifferences to the Application spec
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/template/metadata/annotations/kubectl.kubernetes.io~1last-applied-configuration
    - group: ""
      kind: Service
      jsonPointers:
        - /spec/clusterIP
        - /spec/clusterIPs
```

**Cause 2: Resource managed by another controller**

A label or annotation is being continuously modified by an external operator (e.g., a mesh injecting sidecar annotations).

```bash
# Watch the resource for live mutations
kubectl get deployment my-app -n production -w -o json | jq '.metadata.annotations'

# Fix: ignore the specific field
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jqPathExpressions:
        - '.metadata.annotations["sidecar.istio.io/inject"]'
```

**Cause 3: Helm chart generates non-deterministic output**

Some Helm charts use `randAlphaNum` or `now` functions, generating different values on each template render.

```bash
# Check if rendered manifest changes between renders
argocd app diff my-app
# Wait 60 seconds
argocd app diff my-app --refresh
# If the diff changes, it's a template non-determinism issue

# Fix: pin the random values in values.yaml or use a secret pre-created outside Helm
```

**Cause 4: CRD schema validation rejecting the manifest**

```bash
# Check if a dry-run apply would succeed
kubectl apply -f manifest.yaml --dry-run=server -n production

# Look for validation errors in API server audit logs
kubectl get events -n production | grep "FailedCreate\|Invalid"
```

---

## Scenario 2: Sync Wave Ordering Failure

**Symptom**: Sync fails mid-way. A resource in wave 2 fails because it depends on a resource from wave 1 that has not yet become healthy.

**Example**: A `Deployment` in wave 1 depends on a CRD that was just applied in wave -1, but the CRD is not yet established when the deployment's controller tries to create its custom resource.

### Diagnosis

```bash
# Check which wave failed
argocd app get my-app --show-operation
# Look for "SyncFailed" and the specific resource

# Check CRD establishment status
kubectl get crd my-crd.example.com -o jsonpath='{.status.conditions}'

# Check if resources from the previous wave are actually ready
kubectl get deployments -n production -l app=my-app
kubectl rollout status deployment/dependency-service -n production
```

### Fix

**Option 1: Add health checks to wave 1 resources so ArgoCD waits before proceeding**

ArgoCD respects Kubernetes resource health before advancing to the next wave. Ensure the CRD or Deployment in wave 1 has a health check defined.

For CRDs, ArgoCD has built-in health checks. But for custom resources, define a Lua health check in the ArgoCD ConfigMap:

```yaml
# argocd-cm ConfigMap
data:
  resource.customizations.health.mygroup_MyResource: |
    hs = {}
    if obj.status ~= nil then
      if obj.status.phase == "Ready" then
        hs.status = "Healthy"
        hs.message = "Resource is ready"
        return hs
      end
    end
    hs.status = "Progressing"
    hs.message = "Waiting for resource to become ready"
    return hs
```

**Option 2: Adjust wave numbers to create a larger gap**

```yaml
# Wave -2: CRDs
# Wave -1: Namespaces, RBAC
# Wave 0: ConfigMaps, Secrets
# Wave 1: Core services (databases, message queues)
# Wave 2: Application services that depend on wave 1
# Wave 3: Ingress, HPA
```

**Option 3: Use a PreSync hook for the dependency**

```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
```

---

## Scenario 3: Argo Image Updater Misconfiguration

**Symptom**: Image Updater is configured but never updates image tags in Git despite new images being pushed to the registry.

### Diagnosis

```bash
# Check Image Updater logs
kubectl logs -n argocd deploy/argocd-image-updater --tail=200 | grep -i "error\|warn\|my-app"

# Check the application annotations
kubectl get application my-app -n argocd -o yaml | grep -A 20 annotations

# Verify the registry is reachable from the cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  https://registry.example.com/v2/my-app/tags/list
```

### Common Misconfigurations

**Cause 1: Missing or wrong image annotation format**

```yaml
# Correct annotations on the ArgoCD Application
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: myapp=registry.example.com/my-app
    argocd-image-updater.argoproj.io/myapp.update-strategy: semver
    argocd-image-updater.argoproj.io/myapp.allow-tags: regexp:^v[0-9]+\.[0-9]+\.[0-9]+$
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/git-branch: main
```

**Cause 2: Missing write-back credentials**

Image Updater needs credentials to push commits to Git.

```bash
# Create the git credentials secret
kubectl create secret generic git-creds \
  --from-literal=username=my-bot \
  --from-literal=password=ghp_xxxx \
  -n argocd

# Reference in the application
metadata:
  annotations:
    argocd-image-updater.argoproj.io/write-back-method: git:secret:argocd/git-creds
```

**Cause 3: Registry credentials missing**

```bash
kubectl create secret docker-registry registry-creds \
  --docker-server=registry.example.com \
  --docker-username=my-bot \
  --docker-password=my-token \
  -n argocd

# Image Updater reads secrets labeled with this label
kubectl label secret registry-creds \
  argocd-image-updater.argoproj.io/image-list=myapp \
  -n argocd
```

---

## Scenario 4: Self-Managed ArgoCD Bootstrap

**Symptom**: Need to bootstrap ArgoCD on a fresh cluster so ArgoCD manages its own installation (self-managed/GitOps for ArgoCD itself).

### Approach

```bash
# Step 1: Apply ArgoCD CRDs and controllers the first time manually
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Step 2: Create the self-managing Application
kubectl apply -f - <<'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: argocd
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://argoproj.github.io/argo-helm
    chart: argo-cd
    targetRevision: 7.x
    helm:
      valuesObject:
        server:
          extraArgs:
            - --insecure
        configs:
          params:
            server.insecure: true
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: false       # Never auto-prune ArgoCD's own components
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
EOF

# Step 3: From now on, update ArgoCD by bumping targetRevision in Git
# ArgoCD will sync its own upgrade
```

**Key considerations:**
- Use `prune: false` for the ArgoCD self-managing application — you don't want ArgoCD to delete itself
- Use `ServerSideApply=true` — ArgoCD Helm chart uses server-side apply annotations
- Store the Application manifest in a dedicated bootstrap repo separate from application code

---

## Scenario 5: Multi-Cluster Deployment Failure

**Symptom**: An ApplicationSet targeting 20 clusters shows 3 clusters as `Unknown` or `ComparisonError`.

### Diagnosis

```bash
# Find which clusters are failing
argocd cluster list --output json | \
  jq -r '.[] | select(.connectionState.status != "Successful") | 
  "\(.name) \(.connectionState.status) \(.connectionState.message)"'

# Check connectivity from the ArgoCD hub to a failing spoke cluster
kubectl exec -n argocd deploy/argocd-application-controller -- \
  curl -k https://prod-ap.k8s.example.com/api/v1/namespaces --max-time 5

# Check the cluster secret
kubectl get secret -n argocd -l argocd.argoproj.io/secret-type=cluster | grep prod-ap
kubectl get secret prod-ap-cluster -n argocd -o jsonpath='{.data.config}' | \
  base64 -d | jq '.tlsClientConfig'

# Check token expiry
kubectl get secret prod-ap-cluster -n argocd -o jsonpath='{.data.config}' | \
  base64 -d | jq -r '.bearerToken' | \
  cut -d. -f2 | base64 -d 2>/dev/null | jq '.exp | todate'
```

### Common Causes

**Cause 1: Cluster credential token expired**

```bash
# Re-register the cluster to rotate the ServiceAccount token
argocd cluster rm https://prod-ap.k8s.example.com
argocd cluster add prod-ap-context --name prod-ap \
  --label environment=production \
  --label region=ap-southeast-1
```

**Cause 2: Spoke cluster API server certificate changed**

```bash
# Update the cluster secret with new CA data
NEW_CA=$(kubectl --context=prod-ap-context \
  get configmap kube-root-ca.crt -n default \
  -o jsonpath='{.data.ca\.crt}' | base64 -w0)

kubectl patch secret prod-ap-cluster -n argocd \
  --type='json' \
  -p="[{\"op\": \"replace\", \"path\": \"/data/config\", \"value\": \"...\"}]"
```

**Cause 3: ArgoCD RBAC insufficient on spoke cluster**

```bash
# Check what permissions the ArgoCD SA has on the spoke cluster
kubectl --context=prod-ap-context auth can-i \
  --list \
  --as=system:serviceaccount:argocd:argocd-application-controller
```

---

## Scenario 6: Progressive Delivery Rollback Trigger

**Symptom**: A canary rollout is at 25% traffic and the analysis is detecting elevated error rates, but the rollout is not automatically aborting.

### Diagnosis

```bash
# Check rollout status
kubectl argo rollouts get rollout payment-service -n production

# Check analysis run status
kubectl get analysisrun -n production
kubectl describe analysisrun payment-service-<hash> -n production

# Check the metric query is returning data
kubectl exec -n monitoring deploy/prometheus -- \
  promtool query instant \
  'sum(rate(http_requests_total{service="payment-service-canary",status=~"5.."}[5m]))'
```

### Common Causes

**Cause 1: Analysis metric query returns no data (empty result)**

An empty Prometheus result is not the same as 0. By default, Argo Rollouts treats `no data` as inconclusive, not failure.

```yaml
# Fix: set inconclusiveLimit = 0 to treat no-data as failure
metrics:
  - name: success-rate
    inconclusiveLimit: 0      # Treat no-data as failure immediately
    successCondition: result[0] >= 0.99
    failureCondition: result[0] < 0.99
```

**Cause 2: `failureLimit` too high**

```yaml
# If failureLimit: 5, it takes 5 consecutive failures before aborting
# Reduce for faster rollback
metrics:
  - name: success-rate
    failureLimit: 1         # Abort after 1 failed check
    interval: 30s
    count: 3
```

**Cause 3: Analysis interval too long**

If `interval: 5m` and `count: 3`, the rollout waits 15 minutes before aborting. Reduce for critical services.

### Manual Abort

```bash
# Manually abort and rollback
kubectl argo rollouts abort payment-service -n production

# This rolls traffic back to stable but keeps the failed canary pods
# To retry:
kubectl argo rollouts retry rollout payment-service -n production
```

---

## Scenario 7: Webhook Not Firing — ArgoCD Not Detecting Git Changes

**Symptom**: Commits to the Git repository do not trigger a sync. ArgoCD only picks up changes after the default 3-minute polling interval.

### Diagnosis

```bash
# Check if webhooks are configured
argocd repo list
argocd repo get https://github.com/org/repo

# Check ArgoCD API server logs for incoming webhooks
kubectl logs -n argocd deploy/argocd-server --tail=200 | grep -i "webhook\|github"

# Test webhook delivery from GitHub
# Go to: GitHub repo → Settings → Webhooks → Recent Deliveries
# Look for 200 OK responses or error codes

# Check ArgoCD API server service is accessible externally
kubectl get svc -n argocd argocd-server
```

### Common Causes

**Cause 1: Webhook URL misconfigured**

The webhook URL must point to the ArgoCD API server's `/api/webhook` endpoint.

```
Correct: https://argocd.example.com/api/webhook
Wrong:   https://argocd.example.com/webhook
         https://argocd.example.com/api/v1/webhook
```

**Cause 2: Webhook secret mismatch**

```bash
# Check the configured webhook secret in ArgoCD
kubectl get secret -n argocd argocd-secret -o jsonpath='{.data.webhook\.github\.secret}' | base64 -d

# This must match the secret configured in GitHub repo settings exactly
# If mismatch: ArgoCD logs will show "webhook signature validation failed"
```

**Cause 3: ArgoCD API server not exposed externally**

```bash
# If using LoadBalancer:
kubectl get svc -n argocd argocd-server -o jsonpath='{.status.loadBalancer.ingress}'

# If using Ingress: verify the ingress is routing /api/webhook correctly
kubectl get ingress -n argocd
kubectl describe ingress argocd-server -n argocd

# Test the webhook endpoint from outside the cluster
curl -X POST https://argocd.example.com/api/webhook \
  -H "X-GitHub-Event: push" \
  -H "Content-Type: application/json" \
  -d '{"ref":"refs/heads/main"}' -v
```

**Cause 4: Network policy blocking ingress**

```bash
# Check if a NetworkPolicy blocks traffic to the argocd namespace
kubectl get networkpolicy -n argocd
kubectl describe networkpolicy -n argocd

# Test connectivity from a pod in the cluster
kubectl run test --rm -it --image=curlimages/curl -- \
  curl http://argocd-server.argocd.svc.cluster.local/api/webhook
```

**Fix: Re-register webhook**

In GitHub: Settings → Webhooks → Add webhook
- Payload URL: `https://argocd.example.com/api/webhook`
- Content type: `application/json`
- Secret: value from `argocd-secret.webhook.github.secret`
- Events: `Push events`, `Pull request events` (for PR generator)
