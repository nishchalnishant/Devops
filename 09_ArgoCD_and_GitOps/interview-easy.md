## Easy

**1. What is GitOps?**

GitOps is an operating model that uses Git as the single source of truth for declarative infrastructure and application configuration. Every desired state is committed to Git; an automated system continuously reconciles the actual state with what is in Git.

**2. What is the difference between push-based and pull-based CI/CD?**

In a push model, a CI pipeline is given cluster credentials and pushes changes by running `kubectl apply` or `helm upgrade` after a build. In a pull model, an agent (ArgoCD, Flux) runs inside the cluster and continuously polls a Git repository. When it detects drift between Git state and cluster state, it pulls and applies the changes. Credentials never leave the cluster.

**3. What is ArgoCD?**

ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes. It monitors Git repositories for changes to Kubernetes manifests and automatically (or on demand) applies them to the cluster. It provides a UI and CLI showing sync status, drift detection, and rollback capability.

**4. What is an ArgoCD Application?**

An `Application` is an ArgoCD custom resource that defines a source (Git repo + path + revision) and a destination (cluster + namespace). ArgoCD continuously compares the desired state in the source to the live state in the destination and reports sync status.

**5. What manifest formats does ArgoCD support?**

ArgoCD natively supports: raw Kubernetes YAML/JSON, Helm charts, Kustomize overlays, and Jsonnet. It also supports custom config management plugins for other templating tools.

**6. What is drift detection in ArgoCD?**

Drift occurs when the live cluster state diverges from the state declared in Git — usually caused by manual `kubectl` edits. ArgoCD continuously compares live and desired state; when they differ, the Application shows as `OutOfSync`. ArgoCD can be configured to alert or auto-sync to correct drift.

---

