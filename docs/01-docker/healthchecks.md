
# Docker Health Checks

## Objective

Implement health checks for PASAL services to allow Docker to determine whether containers are functioning correctly.

---

## Why Health Checks Matter

A running container is not necessarily a healthy container.

Without health checks:

```text
Container Running
      ≠
Application Working
```

Examples:

* FastAPI process started but API is unresponsive
* PostgreSQL process running but not accepting connections
* Redis process started but not responding

Health checks allow Docker to monitor service availability and report container health status.

---

## Services Covered

| Service           | Health Check Method                |
| ----------------- | ---------------------------------- |
| Backend (FastAPI) | HTTP request to `/health` endpoint |
| PostgreSQL        | `pg_isready`                       |
| Redis             | `redis-cli ping`                   |

---

## Backend Health Check

### Configuration

```yaml
healthcheck:
  test:
    [
      "CMD",
      "python",
      "-c",
      "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
    ]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

### Explanation

Docker executes a Python command inside the container.

The command sends an HTTP request to:

```text
http://localhost:8000/health
```

If the endpoint responds successfully:

```text
healthy
```

Otherwise:

```text
unhealthy
```

---

## PostgreSQL Health Check

### Configuration

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 30s
  timeout: 10s
  retries: 5
```

### Explanation

The PostgreSQL utility `pg_isready` verifies whether the database is accepting connections.

---

## Redis Health Check

### Configuration

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Explanation

Redis responds with:

```text
PONG
```

If the server is healthy.

---

## Verification

Rebuild and start the containers:

```bash
docker compose down
docker compose up -d --build
```

Check health status:

```bash
docker compose ps
```

Expected output:

```text
pasal-backend    running (healthy)
pasal-postgres   running (healthy)
pasal-redis      running (healthy)
```

---

## Troubleshooting

### Backend marked unhealthy

Possible causes:

* Missing `/health` endpoint
* Application startup failure
* Incorrect health check URL

### PostgreSQL marked unhealthy

Possible causes:

* Incorrect database credentials
* Database initialization still in progress

### Redis marked unhealthy

Possible causes:

* Redis service failed to start
* Redis port conflicts

---

## Learning Outcome

After completing this task:

* Learned the purpose of Docker health checks
* Implemented service health monitoring
* Verified container readiness
* Prepared the project for future Kubernetes readiness and liveness probes
