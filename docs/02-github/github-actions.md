# GitHub Actions CI Pipeline

## Objective

Implement a Continuous Integration (CI) pipeline to automatically validate Docker images whenever code is pushed to GitHub.

## Workflow Architecture

Developer Push
    ↓
GitHub Actions
    ↓
Build Backend Image
    ↓
Build Frontend Image
    ↓
PASS / FAIL

## Workflow File

.github/workflows/docker-build.yml

## Trigger Events

### Push to Main

...

### Pull Requests

...

## Build Steps

### Checkout Repository

...

### Build Backend Image

...

### Build Frontend Image

...

## Verification

Workflow Result:

✓ Success

Run Number:

#1

Execution Time:

21 seconds

## Lessons Learned

- Introduction to CI
- GitHub-hosted runners
- Workflow automation
- Docker image validation
