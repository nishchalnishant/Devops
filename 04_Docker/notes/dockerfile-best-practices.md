---
description: Dockerfile best practices, multi-stage builds, layer caching, image hardening, and build optimization for senior engineers.
---

# Docker — Dockerfile Best Practices & Image Optimization

## The Problem with Naive Dockerfiles

```dockerfile
# NAIVE — 1.2GB image, slow builds, security risks
FROM python:3.11
COPY . /app
RUN pip install -r requirements.txt
CMD python /app/main.py
```

Problems:
- Full Python image includes gcc, make, development headers (not needed at runtime)
- Copying `.git`, `node_modules`, `__pycache__` into image
- Running as root
- No layer cache optimization (re-installs deps on every code change)

***

## Multi-Stage Builds — The Gold Standard

```dockerfile
# Stage 1: Builder — has all build tools
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first (cache layer optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime — lean, minimal attack surface
FROM python:3.11-slim AS runtime

# Security: create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Security hardening
USER appuser

# Document the port (doesn't publish it)
EXPOSE 8080

# Use exec form — receives signals directly, not via shell
CMD ["/home/appuser/.local/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Result:** 120MB vs 1.2GB. No build tools in production image.

***

## Layer Caching — The Most Impactful Optimization

Docker caches each layer. If a layer's instruction or its input files change, that layer **and all subsequent layers** are invalidated.

```dockerfile
# BAD — requirements reinstalled on every code change
COPY . /app
RUN pip install -r /app/requirements.txt

# GOOD — requirements cached independently from code
COPY requirements.txt .           # Changes rarely → cached most of the time
RUN pip install -r requirements.txt
COPY src/ ./src/                  # Changes often → only this layer rebuilds
```

### BuildKit Cache Mounts (Next-Level Caching)

```dockerfile
# Cache pip download cache ACROSS builds (persists on host)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache apt packages across builds
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl
```

**Enable BuildKit:**
```bash
DOCKER_BUILDKIT=1 docker build .
# Or permanently in daemon.json:
# { "features": { "buildkit": true } }
```

***

## `.dockerignore` — What NOT to Send to Build Context

```
# .dockerignore
.git
.github
.gitignore
**/__pycache__
**/*.pyc
**/.pytest_cache
node_modules
dist
*.log
.env
.env.*
terraform.tfstate
*.tfvars
docs/
tests/
README.md
```

Without `.dockerignore`, Docker sends the entire directory to the build daemon — including your `.git` folder and all test files.

***

## Image Hardening Checklist

```dockerfile
# 1. Use specific version tags (never :latest)
FROM python:3.11.9-slim-bookworm

# 2. Run as non-root
RUN useradd --create-home appuser
USER appuser

# 3. Read-only root filesystem (enforced at runtime)
# docker run --read-only --tmpfs /tmp my-image

# 4. No SUID/SGID binaries
RUN find / -perm /4000 -type f -exec chmod a-s {} \; 2>/dev/null || true

# 5. No package manager in runtime image
# (use multi-stage; don't install apt in final stage)

# 6. Use COPY not ADD (ADD has implicit URL and tar extraction)
COPY config.yml /app/config.yml   # GOOD
ADD https://example.com/file.tar  # BAD — implicit behavior

# 7. Pin pip/npm versions
RUN pip install pip==24.0 && pip install -r requirements.txt
```

***

## Node.js Example — Full Production Dockerfile

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production   # ci = clean install, no lockfile changes

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build              # TypeScript compile, webpack, etc.

# Stage 3: Runtime
FROM node:20-alpine AS runtime
RUN apk add --no-cache dumb-init    # Proper init for signal handling

WORKDIR /app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

COPY --from=deps --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist

ENTRYPOINT ["dumb-init", "--"]    # dumb-init is a minimal init process
CMD ["node", "dist/server.js"]
```

***

## Logic & Trickiness Table

| Pattern | Junior Approach | Senior Approach |
|:---|:---|:---|
| **Base image** | `FROM python:3.11` | `FROM python:3.11.9-slim-bookworm` — pinned, minimal |
| **Layer order** | Copy all code first | Copy deps manifest first, then install, then copy code |
| **Cache speed** | No cache strategy | BuildKit cache mounts for package managers |
| **Image size** | Ignore it | Multi-stage; `docker image inspect` to find large layers |
| **Init process** | No init | Use `dumb-init` or `tini` to prevent zombie processes |
| **Shell vs Exec form** | `CMD python app.py` | `CMD ["python", "app.py"]` — exec form receives SIGTERM correctly |
