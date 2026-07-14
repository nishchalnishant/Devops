# 19 — Storage

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why containers need a separate storage abstraction from their ephemeral filesystem.
- Explain Volumes, PersistentVolumes (PV), PersistentVolumeClaims (PVC), and StorageClasses, and how they relate.
- Explain dynamic provisioning and access modes.
- Read and write PV, PVC, and StorageClass manifests, and mount a PVC into a Pod.

**KCNA objectives covered:** Cloud Native Architecture domain — Kubernetes storage abstractions.

---

## 2. Historical Background

Before container orchestration, applications typically stored data directly on the host's local disk, or connected to network storage using ad-hoc, application-specific configuration. Early container platforms carried the same limitation forward: a container's filesystem is, by default, tied to that one container's lifetime — when the container is removed, its filesystem changes vanish. As orchestration scaled applications across many nodes with Pods being created, destroyed, and rescheduled constantly (Chapters 10-12), this ephemeral, node-local storage model became unworkable for anything needing durable data (databases, user uploads, logs). Kubernetes introduced a layered storage abstraction — **Volumes**, **PersistentVolumes**, **PersistentVolumeClaims**, and **StorageClasses** — to decouple "what storage an application needs" from "which physical/cloud storage actually provides it."

---

## 3. Motivation: Why Does Kubernetes Need a Storage Abstraction?

**Analogy — The Hotel Room vs. The Storage Locker:**
A container's own filesystem is like a hotel room: when you check out (the container restarts or is replaced), housekeeping resets everything — nothing you left behind survives. But some things you need to keep no matter how many times you change rooms: your passport, your luggage. For that, you rent a **storage locker** elsewhere in the building — one that exists independently of any particular room, and can be reattached to whichever room you're staying in next. A Kubernetes **PersistentVolume** is that storage locker: independent of any one Pod's lifecycle, and reattachable across Pod restarts and rescheduling.

### 3.1 How Was This Solved Before Kubernetes?

Applications wrote directly to host disks or manually mounted network shares (NFS, SAN) using bespoke, per-application configuration — brittle, inconsistent, and hard to move between machines or cloud providers.

### 3.2 Why Was That Insufficient?

Manual, application-specific storage wiring doesn't scale across a dynamic cluster where Pods can be rescheduled to any node at any time; the storage must "follow" the Pod regardless of node placement, and provisioning needs to be automatable rather than done by hand for every application.

### 3.3 How Kubernetes Solves It

Kubernetes separates **what** storage an app needs (a **PersistentVolumeClaim** — a request) from **how** that storage is actually provided (a **PersistentVolume**, either pre-created or dynamically provisioned via a **StorageClass**), letting the same application manifest work unmodified across different clusters and cloud storage backends.

---

## 4. Core Concepts

### 4.1 Volume

**Definition:** A **Volume** is storage attached to a Pod, with a lifecycle tied to that Pod (not any single container within it — restarting a container inside a Pod does not lose Volume data, but deleting the Pod usually does, unless the Volume type is itself persistent). Basic Volume types include `emptyDir` (temporary scratch space, deleted with the Pod) and `hostPath` (mounts a path from the host node — generally discouraged since it ties Pods to specific nodes).

### 4.2 PersistentVolume (PV)

**Definition:** A **PersistentVolume** is a cluster-level storage resource, provisioned either manually by an administrator or automatically via dynamic provisioning, representing actual durable storage (e.g., a cloud disk, NFS share) with a lifecycle **independent** of any Pod.

### 4.3 PersistentVolumeClaim (PVC)

**Definition:** A **PersistentVolumeClaim** is a namespaced request for storage made by a user/application, specifying size and access mode requirements. Kubernetes binds a PVC to a matching PV (or dynamically provisions one), and the Pod mounts the PVC — never the PV directly.

### 4.4 StorageClass

**Definition:** A **StorageClass** defines a class of storage (e.g., "fast SSD," "slow HDD," a specific cloud provisioner) and enables **dynamic provisioning**: when a PVC requests a StorageClass, Kubernetes automatically creates a matching PV on demand, rather than requiring an administrator to pre-create PVs manually.

### 4.5 Access Modes

| Access Mode | Meaning |
|---|---|
| ReadWriteOnce (RWO) | Mountable read-write by a single node |
| ReadOnlyMany (ROX) | Mountable read-only by many nodes |
| ReadWriteMany (RWX) | Mountable read-write by many nodes |
| ReadWriteOncePod (RWOP) | Mountable read-write by a single Pod only (newer, stricter mode) |

---

## 5. Internal Working

```
1. User creates a PVC requesting e.g. 10Gi, StorageClass "fast-ssd",
   access mode ReadWriteOnce
        ↓
2. Kubernetes checks for an existing PV matching the request
        ↓
3. If none exists AND a StorageClass is specified, the StorageClass's
   provisioner dynamically creates a new PV (and the underlying
   cloud/storage resource) to satisfy the claim
        ↓
4. The PVC is bound 1:1 to the resulting PV
        ↓
5. A Pod references the PVC by name in its volumes section
        ↓
6. The kubelet mounts the underlying storage into the Pod's
   containers at the specified mountPath
        ↓
7. If the Pod is deleted and recreated (e.g., a StatefulSet Pod,
   Chapter 14), it can reattach to the same PVC/PV, preserving data
```

---

## 6. Architecture

```
   ┌─────────────┐        ┌─────────────┐        ┌────────────────┐
   │     Pod      │──uses──▶│     PVC      │──binds──▶│      PV        │
   │ (mounts PVC) │        │ (a request)  │        │ (actual storage) │
   └─────────────┘        └──────┬──────┘        └───────┬────────┘
                                    │  dynamic provisioning        │
                                    ▼                                   ▼
                            ┌──────────────┐              ┌───────────────────┐
                            │ StorageClass  │─────────────▶│ Cloud/Network Disk  │
                            │ (provisioner) │   creates      │ (e.g., EBS, NFS)     │
                            └──────────────┘              └───────────────────┘
```

---

## 7. Component Breakdown

| Component | Role |
|---|---|
| Volume | Pod-scoped storage attachment (may or may not be persistent, depending on type) |
| PersistentVolume (PV) | Cluster-level durable storage resource |
| PersistentVolumeClaim (PVC) | Namespaced request for storage, bound to a PV |
| StorageClass | Defines a storage type and enables dynamic PV provisioning |
| CSI driver | Modern plugin interface (Container Storage Interface) implementing actual provisioning/attaching for a specific storage backend |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| PV (PersistentVolume) | Actual durable storage resource at the cluster level |
| PVC (PersistentVolumeClaim) | A request for storage, bound to a PV |
| StorageClass | A named storage tier/provisioner enabling dynamic provisioning |
| Dynamic provisioning | Automatic PV creation triggered by a PVC referencing a StorageClass |
| Access Mode | Defines how many nodes/Pods may mount a volume, and in what mode (read/write) |
| CSI (Container Storage Interface) | Standard plugin interface for storage providers, analogous to CNI for networking |
| Reclaim Policy | What happens to a PV's underlying storage after its PVC is deleted (`Retain`, `Delete`, `Recycle`) |

---

## 9. YAML Deep Dive

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: app-with-storage
spec:
  containers:
    - name: app
      image: nginx:1.27
      volumeMounts:
        - name: data
          mountPath: /usr/share/nginx/html
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: data-pvc
```

`volumeBindingMode: WaitForFirstConsumer` delays PV provisioning until a Pod actually uses the PVC, ensuring the storage is provisioned in the correct zone/node topology.

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get pv` | List PersistentVolumes | `kubectl get pv` |
| `kubectl get pvc` | List PersistentVolumeClaims | `kubectl get pvc` |
| `kubectl describe pvc <name>` | Show PVC binding status/events | `kubectl describe pvc data-pvc` |
| `kubectl get storageclass` | List StorageClasses | `kubectl get storageclass` |
| `kubectl delete pvc <name>` | Delete a PVC (may trigger PV deletion per reclaim policy) | `kubectl delete pvc data-pvc` |

---

## 11. Hands-on Examples

**Lab 1 — Create a StorageClass, PVC, and Pod, and confirm dynamic provisioning:**
```bash
kubectl apply -f storage-example.yaml
kubectl get pvc data-pvc
# STATUS should transition to "Bound"
kubectl get pv
# A PV should now exist, dynamically created
```

**Lab 2 — Write data, delete and recreate the Pod, confirm persistence:**
```bash
kubectl exec app-with-storage -- sh -c 'echo hello > /usr/share/nginx/html/test.txt'
kubectl delete pod app-with-storage
kubectl apply -f pod.yaml
kubectl exec app-with-storage -- cat /usr/share/nginx/html/test.txt
# Outputs "hello" — same PVC reattached, data survived
```

**Lab 3 — Delete the PVC and observe the PV's reclaim policy in action:**
```bash
kubectl delete pvc data-pvc
kubectl get pv
# With reclaimPolicy: Delete, the underlying PV (and cloud disk) is also removed
```

---

## 12. Internal Flow

See Section 5 — the PVC is the single object application authors interact with; everything from PV binding to underlying disk creation is handled transparently via the StorageClass's provisioner (traditionally in-tree, now standardized as **CSI drivers**), mirroring how CNI (Chapter 18) standardizes pluggable networking.

---

## 13. Real-World Examples

1. **Databases running in Kubernetes** (e.g., PostgreSQL via a StatefulSet, Chapter 14) rely on PVCs bound to fast-SSD-class PVs for durable, low-latency storage.
2. **Cloud-managed clusters** (EKS, AKS, GKE) each ship default StorageClasses backed by their respective block storage services (EBS, Azure Disk, Persistent Disk).
3. **Shared file storage** (e.g., NFS-backed PVs with `ReadWriteMany`) is used when multiple Pods across nodes need to read/write the same files concurrently.
4. **Backup/restore workflows** snapshot PVs periodically, relying on the CSI driver's snapshot support.
5. **Cost optimization** (Chapter 16 Platform Engineering domain preview) uses tiered StorageClasses (e.g., cheaper HDD-backed classes for infrequently accessed data) to control storage spend.

---

## 14. Best Practices

- Always request storage via a **PVC**, never reference a PV directly from a Pod — keeps the application manifest portable across clusters/backends.
- Set `reclaimPolicy: Retain` for critical data if you want a manual safety check before storage is actually destroyed.
- Use `volumeBindingMode: WaitForFirstConsumer` to avoid provisioning storage in the wrong availability zone before a Pod's actual placement is known.
- Choose access modes deliberately — `ReadWriteOnce` is the most widely supported and performant option; only use `ReadWriteMany` when genuinely needed.

---

## 15. Common Mistakes

- Using `hostPath` volumes for anything beyond debugging/testing — ties a Pod to a specific node and offers no real durability guarantee.
- Forgetting that `emptyDir` volumes are deleted along with the Pod — not suitable for data that must survive Pod rescheduling.
- Assuming a deleted PVC always deletes underlying data — actually governed by the PV's `reclaimPolicy` (`Retain` keeps data even after PVC deletion).
- Requesting an access mode not supported by the underlying storage backend (e.g., `ReadWriteMany` on a backend that only supports `ReadWriteOnce`), causing the PVC to remain stuck in `Pending`.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| PVC stuck in `Pending` | No matching PV and no StorageClass/provisioner configured, or unsupported access mode requested | `kubectl describe pvc <name>` | Specify a valid StorageClass; verify supported access modes |
| Pod stuck in `ContainerCreating` | Volume attach/mount failure | `kubectl describe pod <name>`, check events | Check CSI driver logs, node's storage attachment limits |
| Data lost after Pod restart | Used `emptyDir` instead of a PVC-backed volume | `kubectl get pod <name> -o yaml` | Switch to a PVC-backed persistent volume |
| PV stuck in `Released`, not reusable | Reclaim policy set to `Retain`, requires manual cleanup | `kubectl get pv` | Manually delete/reclaim the PV per policy, or change reclaim policy |

---

## 17. Comparison Tables

| Object | Scope | Lifecycle |
|---|---|---|
| Volume | Pod | Tied to Pod (unless a persistent type is used) |
| PersistentVolume (PV) | Cluster | Independent of any Pod |
| PersistentVolumeClaim (PVC) | Namespace | Independent of Pod, bound to a PV |
| StorageClass | Cluster | Defines provisioning behavior, not storage itself |

| Reclaim Policy | Behavior on PVC deletion |
|---|---|
| `Retain` | PV and underlying storage kept, requires manual cleanup |
| `Delete` | PV and underlying storage automatically deleted |
| `Recycle` (deprecated) | Basic scrub and reuse — replaced by dynamic provisioning |

---

## 18. Memory Tricks

- **"PVC is the request, PV is the fulfillment, StorageClass is the factory that builds it on demand."**
- **"Hotel room vs. storage locker"** — container filesystem resets on restart; PV-backed storage survives independently.
- Reclaim policy mnemonic: **"Retain = keep the locker, Delete = destroy the locker."**

---

## 19. Interview Questions

**Easy:**
1. What is the difference between a PersistentVolume and a PersistentVolumeClaim?
   *Expected answer:* A PersistentVolume (PV) is the actual durable storage resource at the cluster level. A PersistentVolumeClaim (PVC) is a namespaced request for storage made by an application, which Kubernetes binds to a matching PV (or dynamically provisions one via a StorageClass).

**Medium:**
2. What is dynamic provisioning, and what enables it?
   *Expected answer:* Dynamic provisioning is the automatic creation of a PersistentVolume when a PVC requests storage, rather than requiring an administrator to pre-create PVs manually. It's enabled by specifying a `StorageClass` on the PVC — the StorageClass's provisioner (often a CSI driver) creates the matching PV and underlying storage resource on demand.

**Hard:**
3. A team deletes a PVC that was bound to a PV with `reclaimPolicy: Retain`, expecting the underlying cloud disk to be freed up automatically. A week later they discover the disk is still there and still being billed. Explain what happened and how they should have handled it.
   *Expected answer:* With `reclaimPolicy: Retain`, deleting the PVC does not delete the underlying PV or its actual storage — the PV instead transitions to a `Released` state, remaining in the cluster (and the underlying cloud disk continues to exist and be billed) until an administrator manually deletes the PV object and the underlying storage resource. This policy exists specifically to prevent accidental data loss, trading off automatic cleanup for safety. The team should have either used `reclaimPolicy: Delete` if automatic cleanup was actually desired and the data was disposable, or, since they used `Retain`, followed up the PVC deletion with a manual review and deletion of the now-`Released` PV (and its underlying disk) once they confirmed the data was no longer needed.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of a PersistentVolumeClaim (PVC)?
A. To define a storage class's provisioner
B. To request storage on behalf of an application, later bound to a PersistentVolume
C. To directly represent a physical disk
D. To configure Pod networking

**Correct answer: B**
*Explanation:* A PVC is a namespaced request for storage. A describes StorageClass. C describes a PersistentVolume. D is unrelated (Chapter 18 topic).

---

**Q2.** What triggers dynamic provisioning of a PersistentVolume?
A. Creating a Pod with an `emptyDir` volume
B. A PVC referencing a StorageClass with no matching existing PV
C. Deleting a PersistentVolume
D. Scaling a Deployment

**Correct answer: B**
*Explanation:* When a PVC references a StorageClass and no matching PV exists, the StorageClass's provisioner dynamically creates one. A describes ephemeral, non-persistent storage. C and D are unrelated to provisioning.

---

**Q3.** Which access mode allows a volume to be mounted read-write by many nodes simultaneously?
A. ReadWriteOnce (RWO)
B. ReadOnlyMany (ROX)
C. ReadWriteMany (RWX)
D. ReadWriteOncePod (RWOP)

**Correct answer: C**
*Explanation:* ReadWriteMany permits concurrent read-write mounting across multiple nodes. RWO (A) restricts to a single node. ROX (B) is read-only across many nodes. RWOP (D) restricts to a single Pod.

---

**Q4.** What happens to a PersistentVolume's underlying storage when its bound PVC is deleted, if `reclaimPolicy` is set to `Retain`?
A. The storage is immediately deleted
B. The storage is kept, requiring manual cleanup
C. The storage is automatically reused by the next PVC
D. The PVC deletion is blocked

**Correct answer: B**
*Explanation:* `Retain` preserves the underlying storage after PVC deletion, transitioning the PV to `Released` and requiring manual administrator action. A describes `Delete`. C and D do not reflect actual reclaim policy behavior.

---

**Q5.** What is the role of a CSI (Container Storage Interface) driver?
A. To implement pluggable Pod networking
B. To implement the actual provisioning and attaching of storage for a specific backend
C. To schedule Pods onto nodes with available storage
D. To enforce NetworkPolicies

**Correct answer: B**
*Explanation:* CSI drivers implement storage provisioning/attachment logic for specific backends, standardizing the interface much like CNI does for networking (A, which is incorrect for storage). C describes the scheduler's general role (Chapter 20), not CSI specifically. D describes NetworkPolicy enforcement (Chapter 18).

---

**Q6.** What is the defining characteristic of an `emptyDir` Volume?
A. It persists independently of the Pod's lifecycle
B. It is temporary scratch space, deleted along with the Pod
C. It can only be mounted read-only
D. It requires a StorageClass to function

**Correct answer: B**
*Explanation:* Per Section 4.1, `emptyDir` is basic, Pod-lifecycle-scoped scratch space — gone when the Pod is deleted. A describes PV-backed storage instead. C and D misstate its actual requirements/behavior.

---

**Q7.** Why is `hostPath` generally discouraged for production workloads?
A. It is not supported by any Kubernetes version
B. It ties a Pod to a specific node and offers no real durability guarantee across rescheduling
C. It only works with StatefulSets
D. It requires a CSI driver

**Correct answer: B**
*Explanation:* Section 4.1 and Section 15's common mistakes both flag this — `hostPath` mounts a specific node's local path, breaking if the Pod is rescheduled elsewhere. A is false; it's a supported but discouraged type. C and D misstate its actual constraints.

---

**Q8.** Per the Internal Working flow (Section 5), what does a Pod reference to use persistent storage — the PVC or the PV directly?
A. The PV directly, bypassing the PVC
B. The PVC, by name, in its volumes section — never the PV directly
C. Both must be referenced simultaneously
D. Neither; the StorageClass name is referenced directly

**Correct answer: B**
*Explanation:* Sections 4.3, 5, and 14's best practices are explicit and consistent: Pods always mount via the PVC, keeping the manifest portable across clusters/backends. A, C, and D contradict this core design principle.

---

**Q9.** What is the purpose of `volumeBindingMode: WaitForFirstConsumer` on a StorageClass?
A. It prevents any PV from ever being created
B. It delays PV provisioning until a Pod actually uses the PVC, ensuring storage is provisioned in the correct zone/node topology
C. It forces immediate provisioning at PVC creation time regardless of Pod placement
D. It disables dynamic provisioning entirely

**Correct answer: B**
*Explanation:* Per Section 9 and Section 14's best practices, this setting avoids provisioning storage in the wrong availability zone before the consuming Pod's placement is known. A and D are false — provisioning still happens, just delayed. C describes the opposite (default) behavior this setting avoids.

---

**Q10.** In the Architecture diagram (Section 6), what is the direct relationship between a StorageClass and a PV during dynamic provisioning?
A. The StorageClass is bound directly to a Pod
B. The StorageClass's provisioner creates the PV (and underlying cloud/network disk) on demand
C. The PV creates the StorageClass
D. There is no relationship; they operate independently

**Correct answer: B**
*Explanation:* Section 6's diagram shows the StorageClass acting as a factory, creating the PV and underlying disk when triggered by a PVC. A misattributes the binding relationship (that's PVC↔Pod and PVC↔PV). C reverses the actual dependency. D contradicts the entire dynamic provisioning model.

---

**Q11.** Why do cost optimization strategies (Section 13) use tiered StorageClasses?
A. Because Kubernetes requires exactly one StorageClass per cluster
B. Because cheaper HDD-backed classes can be used for infrequently accessed data, controlling storage spend versus always using fast-SSD-class storage
C. Because StorageClasses have no effect on cost
D. Because tiered StorageClasses are required for ReadWriteMany support

**Correct answer: B**
*Explanation:* Section 13 explicitly describes this real-world cost-optimization pattern — matching data access patterns to appropriately priced storage tiers. A is false — clusters commonly have multiple StorageClasses. C contradicts the stated purpose. D is unrelated to access modes.

---

**Q12.** Which real-world scenario specifically justifies using `ReadWriteMany` (Section 13)?
A. A single-replica database needing exclusive disk access
B. Shared file storage where multiple Pods across different nodes need to concurrently read/write the same files
C. A StatefulSet where each Pod needs its own dedicated, non-shared volume
D. An emptyDir volume used for temporary caching

**Correct answer: B**
*Explanation:* Section 13 gives this exact example — NFS-backed PVs with `ReadWriteMany` for concurrent, cross-node shared file access. A fits `ReadWriteOnce` instead. C describes the `volumeClaimTemplates` pattern from Chapter 14, which uses per-Pod (not shared) volumes. D is unrelated to persistent access modes.

---

**Q13.** A PVC requests `ReadWriteMany`, but the underlying storage backend only supports `ReadWriteOnce`. What is the most likely observed symptom, per the Common Mistakes and Troubleshooting sections (15, 16)?
A. The PVC is immediately bound anyway, ignoring the access mode mismatch
B. The PVC remains stuck in `Pending` status
C. The Pod starts normally but with read-only access
D. Kubernetes automatically downgrades the request to ReadWriteOnce

**Correct answer: B**
*Explanation:* Sections 15 and 16 both flag this exact scenario — an unsupported access mode request leaves the PVC unbound and stuck `Pending`. A, C, and D describe automatic-correction behaviors that don't occur; Kubernetes does not silently reinterpret the request.

---

**Q14.** What does a PV entering the `Released` state (Section 16's troubleshooting table) indicate?
A. The PV was successfully deleted
B. Its bound PVC was deleted, and with `reclaimPolicy: Retain`, it requires manual cleanup before reuse
C. The PV is actively bound and in use
D. The underlying disk has failed

**Correct answer: B**
*Explanation:* Per Section 16, `Released` specifically signals a former PVC binding has ended (Retain policy), leaving the PV present but not automatically reusable. A is false — the object still exists. C misstates `Released` as still-bound. D is an unrelated failure mode.

---

**Q15.** Per the Comparison Table in Section 17, what is the scope of a PersistentVolume (PV) object?
A. Pod-scoped
B. Namespace-scoped
C. Cluster-scoped
D. Node-scoped

**Correct answer: C**
*Explanation:* Section 17's table places PV at cluster scope, independent of any Pod, distinct from the namespaced PVC. A describes Volume. B describes PVC. D is not a real Kubernetes object scope used in this table.

---

**Q16.** Using the memory trick "PVC is the request, PV is the fulfillment, StorageClass is the factory that builds it on demand" (Section 18), which object corresponds to "the factory"?
A. Volume
B. PersistentVolumeClaim (PVC)
C. PersistentVolume (PV)
D. StorageClass

**Correct answer: D**
*Explanation:* The mnemonic explicitly assigns "factory that builds it on demand" to StorageClass, since it drives dynamic provisioning. A is unrelated to this analogy. B is "the request." C is "the fulfillment."

---

**Q17.** Per the deprecated `Recycle` reclaim policy entry in Section 17's table, what replaced it?
A. Nothing — `Recycle` is still the recommended default
B. Dynamic provisioning
C. `ReadWriteOncePod`
D. CSI snapshots

**Correct answer: B**
*Explanation:* Section 17 explicitly notes `Recycle` (a basic scrub-and-reuse mechanism) was replaced by the more capable dynamic provisioning model. A is false — it's deprecated. C and D are unrelated concepts covered elsewhere in the chapter.

---

**Q18.** A StatefulSet Pod (Chapter 14) is deleted and recreated on a different node. Per Section 5, step 7, and the cross-reference to Chapter 14, what happens to its bound storage?
A. A brand-new, empty PV is provisioned each time
B. It reattaches to the same PVC/PV, preserving data, regardless of which node it's rescheduled to
C. The data is lost since the Pod moved nodes
D. The StorageClass is deleted and must be manually recreated

**Correct answer: B**
*Explanation:* Section 5's step 7 explicitly describes this exact StatefulSet reattachment behavior — the PVC/PV binding, not node placement, determines data continuity. A, C, and D all describe behaviors that would defeat the entire purpose of PV/PVC decoupling from Pod lifecycle.

---

**Q19.** What CSI driver capability supports backup/restore workflows, per Section 13's real-world examples?
A. Automatic Pod rescheduling
B. Snapshot support for periodically snapshotting PVs
C. NetworkPolicy enforcement
D. DNS record management

**Correct answer: B**
*Explanation:* Section 13 explicitly cites CSI driver snapshot support as the mechanism enabling periodic PV backup/restore workflows. A, C, and D are unrelated capabilities belonging to other components (scheduler, CNI, CoreDNS respectively).

---

**Q20.** Following the best practice of setting `reclaimPolicy: Retain` for critical data (Section 14), what tradeoff does this introduce compared to `reclaimPolicy: Delete`?
A. No tradeoff — `Retain` is strictly better in every scenario
B. It trades automatic storage cleanup for a manual safety check before data is actually destroyed, potentially incurring ongoing storage costs until cleaned up
C. It disables dynamic provisioning entirely
D. It forces all future PVCs to use the same access mode

**Correct answer: B**
*Explanation:* This is precisely the tradeoff described in the hard interview Q3 and Section 17's reclaim policy table — safety against accidental data loss, at the cost of requiring manual cleanup (and potential ongoing billing) versus `Delete`'s automatic teardown. A ignores the real cost tradeoff. C and D are unrelated to reclaim policy's actual effect.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- Container filesystems are ephemeral; Kubernetes decouples durable storage needs via **Volumes**, **PersistentVolumes (PV)**, **PersistentVolumeClaims (PVC)**, and **StorageClasses**.
- Applications request storage via a **PVC**; Kubernetes binds it to a matching **PV**, or **dynamically provisions** one via a **StorageClass** and its (often CSI-based) provisioner.
- **Access modes** (RWO, ROX, RWX, RWOP) control how many nodes/Pods can mount a volume concurrently, and in what mode.
- **Reclaim policy** (`Retain` vs `Delete`) governs what happens to underlying storage after a PVC is deleted — a frequent source of unexpected storage costs or, conversely, unexpected data loss if misconfigured.

---

### Chapter Completion Checklist

1. **Topics covered:** Volumes, PersistentVolumes, PersistentVolumeClaims, StorageClasses, dynamic provisioning, access modes, reclaim policies, CSI.
2. **KCNA objectives completed:** Kubernetes storage abstractions.
3. **Remaining objectives:** Scheduling — how kube-scheduler places Pods onto nodes (Chapter 20).
4. **Suggested revision checklist:** Explain the PV/PVC/StorageClass relationship from memory; recite the four access modes; explain the difference between `Retain` and `Delete` reclaim policies.
5. **Suggested hands-on exercises:** Complete Lab 2 (delete/recreate a Pod, confirm data persistence via PVC) — the clearest demonstration of why PVs exist.
6. **Related chapters:** Previous: [18-Networking](../18-Networking/README.md). Next: [20-Scheduling](../20-Scheduling/README.md) — how Kubernetes decides which node runs which Pod.
