# ACEest Fitness & Gym - CI/CD Pipeline (Assignment 2)

Flask API (ported from the Assignment 1 desktop versions) delivered through a fully
automated pipeline: **GitHub -> Jenkins -> Pytest -> SonarQube -> Docker -> Docker Hub -> Kubernetes (Minikube)**.

## Repository layout
| Path | Purpose |
|---|---|
| `app.py`, `ACEest_Fitness.py` | Flask application and entry point |
| `legacy/` | Earlier application versions (v1.0 - v3.2.4) from Assignment 1 |
| `tests/` | Pytest unit and API tests (72 tests) |
| `Dockerfile` | Image with dependencies, tests and gunicorn; version via `APP_VERSION` |
| `Jenkinsfile` | Pipeline: checkout, tests, SonarQube + quality gate, build, in-container tests, push, rolling deploy, smoke test, auto rollback |
| `sonar-project.properties` | SonarQube analysis configuration |
| `k8s/` | Manifests: `rolling/`, `blue-green/`, `canary/`, `shadow/`, `ab-testing/` |
| `docs/` | Evidence: screenshots and SonarQube export |

## Run locally
```bash
pip install -r requirements-dev.txt
pytest -q
python ACEest_Fitness.py        # http://localhost:5000/health
```

## Pipeline stages
Checkout -> Unit Tests (JUnit + coverage) -> SonarQube Analysis -> Quality Gate -> Build Image ->
Tests in Container -> Push to Docker Hub (`yamunahegade/aceest-fitness:<version>`) ->
Deploy (Rolling Update) -> Smoke Test (`/health`). On failure: `kubectl rollout undo`.

## Deployment strategies (`k8s/`)
| Strategy | How it works | Rollback |
|---|---|---|
| Rolling update | `maxUnavailable: 0`, readiness probes | `kubectl rollout undo deploy/aceest-rolling` |
| Blue-green | Two Deployments, Service selector switches slot | Patch selector back to blue |
| Canary | Stable (3 replicas) + canary (1 replica) behind one Service (~25%) | Scale canary to 0 |
| Shadow | NGINX ingress mirrors live traffic to v2, response discarded | Delete the shadow ingress |
| A/B testing | NGINX ingress routes by header `X-Variant: B` | Delete the variant ingress |
