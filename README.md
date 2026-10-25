# CI/CD Pipeline Masterclass & Implementation Project

A production-grade, end-to-end implementation of a **Continuous Integration and Continuous Delivery / Deployment (CI/CD)** pipeline for a modern cloud-native microservice.

---

## 📑 Table of Contents
1. [Core Concepts: What is CI/CD & How Does It Work?](#core-concepts-what-is-cicd--how-does-it-work)
2. [Continuous Integration vs. Continuous Delivery vs. Continuous Deployment](#ci-vs-delivery-vs-deployment)
3. [Architecture of a Modern CI/CD Pipeline](#architecture-of-a-modern-cicd-pipeline)
4. [Project Directory Structure](#project-directory-structure)
5. [Step-by-Step Implementation Guide](#step-by-step-implementation-guide)
6. [Running the Pipeline Locally](#running-the-pipeline-locally)
7. [Cloud CI/CD Workflows (GitHub Actions & GitLab CI)](#cloud-cicd-workflows)
8. [Production Deployment Strategy (Kubernetes Rolling Update & Rollback)](#production-deployment-strategy)

---

## 1. Core Concepts: What is CI/CD & How Does It Work?

**CI/CD** is a methodology and automated software engineering practice designed to bridge the gap between development teams and operations, enabling frequent, reliable, and secure code delivery.

### How it Works (The Core Loop)
1. **Trigger**: A developer pushes code or creates a Pull Request (PR) in a Git repository.
2. **Integration (CI)**:
   - An automated runner spins up an ephemeral environment.
   - Code is checked for formatting, lint errors, and syntax.
   - Security scanning checks for hardcoded credentials and CVE vulnerabilities.
   - Automated unit, integration, and contract tests are executed.
   - A container image or deployable artifact is built.
3. **Delivery & Deployment (CD)**:
   - The verified artifact is published to a container registry (GHCR, Docker Hub, ECR).
   - The artifact is automatically deployed to a **Staging environment**.
   - Automated smoke tests verify application health.
   - Upon meeting approval rules or automated thresholds, the artifact is rolled out to **Production** with zero downtime.

---

## 2. CI vs. Delivery vs. Deployment

| Capability | Continuous Integration (CI) | Continuous Delivery (CD) | Continuous Deployment (CD) |
|---|---|---|---|
| **Goal** | Catch bugs & validate quality early | Ensure release readiness at any time | Deliver every healthy change straight to users |
| **Trigger** | Every git commit / PR | Merge to `main` branch | Merge to `main` passing all checks |
| **Output** | Tested code & passing build | Packaged artifact deployed to Staging | Live in Production |
| **Production Gate** | N/A | **Manual Approval** or Scheduled Release | **100% Automated** |

---

## 3. Architecture of a Modern CI/CD Pipeline

```
[ Developer ] 
      │ git push / PR
      ▼
┌────────────────────────────────────────────────────────┐
│            CONTINUOUS INTEGRATION (CI)                 │
│                                                        │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────┐  │
│  │ Lint & Style │──▶│ Security SAST│──▶│ Unit Tests │  │
│  │   (Ruff)     │   │   (Bandit)   │   │  (Pytest)  │  │
│  └──────────────┘   └──────────────┘   └────────────┘  │
│                            │                           │
│                            ▼                           │
│                 ┌────────────────────┐                 │
│                 │ Docker Image Build │                 │
│                 │   & Trivy Scan     │                 │
│                 └────────────────────┘                 │
└────────────────────────────┬───────────────────────────┘
                             │
                             ▼ (Merge to main)
┌────────────────────────────────────────────────────────┐
│            CONTINUOUS DELIVERY / DEPLOYMENT (CD)       │
│                                                        │
│  ┌─────────────────────────┐                           │
│  │ Artifact Publication    │                           │
│  │ (ghcr.io / Docker Hub)  │                           │
│  └───────────┬─────────────┘                           │
│              ▼                                         │
│  ┌─────────────────────────┐                           │
│  │ Staging Deployment      │                           │
│  │ + Automated Smoke Tests │                           │
│  └───────────┬─────────────┘                           │
│              ▼                                         │
│  ┌─────────────────────────┐                           │
│  │ Production Deployment   │ (Manual Gate or Auto)     │
│  │ Rolling Update (K8s)    │                           │
│  └───────────┬─────────────┘                           │
│              ▼                                         │
│  ┌─────────────────────────┐                           │
│  │ Post-deploy Healthcheck │ (Rollback if failed)      │
│  └─────────────────────────┘                           │
└────────────────────────────────────────────────────────┘
```

---

## 4. Project Directory Structure

```
cicd-pipeline-masterclass/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # GitHub Actions CI Workflow
│       └── cd.yml                 # GitHub Actions CD Workflow (Staging & Prod)
├── .gitlab-ci.yml                 # GitLab CI alternative configuration
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                # FastAPI app with health & readiness probes
│       └── services.py            # Business logic module
├── tests/
│   ├── test_api.py                # Integration / API route tests
│   └── test_services.py           # Unit tests
├── k8s/
│   └── deployment.yaml            # Kubernetes deployment, service, probes
├── scripts/
│   └── local_ci_cd.py             # Local pipeline runner simulator
├── Dockerfile                     # Multi-stage production container build
├── docker-compose.yml             # Local container orchestration
├── requirements.txt               # Production dependencies
└── requirements-dev.txt           # Testing & linting dependencies
```

---

## 5. Running the Pipeline Locally

You do not need to push to GitHub to test and observe how the pipeline works. A local pipeline simulation runner is included:

```bash
python scripts/local_ci_cd.py
```

This runs:
1. Syntax validation & lint checks
2. Static security scans (SAST)
3. Unit and integration tests with coverage reporting
4. Dockerfile validation
5. Staging deployment simulation & synthetic smoke checks
6. Production gate & zero-downtime rolling update verification

---

## 6. How to Run Tests Manually

```bash
# Run unit & integration test suite with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Run code style linter
ruff check .
```

---

## 7. How to Deploy using Docker

```bash
# Build the production container image
docker build -t ci-cd-demo-service:1.0.0 .

# Run container locally
docker run -d -p 8000:8000 --name ci-cd-demo ci-cd-demo-service:1.0.0

# Verify health check endpoints
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```
