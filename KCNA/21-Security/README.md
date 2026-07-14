# 21 — Security

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain the four Cs of Cloud Native Security (Cloud, Cluster, Container, Code).
- Explain RBAC (Role-Based Access Control): Roles, ClusterRoles, RoleBindings, ClusterRoleBindings.
- Explain ServiceAccounts and how Pods authenticate to the API server.
- Explain Secrets and Pod Security Standards/Admission.
- Read and write RBAC and Secret manifests.

**KCNA objectives covered:** Cloud Native Security domain.

---

## 2. Historical Background

Early multi-user computing systems required access-control models almost immediately — file permissions, user accounts, and privilege separation existed long before containers. As Kubernetes clusters became shared, multi-tenant systems running critical workloads, the same fundamental problem resurfaced at a new layer: **who or what is allowed to do what, to which resources, in the cluster?** Kubernetes adopted **RBAC** (a well-established access-control pattern from traditional systems) as its primary authorization mechanism, alongside **ServiceAccounts** (identity for workloads, not just humans), **Secrets** (for sensitive data), and **Pod Security Standards** (constraining what a Pod is allowed to do at the OS/kernel level).

---

## 3. Motivation: Why Does Kubernetes Need Built-in Security Primitives?

**Analogy — The Office Building's Keycard System:**
Imagine an office building with no keycard system — anyone who gets in the front door can walk into any room, including the server room and the CEO's office. Real office buildings issue keycards granting **only the specific access each person needs** (RBAC), separately badge visiting contractors differently from employees (ServiceAccounts for non-human identities), keep sensitive documents in a locked safe rather than lying on desks (Secrets), and have building policies restricting risky behavior building-wide (Pod Security Standards). Kubernetes needs the exact same layered security model because a cluster is a shared building with many different tenants, applications, and pieces of automation, each needing precisely scoped access — not blanket trust.

### 3.1 How Was This Solved Before Kubernetes?

Traditional systems used OS-level users/groups and file permissions; early container platforms often ran everything as root with minimal internal access control, trusting the perimeter (network firewall) rather than internal boundaries.

### 3.2 Why Was That Insufficient?

Perimeter-only security fails once you're inside a shared cluster running many tenants/workloads — a single compromised or careless Pod could otherwise access anything else in the cluster, including the API server itself, with no internal boundaries to stop lateral movement.

### 3.3 How Kubernetes Solves It

Kubernetes layers security across the "four Cs" (Section 4.1), enforces fine-grained, declarative access control via **RBAC**, gives every Pod a scoped, revocable machine identity via **ServiceAccounts**, stores sensitive data via **Secrets** (separated from Pod specs and ConfigMaps), and restricts risky Pod-level behavior via **Pod Security Standards/Admission**.

---

## 4. Core Concepts

### 4.1 The Four Cs of Cloud Native Security

| Layer | Concern |
|---|---|
| Cloud | Security of the underlying infrastructure (cloud provider account security, IAM, physical security) |
| Cluster | Security of the Kubernetes cluster itself (RBAC, API server access, etcd encryption) |
| Container | Security of the container image and runtime (minimal images, no running as root, vulnerability scanning) |
| Code | Security of the application code itself (secure coding practices, dependency scanning) |

Each layer depends on the ones "outside" it being secure — a secure Code layer doesn't help if the Cluster layer is wide open.

### 4.2 RBAC (Role-Based Access Control)

**Definition:** RBAC is Kubernetes's primary authorization mechanism, controlling **who** (a user, group, or ServiceAccount) can perform **what actions** (verbs like `get`, `list`, `create`, `delete`) on **which resources** (Pods, Services, Secrets, etc.), scoped to either a namespace or the whole cluster.

| Object | Scope | Purpose |
|---|---|---|
| Role | Namespace | Defines a set of permissions within one namespace |
| ClusterRole | Cluster-wide | Defines a set of permissions across the whole cluster (or reusable across namespaces) |
| RoleBinding | Namespace | Grants a Role (or ClusterRole) to a subject, within one namespace |
| ClusterRoleBinding | Cluster-wide | Grants a ClusterRole to a subject, cluster-wide |

### 4.3 ServiceAccount

**Definition:** A **ServiceAccount** is an identity that Pods use to authenticate to the Kubernetes API server (distinct from human user accounts). Every namespace has a `default` ServiceAccount, but best practice is creating dedicated, minimally-privileged ServiceAccounts per application.

### 4.4 Secrets

**Definition:** A **Secret** is an API object for storing sensitive data (passwords, tokens, keys), base64-encoded (not encrypted by default — encryption at rest must be separately configured) and kept distinct from ConfigMaps (which hold non-sensitive configuration).

### 4.5 Pod Security Standards / Admission

**Definition:** Kubernetes defines three built-in **Pod Security Standards** — `Privileged` (unrestricted), `Baseline` (blocks known privilege escalations), `Restricted` (heavily locked down, following hardening best practices) — enforceable via the built-in **Pod Security Admission** controller at the namespace level, replacing the older, now-removed PodSecurityPolicy mechanism.

---

## 5. Internal Working

```
1. A user or Pod (via its ServiceAccount token) sends a request to
   the API server
        ↓
2. Authentication: API server verifies the requester's identity
   (e.g., validates the ServiceAccount token or user certificate)
        ↓
3. Authorization (RBAC): API server checks whether any Role/ClusterRole
   bound to this identity (via RoleBinding/ClusterRoleBinding) permits
   the requested verb on the requested resource
        ↓
4. Admission Control: if authorized, admission controllers (including
   Pod Security Admission) may still reject or mutate the request
   based on additional policy (e.g., rejecting a Pod that requests
   privileged mode in a `Restricted` namespace)
        ↓
5. If all checks pass, the request is persisted to etcd and acted upon
```

---

## 6. Architecture

```
        ┌─────────────┐      ┌─────────────┐
        │   User/Human   │      │  Pod (via SA)   │
        └──────┬──────┘      └──────┬──────┘
                │  request                  │  request
                ▼                                  ▼
                    ┌────────────────────┐
                    │      API Server       │
                    │  1. Authentication      │
                    │  2. RBAC Authorization  │
                    │  3. Admission Control   │
                    │     (incl. Pod Security) │
                    └──────────┬──────────┘
                                ▼
                    ┌────────────────────┐
                    │        etcd            │
                    └────────────────────┘
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| Role / ClusterRole | Defines a set of permitted actions on resources |
| RoleBinding / ClusterRoleBinding | Grants a Role/ClusterRole to a subject |
| ServiceAccount | Machine identity used by Pods to authenticate |
| Secret | Storage for sensitive data |
| Pod Security Admission | Namespace-level enforcement of Pod Security Standards |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| RBAC | Role-Based Access Control — Kubernetes's primary authorization model |
| Role / ClusterRole | Permission set, namespaced or cluster-wide |
| RoleBinding / ClusterRoleBinding | Grants a Role/ClusterRole to a subject |
| ServiceAccount | Identity used by Pods/workloads (not humans) to authenticate |
| Secret | API object storing sensitive data, base64-encoded |
| Pod Security Standards | Three built-in security profiles: Privileged, Baseline, Restricted |
| Admission Controller | API server plugin that can validate/mutate requests after authorization |

---

## 9. YAML Deep Dive

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-reader
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
  - kind: ServiceAccount
    name: app-reader
    namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=
  password: cGFzc3dvcmQxMjM=
```

This grants the `app-reader` ServiceAccount **read-only** access (`get`, `list`, `watch`) to Pods in the `default` namespace only — nothing else, following least-privilege.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl create serviceaccount <name>` | Create a ServiceAccount | `kubectl create serviceaccount app-reader` |
| `kubectl get roles,rolebindings` | List Roles/RoleBindings in a namespace | `kubectl get roles,rolebindings` |
| `kubectl auth can-i <verb> <resource> --as=<subject>` | Test whether a subject can perform an action | `kubectl auth can-i list pods --as=system:serviceaccount:default:app-reader` |
| `kubectl create secret generic <name> --from-literal=key=value` | Create a Secret | `kubectl create secret generic db-credentials --from-literal=password=pass123` |
| `kubectl label namespace <ns> pod-security.kubernetes.io/enforce=restricted` | Enforce a Pod Security Standard on a namespace | `kubectl label namespace default pod-security.kubernetes.io/enforce=restricted` |

---

## 11. Hands-on Examples

**Lab 1 — Create a ServiceAccount with limited RBAC permissions and verify:**
```bash
kubectl apply -f rbac-example.yaml
kubectl auth can-i list pods --as=system:serviceaccount:default:app-reader
# yes
kubectl auth can-i delete pods --as=system:serviceaccount:default:app-reader
# no
```

**Lab 2 — Create and consume a Secret from within a Pod:**
```bash
kubectl create secret generic db-credentials --from-literal=password=pass123
kubectl run test-pod --image=nginx --overrides='
{"spec":{"containers":[{"name":"nginx","image":"nginx","envFrom":[{"secretRef":{"name":"db-credentials"}}]}]}}'
kubectl exec test-pod -- env | grep password
```

**Lab 3 — Enforce Restricted Pod Security Standard and confirm a privileged Pod is rejected:**
```bash
kubectl label namespace default pod-security.kubernetes.io/enforce=restricted
kubectl apply -f privileged-pod.yaml
# Rejected by admission: violates Restricted Pod Security Standard
```

---

## 12. Internal Flow

See Section 5 — every request to the API server passes through **authentication** (who are you), **RBAC authorization** (are you allowed to do this), and **admission control** (does this request otherwise comply with cluster policy, including Pod Security Standards) before it's ever persisted or acted upon.

---

## 13. Real-World Examples

1. **CI/CD pipelines** (Chapters 06-09 preview) use dedicated ServiceAccounts with narrowly scoped RBAC permissions (e.g., only allowed to deploy to a specific namespace) rather than broad cluster-admin access.
2. **Multi-tenant SaaS platforms** enforce `Restricted` Pod Security Standards cluster-wide to prevent any tenant workload from running privileged containers.
3. **Secret management integrations** (e.g., HashiCorp Vault, cloud KMS) often replace native Kubernetes Secrets with external secret stores injected at runtime, addressing the "base64 is not encryption" limitation.
4. **Audit logging** (a Cluster-layer security control) records every RBAC-authorized (and denied) API request for compliance and incident investigation.
5. **GitOps controllers** (Chapter 09/24 preview) run with tightly scoped ServiceAccounts so a compromised GitOps pipeline can't escalate beyond its intended deployment scope.

---

## 14. Best Practices

- Follow **least privilege**: grant only the exact verbs/resources a ServiceAccount needs, scoped to a namespace (Role) rather than cluster-wide (ClusterRole) whenever possible.
- Never rely on Secrets' base64 encoding as encryption — enable **encryption at rest** for etcd, and consider an external secret manager for highly sensitive data.
- Enforce `Restricted` (or at minimum `Baseline`) Pod Security Standards on all namespaces running untrusted or less-trusted workloads.
- Avoid using the `default` ServiceAccount for application Pods — create dedicated ServiceAccounts per application for clearer audit trails and scoped permissions.

---

## 15. Common Mistakes

- Granting `cluster-admin` (a built-in, all-powerful ClusterRole) to ServiceAccounts or users out of convenience, vastly exceeding what's actually needed.
- Assuming Secrets are encrypted simply because they're a distinct object type from ConfigMaps — without encryption at rest configured, Secret data in etcd is only base64-encoded, not encrypted.
- Forgetting that RoleBindings are namespace-scoped even when referencing a ClusterRole — granting a ClusterRole via a RoleBinding only applies within that one namespace, not cluster-wide (a frequently misunderstood distinction).
- Not enforcing any Pod Security Standard, leaving namespaces at the permissive default and allowing privileged, host-network, or host-PID Pods to run unchecked.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| "Forbidden" errors on API requests | RBAC permissions missing for the subject | `kubectl auth can-i <verb> <resource> --as=<subject>` | Add/adjust Role and RoleBinding |
| Pod rejected on creation | Violates the namespace's enforced Pod Security Standard | `kubectl describe pod`, check admission error message | Adjust Pod's securityContext to comply, or use a less restrictive namespace |
| Secret data appears as plain base64 in etcd backups | Encryption at rest not configured | Check API server `--encryption-provider-config` | Enable etcd encryption at rest |
| ServiceAccount has unexpectedly broad access | Bound to a powerful ClusterRole (e.g., `cluster-admin`) via ClusterRoleBinding | `kubectl get clusterrolebindings -o wide` | Replace with a narrowly scoped Role/RoleBinding |

---

## 17. Comparison Tables

| Object | Scope | Grants |
|---|---|---|
| Role | Namespace | Permissions within that namespace |
| ClusterRole | Cluster-wide | Permissions across the cluster (or reusable) |
| RoleBinding | Namespace | Binds a Role/ClusterRole to a subject, scoped to one namespace |
| ClusterRoleBinding | Cluster-wide | Binds a ClusterRole to a subject, cluster-wide |

| Pod Security Standard | Restriction Level |
|---|---|
| Privileged | No restrictions |
| Baseline | Blocks known privilege escalations |
| Restricted | Heavily locked down, hardened best practices |

---

## 18. Memory Tricks

- **"Keycard system"** — RBAC grants exactly the access needed, nothing more.
- **"Role = one room, ClusterRole = master key (scope depends on the binding used)."**
- **"Secrets are base64, not encrypted — locked drawer, not a safe, unless you add encryption at rest."**

---

## 19. Interview Questions

**Easy:**
1. What is the difference between a Role and a ClusterRole?
   *Expected answer:* A Role defines permissions scoped to a single namespace. A ClusterRole defines permissions that can apply cluster-wide (or be reused across multiple namespaces), depending on how it's bound.

**Medium:**
2. Why is it incorrect to say that Kubernetes Secrets are "encrypted"?
   *Expected answer:* By default, Secret data is only base64-**encoded**, not encrypted — base64 is trivially reversible and provides no real confidentiality protection. Actual encryption requires separately configuring encryption at rest for etcd (or using an external secret management system). Treating base64 encoding as if it were encryption is a common security misconception.

**Hard:**
3. A team binds a powerful ClusterRole (with broad permissions across many resource types) to a ServiceAccount using a **RoleBinding** (not a ClusterRoleBinding) in a single namespace, believing they've granted cluster-wide access. Later, they're surprised the ServiceAccount can't access resources in other namespaces. Explain why, and what they should have used instead.
   *Expected answer:* A RoleBinding, even when it references a ClusterRole, only grants the permissions defined in that ClusterRole **within the namespace the RoleBinding itself lives in** — it does not grant cluster-wide access. This is a common and useful pattern (reusing a single ClusterRole's rule set across many namespaces via separate RoleBindings) but it is scoped per-binding, not cluster-wide, by design. To actually grant cluster-wide access to all namespaces, the team needed a **ClusterRoleBinding** instead, which applies the ClusterRole's permissions across the entire cluster rather than being confined to one namespace.

---

## 20. KCNA Practice Questions

**Q1.** What are the "Four Cs" of Cloud Native Security?
A. Cloud, Cluster, Container, Code
B. Compute, Cluster, Container, Compliance
C. Cloud, Compute, Code, Compliance
D. Cluster, Container, Code, Certificate

**Correct answer: A**
*Explanation:* The Four Cs model layers security across Cloud (infrastructure), Cluster (Kubernetes itself), Container (image/runtime), and Code (application). The other options substitute incorrect terms.

---

**Q2.** What is the primary purpose of a ServiceAccount?
A. To provide a human user login to the Kubernetes dashboard
B. To provide an identity for Pods/workloads to authenticate to the API server
C. To store sensitive configuration data
D. To define network traffic rules

**Correct answer: B**
*Explanation:* ServiceAccounts are machine identities for Pods, distinct from human user accounts. C describes Secrets. D describes NetworkPolicy (Chapter 18).

---

**Q3.** By default, how is data stored in a Kubernetes Secret protected?
A. Encrypted using AES-256
B. Only base64-encoded, not encrypted, unless encryption at rest is separately configured
C. Stored in plaintext with no encoding at all
D. Automatically synced to an external vault

**Correct answer: B**
*Explanation:* Secrets are base64-encoded by default, which is not encryption — actual confidentiality requires enabling etcd encryption at rest or using an external secret manager. A, C, and D misdescribe default Secret behavior.

---

**Q4.** What does a RoleBinding do when it references a ClusterRole?
A. Grants the ClusterRole's permissions cluster-wide, regardless of the RoleBinding's namespace
B. Grants the ClusterRole's permissions only within the namespace the RoleBinding is created in
C. Has no effect — RoleBindings cannot reference ClusterRoles
D. Automatically converts the ClusterRole into a Role

**Correct answer: B**
*Explanation:* A RoleBinding scopes any referenced ClusterRole's permissions to its own namespace only — a common pattern for reusing one ClusterRole's rules across multiple namespaces without cluster-wide exposure. A describes ClusterRoleBinding behavior instead.

---

**Q5.** Which built-in Pod Security Standard is the most restrictive, enforcing hardened best practices?
A. Privileged
B. Baseline
C. Restricted
D. Enforced

**Correct answer: C**
*Explanation:* `Restricted` is the most locked-down of the three built-in standards. `Privileged` (A) applies no restrictions. `Baseline` (B) blocks only known privilege escalations, a middle ground. `Enforced` (D) is not a Pod Security Standard name — it's an admission mode (`enforce`, `audit`, `warn`).

---

**Q6.** In the "Office building keycard system" analogy, what does issuing different badges to visiting contractors versus employees represent?
A. RBAC least privilege
B. ServiceAccounts as distinct, non-human identities
C. Pod Security Standards
D. Secret encryption

**Correct answer: B**
*Explanation:* The analogy maps contractor-vs-employee badges to ServiceAccounts providing distinct machine identities separate from human users. A refers to scoped keycard access generally. C and D map to other parts of the analogy (building policies and the locked safe, respectively).

---

**Q7.** In the Internal Working flow, what happens immediately after the API server authenticates a request but before it is persisted to etcd?
A. The request is immediately written to etcd
B. RBAC authorization is checked, followed by admission control
C. The ServiceAccount token is regenerated
D. The kubelet validates the request

**Correct answer: B**
*Explanation:* Per Section 5, the order is authentication → RBAC authorization → admission control (including Pod Security Admission) → persistence to etcd. A skips required steps. C and D are not part of this flow.

---

**Q8.** Which verbs would a Role need to grant for a ServiceAccount to only watch and read Pods, never modify them?
A. create, update, patch
B. get, list, watch
C. delete, deletecollection
D. bind, escalate

**Correct answer: B**
*Explanation:* `get`, `list`, and `watch` are read-only verbs, matching the least-privilege read access shown in the YAML Deep Dive example. A and C are write/destructive verbs. D relates to RBAC escalation permissions, not basic read access.

---

**Q9.** Why does the chapter recommend avoiding the `default` ServiceAccount for application Pods?
A. The default ServiceAccount cannot authenticate to the API server
B. Using dedicated ServiceAccounts per application gives clearer audit trails and allows scoped, least-privilege permissions
C. The default ServiceAccount is automatically granted cluster-admin
D. Kubernetes deletes the default ServiceAccount after 24 hours

**Correct answer: B**
*Explanation:* Per Best Practices, dedicated ServiceAccounts improve auditability and let permissions be scoped precisely per application, rather than sharing one identity across unrelated workloads. A is false — the default ServiceAccount can authenticate. C and D are fabricated behaviors.

---

**Q10.** According to the Troubleshooting table, what is the first debugging step when an API request unexpectedly returns "Forbidden"?
A. Restart the API server
B. Run `kubectl auth can-i <verb> <resource> --as=<subject>` to check RBAC permissions
C. Regenerate the cluster's TLS certificates
D. Delete and recreate the Secret

**Correct answer: B**
*Explanation:* The Troubleshooting table lists `kubectl auth can-i ... --as=` as the direct way to confirm whether RBAC permits the action for that subject. A, C, and D are unrelated to diagnosing an authorization failure.

---

**Q11.** What is the security risk of granting `cluster-admin` to a ServiceAccount purely out of convenience?
A. There is no risk — cluster-admin is scoped to a single namespace
B. It vastly exceeds least privilege, giving the ServiceAccount unrestricted access across the entire cluster
C. cluster-admin only grants read access, so it is inherently safe
D. cluster-admin cannot be bound to ServiceAccounts, only human users

**Correct answer: B**
*Explanation:* Per Common Mistakes, `cluster-admin` is a built-in, all-powerful ClusterRole — binding it out of convenience violates least privilege and creates a large blast radius if that identity is compromised. A, C, and D misdescribe `cluster-admin`'s actual scope and power.

---

**Q12.** Which admission-control feature specifically enforces Pod Security Standards at the namespace level?
A. RBAC
B. Pod Security Admission
C. ServiceAccount token projection
D. NetworkPolicy

**Correct answer: B**
*Explanation:* Pod Security Admission is the built-in controller enforcing `Privileged`/`Baseline`/`Restricted` standards per namespace, replacing the removed PodSecurityPolicy. A governs authorization, not Pod-level restrictions. C and D are unrelated mechanisms (Chapter 18 covers NetworkPolicy).

---

**Q13.** A namespace is labeled `pod-security.kubernetes.io/enforce=restricted`. What happens when a Pod manifest requesting privileged mode is applied to it?
A. The Pod is created successfully with a warning logged
B. The request is rejected by admission control before the Pod is created
C. The Pod is created but immediately evicted
D. Only the privileged container within the Pod is removed

**Correct answer: B**
*Explanation:* As shown in Lab 3, a namespace enforcing `Restricted` will have admission control reject a privileged Pod outright at creation time. A describes `audit`/`warn` modes, not `enforce`. C and D do not reflect actual admission behavior.

---

**Q14.** Why is perimeter-only network security (e.g., a firewall around the whole cluster) insufficient inside a shared, multi-tenant Kubernetes cluster?
A. Firewalls do not work with container networking at all
B. A single compromised or careless Pod inside the perimeter could access anything else in the cluster without internal boundaries like RBAC
C. Perimeter security is actually sufficient and no internal controls are needed
D. Firewalls block all Pod-to-Pod communication by default

**Correct answer: B**
*Explanation:* Per Section 3.2, once inside the cluster, a compromised Pod can move laterally unless internal boundaries (RBAC, NetworkPolicy, Pod Security Standards) constrain it — perimeter defense alone doesn't stop internal lateral movement. A, C, and D are factually incorrect.

---

**Q15.** How does the "locked drawer, not a safe" memory trick describe default Secret behavior?
A. Secrets are fully encrypted and inaccessible without a key
B. Secrets are only base64-encoded (easily reversible), offering minimal real protection unless encryption at rest is added
C. Secrets cannot be read by any Pod under any circumstance
D. Secrets are stored only in memory and never persisted

**Correct answer: B**
*Explanation:* The mnemonic captures that base64 encoding is trivially reversible ("a locked drawer") rather than true encryption ("a safe") — matching Q3's explanation and the Memory Tricks section. A overstates protection. C and D misdescribe Secret accessibility and persistence.

---

**Q16.** In a CI/CD real-world example, why do pipelines use dedicated, narrowly scoped ServiceAccounts rather than broad cluster-admin access?
A. Cluster-admin ServiceAccounts are technically incompatible with CI/CD tools
B. Narrow scoping limits the blast radius if the pipeline's credentials are ever compromised
C. Kubernetes requires a new ServiceAccount for every pipeline run
D. Broad access improves pipeline performance

**Correct answer: B**
*Explanation:* Per Real-World Examples, scoping CI/CD ServiceAccounts to only what's needed (e.g., deploy to one namespace) limits damage if pipeline credentials leak — a direct application of least privilege. A, C, and D are not accurate reasons.

---

**Q17.** What distinguishes a ClusterRoleBinding from a RoleBinding referencing the same ClusterRole?
A. They behave identically in every respect
B. A ClusterRoleBinding grants the ClusterRole's permissions cluster-wide, while the RoleBinding confines them to its own namespace
C. A ClusterRoleBinding only works with Roles, not ClusterRoles
D. A RoleBinding can only bind to ServiceAccounts, never users

**Correct answer: B**
*Explanation:* This is the core distinction tested in Q4 and the hard interview question — same ClusterRole, but scope differs entirely based on which binding type is used. A ignores this critical difference. C and D are incorrect statements about binding capabilities.

---

**Q18.** Which of the following best explains why Secret and ConfigMap are kept as distinct object types in Kubernetes?
A. ConfigMaps are deprecated in favor of Secrets
B. Secrets are intended for sensitive data and receive different handling considerations (e.g., not logged in plaintext by some tooling), while ConfigMaps hold non-sensitive configuration
C. They are functionally identical and interchangeable
D. ConfigMaps can only store binary data, while Secrets only store text

**Correct answer: B**
*Explanation:* Per Section 4.4, Secrets are specifically for sensitive data with handling considerations distinct from ConfigMaps' general-purpose configuration role. A is false. C contradicts their distinct purposes. D misdescribes their data-format capabilities (both can hold similar data types).

---

**Q19.** What replaced the older PodSecurityPolicy (PSP) mechanism, which has since been removed from Kubernetes?
A. NetworkPolicy
B. Pod Security Admission, enforcing the built-in Pod Security Standards
C. RBAC ClusterRoles
D. Admission webhooks only, with no built-in alternative

**Correct answer: B**
*Explanation:* Per Section 4.5, Pod Security Admission (enforcing `Privileged`/`Baseline`/`Restricted`) is the built-in replacement for the removed PodSecurityPolicy. A and C address different concerns (network isolation and authorization, respectively). D is incorrect — a built-in alternative does exist.

---

**Q20.** Following the Troubleshooting table, if audits reveal a ServiceAccount has unexpectedly broad cluster access, what is the most likely underlying cause and fix?
A. The ServiceAccount was bound to a powerful ClusterRole (e.g., `cluster-admin`) via a ClusterRoleBinding; fix by replacing it with a narrowly scoped Role/RoleBinding
B. The ServiceAccount's token expired; fix by rotating the token
C. The namespace's Pod Security Standard is too permissive; fix by enforcing `Restricted`
D. The Secret associated with the ServiceAccount was leaked; fix by deleting the Secret

**Correct answer: A**
*Explanation:* Per the Troubleshooting table, unexpectedly broad access traces to an overly powerful ClusterRoleBinding, remedied by scoping down to a Role/RoleBinding. B, C, and D address unrelated symptoms (token lifecycle, Pod-level restrictions, and Secret exposure) rather than RBAC over-permissioning.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Cloud Native Security spans the **Four Cs**: Cloud, Cluster, Container, Code — each layer depends on the ones outside it.
- **RBAC** governs authorization via Roles/ClusterRoles (permission sets) and RoleBindings/ClusterRoleBindings (grants to subjects) — RoleBindings always scope to their own namespace, even when referencing a ClusterRole.
- **ServiceAccounts** are machine identities for Pods, distinct from human users; avoid using the `default` ServiceAccount for applications.
- **Secrets** are base64-encoded, **not encrypted**, by default — enable etcd encryption at rest or use an external secret manager for real confidentiality.
- **Pod Security Standards** (`Privileged`, `Baseline`, `Restricted`), enforced via **Pod Security Admission**, restrict risky Pod-level behavior at the namespace level.

---

### Chapter Completion Checklist

1. **Topics covered:** Four Cs of Cloud Native Security, RBAC (Role/ClusterRole/RoleBinding/ClusterRoleBinding), ServiceAccounts, Secrets, Pod Security Standards/Admission.
2. **KCNA objectives completed:** Cloud Native Security domain.
3. **Remaining objectives:** Observability — logging, metrics, tracing, health checks (Chapter 22).
4. **Suggested revision checklist:** Recite the Four Cs; explain the RBAC object relationships from memory; explain why RoleBinding+ClusterRole is namespace-scoped; explain why Secrets aren't encrypted by default.
5. **Suggested hands-on exercises:** Complete Lab 1 (RBAC permission test via `kubectl auth can-i`) — the clearest way to verify least-privilege configuration actually works as intended.
6. **Related chapters:** Previous: [20-Scheduling](../20-Scheduling/README.md). Next: [22-Observability](../22-Observability/README.md) — how to monitor and understand cluster/application behavior.
