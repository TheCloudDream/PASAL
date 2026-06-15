
# Docker Restart Policies

## Objective

Configure Docker containers to automatically recover from failures and system reboots.

---

## Why Restart Policies Matter

Containers can stop unexpectedly due to:

* Application crashes
* Runtime errors
* Host system reboots
* Resource exhaustion

Without a restart policy:

```text
Container Stops
      ↓
Application Offline
```

With a restart policy:

```text
Container Stops
      ↓
Docker Detects Failure
      ↓
Container Restarts Automatically
```

This provides a basic level of self-healing for containerized applications.

---

## Restart Policy Used

For the PASAL project, the following restart policy was selected:

```yaml
restart: unless-stopped
```

### Behavior

| Scenario                    | Result                |
| --------------------------- | --------------------- |
| Container crashes           | Restart automatically |
| Docker daemon restarts      | Restart automatically |
| Host machine reboots        | Restart automatically |
| Manual stop (`docker stop`) | Remains stopped       |

---

## Services Configured

The restart policy was applied to:

* Backend (FastAPI)
* Frontend (Nginx)
* PostgreSQL
* Redis

Example:

```yaml
backend:
  container_name: pasal-backend
  restart: unless-stopped
```

---

## Why `unless-stopped` Was Chosen

Docker supports several restart policies:

| Policy         | Description                            |
| -------------- | -------------------------------------- |
| no             | Never restart                          |
| on-failure     | Restart only after failures            |
| always         | Always restart, even after manual stop |
| unless-stopped | Restart unless explicitly stopped      |

For development and homelab environments, `unless-stopped` provides the best balance between availability and control.

---

## Verification

After applying the restart policy:

```bash
docker compose up -d
```

Verify:

```bash
docker inspect pasal-backend --format='{{.HostConfig.RestartPolicy.Name}}'
```

Expected output:

```text
unless-stopped
```

---

## Practical Example

If the backend container crashes:

```text
FastAPI Error
      ↓
Container Exits
      ↓
Docker Detects Failure
      ↓
Container Restarts
```

Users experience minimal downtime.

---

## Relation to Kubernetes

Docker restart policies introduce the concept of self-healing.

Later in Kubernetes:

```text
Docker Restart Policy
          ↓
Kubernetes Restart Policy
          ↓
Liveness Probes
          ↓
Self-Healing Pods
```

Understanding restart policies helps build a foundation for Kubernetes workload management.

---

## Learning Outcome

After completing this task:

* Learned the purpose of restart policies
* Configured automatic container recovery
* Verified Docker restart behavior
* Prepared for Kubernetes self-healing concepts
