# ACEest Fitness & Gym – CI/CD Report
**Name / BITS ID:** ________  **GitHub:** ________  **Docker Hub:** ________

## 1. CI/CD Architecture Overview
A developer pushes code to **GitHub** (feature branch → `main`, release tags `v1.0.0`, `v1.1.0`).
**Jenkins** polls the repository every two minutes and runs the `Jenkinsfile` pipeline:

1. **Checkout** the commit.
2. **Unit tests** – Pytest with coverage (`report.xml`, `coverage.xml` archived as build artifacts).
3. **SonarQube analysis + Quality Gate** – static analysis; pipeline aborts if the gate fails.
4. **Docker build** – image tagged with the version and `latest`.
5. **Containerised tests** – `pytest` is executed inside the built image.
6. **Push** to **Docker Hub** (`<user>/aceest-fitness:<version>`), so every version is retained.
7. **Deploy to Kubernetes (Minikube)** using a rolling update, followed by a smoke test on `/health`.
8. **Automatic rollback** – on failure, `kubectl rollout undo` restores the last stable revision.

Additional strategies implemented as manifests: **Blue-Green** (Service selector switch), **Canary** (replica-ratio traffic split 75/25),
**Shadow** (Istio traffic mirroring), **A/B testing** (NGINX ingress header routing). Readiness/liveness probes on `/health` and
`maxUnavailable: 0` give zero-downtime updates.

*(Insert architecture diagram here.)*

## 2. Challenges Faced and Mitigation
| Challenge | Mitigation |
|---|---|
| Jenkins container could not run Docker / kubectl | Mounted host Docker socket; installed kubectl; supplied kubeconfig as a Jenkins credential |
| SonarQube quality gate never returned | Configured SonarQube → Jenkins webhook |
| Minikube could not pull the locally built image | Pushed images to Docker Hub with explicit version tags |
| Shadow deployment needs a service mesh | Installed Istio demo profile and used `VirtualService.mirror` |
| Faulty release reaching users | Readiness probes, rollout status check, `rollout undo` in `post { failure }` |
| *(add your own, e.g. port conflicts, memory limits on Minikube)* | |

## 3. Key Automation Outcomes
- Every commit is automatically tested, analysed, built, containerised and deployed with no manual steps.
- N unit tests, X% coverage (fill in from your run); SonarQube quality gate: Passed (screenshot).
- Versioned images (1.0.0, 1.1.0, …) available on Docker Hub.
- Five deployment strategies demonstrated with a tested rollback path for each.
- Mean pipeline time: ___ min (from Jenkins).

## 4. Evidence (attach screenshots)
Jenkins successful runs • SonarQube dashboard • Docker Hub tags • `kubectl get pods,svc` • each strategy's endpoint output.
