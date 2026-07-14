# 15 — Jobs and CronJobs

## 1. Learning Objectives

By the end of this chapter you will be able to:

- Explain why some workloads need to **run to completion** instead of running forever.
- Explain how a Job differs from a Deployment/ReplicaSet in its success/failure model.
- Configure `completions`, `parallelism`, and `backoffLimit` for a Job.
- Explain how a CronJob schedules Jobs on a recurring basis.
- Read and write complete Job and CronJob manifests.

**KCNA objectives covered:** Kubernetes Fundamentals domain — run-to-completion workloads, completing the workload-controller family alongside Deployments (Ch.12), DaemonSets (Ch.13), and StatefulSets (Ch.14).

---

## 2. Historical Background

Every controller covered so far (ReplicaSet, Deployment, DaemonSet, StatefulSet) is designed around Pods that should run **indefinitely** — if a Pod exits, it's treated as a failure to be restarted. But plenty of real workloads are the opposite: a batch report generator, a database migration script, a nightly backup — these are supposed to run once, finish, and stop. Before Kubernetes had a dedicated object for this, people either abused Deployments (which kept restarting "completed" Pods forever, since a Deployment doesn't understand the concept of "done") or ran such tasks entirely outside the cluster via external cron daemons on a manually managed VM. Kubernetes introduced the **Job** to represent finite, run-to-completion work, and the **CronJob** to schedule Jobs on a recurring time-based schedule — bringing traditional Unix `cron` semantics natively into the cluster.

---

## 3. Motivation: Why Do Jobs and CronJobs Exist?

**Analogy — The Factory's Production Run vs Assembly Line:**
An assembly line (a Deployment) runs continuously, forever, producing output as long as the factory is open — if a worker station stops, the line manager replaces the worker immediately because the line is never supposed to stop. But a **special production run** — say, manufacturing exactly 500 units of a custom order — is different: once 500 units are done, the run is **finished**, and restarting the machine would be wrong, not right. A **Job** is that special production run: it's declared successful once its work is done, and Kubernetes stops trying to "fix" it by restarting.

A **CronJob** is the factory's shift schedule board: "run the special production run every night at 2 AM" — it doesn't run continuously; it creates a new Job automatically at each scheduled time.

### 3.1 How Was This Solved Before Kubernetes?

Batch and scheduled tasks ran via traditional `cron` daemons on dedicated VMs, or in separate batch-processing systems entirely outside the container orchestration layer — meaning batch workloads couldn't share the same scheduling, resource limits, scaling, and observability tooling as the rest of the application fleet.

### 3.2 How Kubernetes Solves It

A **Job** creates one or more Pods and tracks them until a specified number complete **successfully** — unlike a Deployment, a Job understands the concept of "done" and does not restart successfully completed Pods. A **CronJob** wraps a Job template with a schedule (in standard cron syntax), automatically creating a new Job at each scheduled time.

---

## 4. Core Concepts

### 4.1 Job vs Deployment — Different Success Models

| Aspect | Deployment | Job |
|---|---|---|
| Pod exits successfully (exit code 0) | Treated as failure — Pod is restarted to keep desired replica count running | Treated as **success** — Pod is not restarted |
| Intended lifetime | Forever (until scaled down or deleted) | Finite — until the specified number of completions is reached |
| Use case | Web servers, APIs — always-on services | Batch jobs, migrations, one-off scripts, data processing |

### 4.2 Key Job Spec Fields

| Field | Meaning |
|---|---|
| `completions` | Total number of successful Pod completions required for the Job to be considered done |
| `parallelism` | Maximum number of Pods allowed to run concurrently at once |
| `backoffLimit` | Number of retries allowed before the Job is marked as failed |
| `activeDeadlineSeconds` | Maximum wall-clock time the Job is allowed to run before being terminated |
| `restartPolicy` | Must be `OnFailure` or `Never` for Job Pods (never `Always` — that would contradict "run to completion") |

### 4.3 Job Patterns

| Pattern | `completions` / `parallelism` | Use Case |
|---|---|---|
| Single Pod | `completions: 1`, `parallelism: 1` (defaults) | One-off task, e.g., a single migration script |
| Fixed completion count | `completions: 5`, `parallelism: 2` | Process a known number of work items, 2 at a time |
| Work queue | `completions` unset, `parallelism: N` | Pods pull from a shared external queue until it's empty, then exit successfully |

### 4.4 CronJob Scheduling

A CronJob uses standard cron syntax (`minute hour day-of-month month day-of-week`) to determine when to create a new Job from its template. For example, `0 2 * * *` means "every day at 2:00 AM."

| Field | Meaning |
|---|---|
| `schedule` | Standard cron expression for when to create a new Job |
| `jobTemplate` | The Job spec to instantiate at each scheduled time |
| `concurrencyPolicy` | `Allow` (default, run concurrently), `Forbid` (skip if previous still running), `Replace` (cancel previous, start new) |
| `startingDeadlineSeconds` | How late a missed schedule can still be started before being skipped |
| `successfulJobsHistoryLimit` / `failedJobsHistoryLimit` | How many old completed/failed Jobs to retain for inspection |

---

## 5. Internal Working

```
1. A Job object is submitted with completions: 3, parallelism: 2
        ↓
2. Job controller creates 2 Pods immediately (parallelism limit)
        ↓
3. As each Pod completes SUCCESSFULLY, the controller creates a
   replacement Pod, until 3 total successful completions are reached
        ↓
4. A Pod that fails is retried according to backoffLimit; each retry
   uses exponential backoff delay
        ↓
5. Once 3 Pods have completed successfully, the Job is marked
   Complete — no further Pods are created, and existing successful
   Pods are NOT deleted (for log inspection) unless explicitly cleaned up
```

**CronJob flow:**

```
1. CronJob's schedule (e.g., "0 2 * * *") is evaluated by the
   CronJob controller every tick
        ↓
2. When the schedule time arrives, the controller creates a new
   Job object from jobTemplate
        ↓
3. That Job runs through the normal Job lifecycle (Section 5, above)
        ↓
4. Old Jobs are retained per successfulJobsHistoryLimit /
   failedJobsHistoryLimit, then garbage collected
```

---

## 6. Architecture

```
CronJob "nightly-backup"  (schedule: "0 2 * * *")
        │
        │ creates, at 2 AM each day
        ▼
   Job "nightly-backup-28392034"
        │
        │ creates Pods per completions/parallelism
        ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Pod (ok) │   │ Pod (ok) │   │ Pod(fail)│──▶ retried per backoffLimit
   └─────────┘   └─────────┘   └─────────┘
        │
        ▼
   Job marked "Complete" once completions target is met
```

---

## 7. Component Breakdown

| Piece | Role |
|---|---|
| Job object | Manages Pods that must run to successful completion, not indefinitely |
| CronJob object | Creates Jobs automatically on a recurring cron schedule |
| Job controller | Tracks successful/failed completions, applies backoff and parallelism limits |
| CronJob controller | Evaluates the schedule and creates new Job objects at the right time |

---

## 8. Important Terminology

| Term | Meaning |
|---|---|
| Job | Controller that runs Pods to successful completion, then stops |
| CronJob | Controller that creates Jobs on a recurring cron schedule |
| Completions | Number of successful Pod completions required |
| Parallelism | Max concurrent Pods for a Job |
| backoffLimit | Retry limit before a Job is marked failed |
| concurrencyPolicy | Rule for handling overlapping CronJob-triggered Job runs |

---

## 9. YAML Deep Dive

**Job:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  completions: 3
  parallelism: 2
  backoffLimit: 4
  activeDeadlineSeconds: 300
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: migrate
          image: migrate-tool:1.0
          command: ["./run-migration.sh"]
```

**CronJob:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: backup-tool:1.0
              command: ["./backup.sh"]
```

---

## 10. kubectl Commands

| Command | Purpose | Example |
|---|---|---|
| `kubectl get jobs` | List Jobs | `kubectl get jobs` |
| `kubectl get cronjobs` | List CronJobs | `kubectl get cronjobs` |
| `kubectl create job --from=cronjob/<name>` | Manually trigger a Job from a CronJob template right now | `kubectl create job manual-run --from=cronjob/nightly-backup` |
| `kubectl logs job/<name>` | View logs of a Job's Pod(s) | `kubectl logs job/db-migration` |
| `kubectl delete job <name>` | Delete a Job (and its Pods, by default) | `kubectl delete job db-migration` |

---

## 11. Hands-on Examples

**Lab 1 — Run a simple Job to completion:**
```bash
kubectl apply -f db-migration-job.yaml
kubectl get jobs -w
# STATUS moves to "Complete" once completions target is reached
kubectl logs job/db-migration
```

**Lab 2 — Observe backoffLimit retry behavior:**
```bash
# Deploy a Job whose container deliberately exits with code 1
kubectl apply -f failing-job.yaml
kubectl get pods -w
# Watch failed Pods retried with exponential backoff, up to backoffLimit,
# then the Job is marked "Failed"
```

**Lab 3 — Manually trigger a CronJob immediately:**
```bash
kubectl create job manual-test --from=cronjob/nightly-backup
kubectl get jobs
# A Job is created right now, without waiting for the schedule
```

---

## 12. Internal Flow

See Section 5 — Jobs use a modified reconciliation loop (building on Chapter 06's general pattern) that tracks a **completion count** rather than a fixed always-desired replica count, and CronJobs add a **time-based trigger** layer on top that periodically creates new Job objects rather than continuously reconciling a single long-lived object.

---

## 13. Real-World Examples

1. **Database migrations** run once during a deployment rollout, using a Job to guarantee the migration script runs to completion exactly the required number of times.
2. **Nightly backups** use a CronJob scheduled at low-traffic hours (e.g., `0 2 * * *`) to back up databases or persistent volumes automatically.
3. **Report generation** batch jobs (e.g., generating a daily sales report) run via CronJob, with results pushed to storage or emailed on completion.
4. **Data processing pipelines** (e.g., processing a batch of uploaded files) use a Job with `parallelism` to process multiple files concurrently, each Pod pulling from a shared work queue.
5. **Certificate renewal / cleanup tasks** run periodically via CronJob to renew TLS certificates or clean up expired resources across the cluster.

---

## 14. Best Practices

- Always set `activeDeadlineSeconds` for Jobs to prevent a stuck or hung task from running forever and consuming resources.
- Set `concurrencyPolicy: Forbid` for CronJobs whose Job runs must never overlap (e.g., a backup that shouldn't run twice at once).
- Set reasonable `successfulJobsHistoryLimit` / `failedJobsHistoryLimit` values — too high wastes etcd storage with old completed Job objects, too low loses useful debugging history.
- Use `restartPolicy: OnFailure` (rather than `Never`) when you want failed Pods retried in-place rather than replaced with fresh Pods, keeping the Job's Pod count leaner.

---

## 15. Common Mistakes

- Using a Deployment for a task that should run once and finish, causing Kubernetes to endlessly try to restart a Pod that has already done its job (since a Deployment doesn't understand "completion").
- Forgetting `activeDeadlineSeconds`, letting a hung Job run indefinitely and consume cluster resources.
- Not setting `concurrencyPolicy`, leading to overlapping CronJob runs colliding on shared resources (e.g., two backup Jobs writing to the same file simultaneously).
- Setting `restartPolicy: Always` on a Job Pod — this is invalid and contradicts the entire run-to-completion model; Job Pods must use `OnFailure` or `Never`.

---

## 16. Troubleshooting

| Symptom | Likely Cause | Debugging Commands | Fix |
|---|---|---|---|
| Job never reaches "Complete" | Pods keep failing, retried up to `backoffLimit`, then Job fails | `kubectl describe job`, `kubectl logs` | Fix underlying script/container error causing failure |
| CronJob never creates any Jobs | Invalid cron `schedule` syntax, or `startingDeadlineSeconds` too short | `kubectl describe cronjob` | Correct the cron expression; adjust deadline |
| Two CronJob-triggered Jobs overlap unexpectedly | `concurrencyPolicy: Allow` (default) permits overlap | `kubectl get jobs` | Set `concurrencyPolicy: Forbid` or `Replace` |
| Job Pods keep getting recreated forever | Deployment used instead of Job for a finite task | `kubectl get deploy`, `kubectl describe deploy` | Convert the workload to a Job |

---

## 17. Comparison Tables

**Job vs CronJob:**

| Aspect | Job | CronJob |
|---|---|---|
| Trigger | Created directly, runs once to completion | Created automatically on a recurring schedule |
| Use case | One-off batch task | Recurring batch task (nightly, hourly, etc.) |
| Underlying mechanism | Manages Pods directly | Creates Job objects, which then manage Pods |

**Job vs Deployment (recap of Section 4.1):**

| Aspect | Job | Deployment |
|---|---|---|
| Pod exit (success) | Job considered complete, no restart | Pod restarted to maintain replica count |
| Lifespan | Finite | Indefinite |

---

## 18. Memory Tricks

- **"Job = factory's special production run, CronJob = shift schedule board."**
- **"Deployment doesn't know the word 'done'; Job's entire purpose is knowing the word 'done.'"**
- Field mnemonic: **"Completions = how many, Parallelism = how many at once, backoffLimit = how many retries."**

---

## 19. Interview Questions

**Easy:**
1. How does a Job's handling of a successfully exited Pod differ from a Deployment's?
   *Expected answer:* A Deployment treats any Pod exit — success or failure — as a deviation from the desired "always running" state and restarts it. A Job treats a successful exit (exit code 0) as the intended outcome — the Pod is not restarted, and the Job counts it toward its required `completions`.

**Medium:**
2. What is the purpose of `backoffLimit`, and what happens once it's exceeded?
   *Expected answer:* `backoffLimit` caps how many times a Job will retry a failing Pod (with exponential backoff delay between retries) before giving up. Once exceeded, the Job is marked as `Failed` and no further retries are attempted, requiring manual investigation and intervention.

**Hard:**
3. A CronJob scheduled to run every 5 minutes occasionally has Job runs that take longer than 5 minutes to finish. What could go wrong with the default configuration, and how would you prevent it?
   *Expected answer:* With the default `concurrencyPolicy: Allow`, if a Job run takes longer than the schedule interval, a new Job will be created and start running concurrently with the still-in-progress previous one — potentially causing resource contention, duplicate work, or data corruption if both instances write to the same external resource. To prevent this, set `concurrencyPolicy: Forbid` (skip creating a new Job if the previous one is still running) or `Replace` (cancel the still-running Job and start the new one), depending on which behavior is safe for the specific workload. Additionally, `activeDeadlineSeconds` can be used to cap how long any single run is allowed to take, preventing runaway executions in the first place.

---

## 20. KCNA Practice Questions

**Q1.** What is the primary purpose of a Kubernetes Job?
A. To run a Pod indefinitely and restart it on any exit
B. To run Pods to successful completion a specified number of times, then stop
C. To schedule Pods to run at a recurring time
D. To ensure one Pod runs per node in the cluster

**Correct answer: B**
*Explanation:* A Job's defining behavior is tracking successful completions and stopping once the target is reached — unlike a Deployment (A), which always restarts exited Pods. C describes a CronJob, not a Job itself. D describes a DaemonSet (Chapter 13).

---

**Q2.** What object is responsible for creating Jobs on a recurring, time-based schedule?
A. Deployment
B. ReplicaSet
C. CronJob
D. StatefulSet

**Correct answer: C**
*Explanation:* A CronJob wraps a Job template with a cron schedule and automatically creates new Job objects at each scheduled time. A, B, and D are unrelated to time-based scheduling.

---

**Q3.** In a Job spec, what does the `parallelism` field control?
A. The total number of successful completions required
B. The maximum number of Pods allowed to run concurrently
C. The number of retries allowed before the Job fails
D. The maximum time the Job is allowed to run

**Correct answer: B**
*Explanation:* `parallelism` caps concurrent Pod execution. A describes `completions`. C describes `backoffLimit`. D describes `activeDeadlineSeconds`.

---

**Q4.** Which `restartPolicy` values are valid for a Job's Pod template?
A. `Always` only
B. `OnFailure` or `Never`
C. `Always` or `Never`
D. Any value is valid, including `Always`

**Correct answer: B**
*Explanation:* Job Pods must use `OnFailure` or `Never` since `Always` would contradict the run-to-completion model (a Pod that exits successfully must not be restarted). A, C, and D incorrectly include `Always` as valid.

---

**Q5.** A CronJob has `concurrencyPolicy: Forbid`. What happens if a new scheduled run is due while the previous Job triggered by this CronJob is still running?
A. The new Job is created and runs alongside the old one
B. The new Job's run is skipped until the current one finishes
C. The old Job is immediately terminated and replaced
D. The CronJob is deleted automatically

**Correct answer: B**
*Explanation:* `Forbid` skips creating a new Job if the previous one hasn't finished yet, preventing overlapping runs. A describes `Allow` (the default). C describes `Replace`. D does not occur.

---

**Q6.** What does the `completions` field specify in a Job spec?
A. The maximum number of Pods that can run at once
B. The total number of successful Pod completions required for the Job to be done
C. The number of retries allowed before failing
D. The maximum wall-clock runtime allowed

**Correct answer: B**
*Explanation:* `completions` is the success target the Job controller tracks until reached. A describes `parallelism`, C describes `backoffLimit`, and D describes `activeDeadlineSeconds` (Section 4.2).

---

**Q7.** What is the purpose of `activeDeadlineSeconds` on a Job?
A. To set how many Pods run concurrently
B. To cap the total wall-clock time the Job is allowed to run before being terminated
C. To specify how many old Jobs to retain in history
D. To define the cron schedule for recurring execution

**Correct answer: B**
*Explanation:* `activeDeadlineSeconds` prevents a hung or stuck Job from running (and consuming resources) forever (Sections 4.2 and 14's best practices). A describes `parallelism`. C describes the history-limit fields. D applies to CronJob's `schedule`, not a bare Job.

---

**Q8.** In the "work queue" Job pattern (Section 4.3), how do Pods know when to stop?
A. Kubernetes automatically kills them after a fixed timeout
B. Each Pod pulls from a shared external queue and exits successfully once the queue is empty, with no fixed `completions` count set
C. `completions` must always be set to the number of queue items
D. The CronJob controller signals when to stop

**Correct answer: B**
*Explanation:* The work-queue pattern deliberately leaves `completions` unset — Pods self-determine completion by observing the shared queue is empty. A misdescribes the mechanism (no automatic timeout kill for this reason). C contradicts the pattern's point (unknown/dynamic item count). D confuses CronJob with Job Pod behavior.

---

**Q9.** What cron schedule expression means "every day at 2:00 AM," as used in Section 4.4?
A. `2 0 * * *`
B. `0 2 * * *`
C. `* * 2 0 *`
D. `0 0 * * 2`

**Correct answer: B**
*Explanation:* Standard cron order is `minute hour day-of-month month day-of-week`, so `0 2 * * *` means minute 0, hour 2, every day. A swaps minute/hour. C and D scramble the field order/meaning entirely.

---

**Q10.** Why does `successfulJobsHistoryLimit` exist, and what's the tradeoff of setting it too high?
A. It controls parallelism; too high slows down Job execution
B. It retains a number of old completed Job objects for inspection/debugging; too high wastes etcd storage with old objects
C. It sets how many retries are allowed; too high risks infinite retries
D. It has no practical tradeoff — always set it as high as possible

**Correct answer: B**
*Explanation:* Per Section 14's best practices, retaining completed Job objects aids debugging but consumes etcd storage if kept indefinitely, requiring a balanced limit. A misattributes this to parallelism. C describes `backoffLimit`. D ignores the explicitly stated tradeoff.

---

**Q11.** A team runs a batch task as a Deployment instead of a Job. What symptom will they most likely observe?
A. The Deployment will refuse to start any Pods
B. Completed Pods are continuously restarted because the Deployment doesn't recognize "successful completion" as a valid end state
C. The task will run exactly once, then the Deployment will delete itself
D. The Deployment will automatically convert itself into a Job

**Correct answer: B**
*Explanation:* This is the classic anti-pattern from Section 15 (Common Mistakes) and the Section 16 troubleshooting table — a Deployment always tries to maintain running replicas, restarting Pods that exit even successfully. A, C, and D describe behaviors that do not occur.

---

**Q12.** Why must a Job's Pod template use `restartPolicy: OnFailure` or `Never`, and never `Always`?
A. `Always` is simply not a recognized Kubernetes value anywhere
B. `Always` would contradict the Job's run-to-completion model, since a successfully completed Pod must not be restarted
C. `Always` is reserved exclusively for StatefulSets
D. `Always` causes the Job controller to crash on validation

**Correct answer: B**
*Explanation:* This is explicitly called out in Sections 4.2 and 15 — `Always` is valid elsewhere (e.g., regular Pod specs) but is semantically incompatible with a Job's success model. A is false — `Always` is a valid `restartPolicy` value in other contexts. C is false; it's not StatefulSet-exclusive. D overstates the failure mode (it's a validation rejection, not a crash).

---

**Q13.** What is the difference between `restartPolicy: OnFailure` and `Never` for a failed Job Pod?
A. There is no difference; they behave identically
B. `OnFailure` restarts the failed container in place within the same Pod; `Never` creates a brand-new replacement Pod instead
C. `OnFailure` deletes the Job immediately; `Never` retries indefinitely
D. `OnFailure` is only valid for CronJobs, not Jobs

**Correct answer: B**
*Explanation:* Per Section 14's best practices, `OnFailure` retries in-place (keeping Pod count leaner), while `Never` results in the Job controller creating new Pods for each retry attempt. A is false — they differ in retry mechanics. C and D misstate their behavior and scope.

---

**Q14.** A CronJob's `startingDeadlineSeconds` is set to 100. If the CronJob controller is down for 5 minutes and misses a scheduled run, what happens?
A. The missed run always executes immediately once the controller recovers, regardless of delay
B. If the missed run falls further behind than 100 seconds, it is counted as a missed schedule and skipped rather than run late
C. `startingDeadlineSeconds` has no effect on missed schedules
D. The CronJob is automatically deleted after a missed schedule

**Correct answer: B**
*Explanation:* `startingDeadlineSeconds` (Section 4.4) bounds how late a missed run can still start; beyond that window, it's treated as skipped rather than run arbitrarily late. A contradicts the deadline's purpose. C and D misstate the field's effect and consequence.

---

**Q15.** Which Job pattern fits "process a known number of 5 work items, 2 at a time"?
A. `completions: 5`, `parallelism: 2`
B. `completions: 2`, `parallelism: 5`
C. `completions` unset, `parallelism: 5`
D. `completions: 1`, `parallelism: 1`

**Correct answer: A**
*Explanation:* Per Section 4.3's fixed-completion-count pattern, `completions` sets the total required successes (5) and `parallelism` caps concurrency (2 at a time). B swaps the values incorrectly. C describes the work-queue pattern instead. D describes the single-Pod pattern.

---

**Q16.** What is the underlying mechanism relationship between a CronJob and a Job?
A. A CronJob directly manages Pods itself, bypassing Jobs entirely
B. A CronJob creates Job objects on a schedule, and those Job objects then manage the actual Pods
C. A Job creates CronJobs dynamically at runtime
D. CronJobs and Jobs are entirely unrelated objects with no interaction

**Correct answer: B**
*Explanation:* Per Section 17's comparison table, a CronJob's role is purely scheduling — it creates Job objects, which then handle Pod-level completion tracking and retries themselves. A inverts the actual layering. C reverses the relationship. D contradicts the entire chapter's premise.

---

**Q17.** A Job with `backoffLimit: 4` has failed on all 4 retry attempts. What is the Job's final status?
A. It keeps retrying indefinitely beyond the limit
B. It is marked `Failed`, and no further retries are attempted
C. It is automatically converted into a CronJob
D. It silently succeeds regardless of the failures

**Correct answer: B**
*Explanation:* Per Section 19's interview Q2, exceeding `backoffLimit` marks the Job `Failed` and halts further retry attempts, requiring manual investigation. A contradicts the defined limit's purpose. C and D describe behaviors that do not occur.

---

**Q18.** Using the chapter's factory analogy (Section 3), what does a CronJob represent?
A. The assembly line itself, running forever
B. The factory's shift schedule board, triggering a new production run at specified times
C. A single worker station on the assembly line
D. The final shipped product

**Correct answer: B**
*Explanation:* The analogy explicitly maps CronJob to the shift-schedule board that triggers new production runs (Jobs) at set times. A describes a Deployment/ReplicaSet instead. C and D don't correspond to any controller-level concept in the analogy.

---

**Q19.** Why are successfully completed Job Pods NOT automatically deleted once the Job reaches `Complete` status?
A. Kubernetes lacks the capability to delete completed Pods
B. They are retained deliberately so their logs remain available for inspection, unless explicitly cleaned up
C. Deleting them would cause the Job to restart
D. Completed Pods are automatically converted into CronJobs

**Correct answer: B**
*Explanation:* Per Section 5's internal working flow, successful Pods are kept around specifically to allow log/debugging inspection after the fact — cleanup is a separate, explicit step. A is false — Kubernetes can delete Pods; this is a deliberate choice. C and D describe behaviors that do not occur.

---

**Q20.** A CronJob scheduled every 5 minutes has runs that occasionally take 7 minutes. With the default `concurrencyPolicy: Allow`, what risk does this create?
A. No risk — Allow silently prevents any overlap automatically
B. A new Job may start before the previous one finishes, causing concurrent runs that can contend for shared resources or duplicate work
C. The CronJob will automatically switch to `Forbid` after detecting the overlap
D. The overrunning Job is forcibly killed the moment the next schedule fires

**Correct answer: B**
*Explanation:* This is the exact scenario from Section 19's interview Q3 — `Allow` (the default) permits overlapping runs, risking contention or duplicated work unless `Forbid`/`Replace` or `activeDeadlineSeconds` is used to prevent it. A contradicts what `Allow` actually does. C and D describe behaviors that do not occur automatically.

---

## 21. Chapter Summary (One-Page Revision Sheet)

- A **Job** runs Pods to successful completion a specified number of times (`completions`), optionally with limited concurrency (`parallelism`), and stops — unlike a Deployment, which always restarts exited Pods.
- `backoffLimit` caps retries before a Job is marked `Failed`; `activeDeadlineSeconds` caps total run time.
- A **CronJob** creates Jobs automatically on a recurring cron `schedule`; `concurrencyPolicy` (`Allow`/`Forbid`/`Replace`) controls overlapping runs.
- Job Pods must use `restartPolicy: OnFailure` or `Never` — never `Always`.
- Classic use cases: database migrations, nightly backups, report generation, batch data processing, periodic cleanup tasks.

---

### Chapter Completion Checklist

1. **Topics covered:** Job completion/parallelism/backoff model, CronJob scheduling and concurrency policy.
2. **KCNA objectives completed:** Run-to-completion workloads, completing the full workload-controller family (ReplicaSet, Deployment, DaemonSet, StatefulSet, Job/CronJob).
3. **Remaining objectives:** Networking — Services (Chapter 16).
4. **Suggested revision checklist:** Recite the Job vs Deployment success-model difference from memory; explain `concurrencyPolicy` options; explain why Job Pods can't use `restartPolicy: Always`.
5. **Suggested hands-on exercises:** Complete Lab 2 (backoffLimit retry behavior) — seeing exponential backoff retries firsthand makes the failure model concrete.
6. **Related chapters:** Previous: [14-StatefulSets](../14-StatefulSets/README.md). Next: [16-Services](../16-Services/README.md) — how Pods are exposed and discovered on the network.
