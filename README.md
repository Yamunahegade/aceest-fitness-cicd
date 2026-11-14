# ACEest Fitness & Gym – CI/CD Pipeline

Flask app → Pytest → SonarQube → Docker → Docker Hub → Kubernetes (Minikube), orchestrated by Jenkins.

## 0. Before you start – replace placeholders
- `YOUR_DOCKERHUB_USER` in `Jenkinsfile` and every `k8s/**/*.yaml`
- Paste your Assignment 1 logic into `ACEest_Fitness.py` (keep `create_app()` + `/health`) and update `tests/`
- Keep older versions as `ACEest_Fitness_v1_0.py`, `..._v1_1.py` etc. if your Assignment 1 had them

## 1. Git & GitHub
```bash
git init && git add . && git commit -m "feat: initial Flask app, tests, Dockerfile"
git branch -M main
git remote add origin https://github.com/<you>/aceest-fitness.git
git push -u origin main
git checkout -b feature/v1.1 ; # make changes ...
git commit -am "feat: v1.1 improvements" ; git checkout main ; git merge feature/v1.1
git tag v1.0.0 ; git tag v1.1.0 ; git push --tags
```

## 2. Local run + tests
```bash
pip install -r requirements-dev.txt
pytest -q --cov=. --cov-report=xml
python ACEest_Fitness.py        # http://localhost:5000/health
```

## 3. Docker
```bash
docker build --build-arg APP_VERSION=1.0.0 -t <user>/aceest-fitness:1.0.0 .
docker run --rm <user>/aceest-fitness:1.0.0 pytest -q     # tests inside container
docker login && docker push <user>/aceest-fitness:1.0.0
# change code, bump APP_VERSION, build & push 1.1.0 (and 1.2.0 ...) – needed for canary/blue-green/A-B
```
(Podman: replace `docker` with `podman`.)

## 4. SonarQube
```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
```
Open http://localhost:9000 (admin/admin) → create project `aceest-fitness` → generate a token →
Jenkins: *Manage Jenkins → System → SonarQube servers* (name `SonarQube`, add token as secret text),
*Tools → SonarQube Scanner* (name `SonarScanner`). Add a webhook in SonarQube → `http://<jenkins>:8080/sonarqube-webhook/`
(needed by `waitForQualityGate`). Take screenshots of the dashboard/quality gate for your report.

## 5. Jenkins
```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts
```
Install plugins: Pipeline, Git, GitHub, Docker Pipeline, SonarQube Scanner, JUnit, Credentials Binding.
Credentials: `dockerhub-creds` (username/password), `kubeconfig` (secret file).
Create a *Multibranch Pipeline* (or Pipeline from SCM) pointing at your GitHub repo; Jenkinsfile polls SCM every 2 min.
The Jenkins container also needs `python3`, `python3-venv`, `docker` CLI and `kubectl`.

## 6. Kubernetes (Minikube)
```bash
minikube start --driver=docker
minikube addons enable ingress
```
| Strategy | Apply | Switch / verify | Rollback |
|---|---|---|---|
| Rolling update | `kubectl apply -f k8s/rolling/` | `kubectl set image deploy/aceest-rolling app=<user>/aceest-fitness:1.1.0` ; `kubectl rollout status deploy/aceest-rolling` | `kubectl rollout undo deploy/aceest-rolling` |
| Blue-Green | `kubectl apply -f k8s/blue-green/` | patch Service selector to `slot: green` (see service.yaml) | patch selector back to `blue` |
| Canary | `kubectl apply -f k8s/canary/` | `for i in $(seq 20); do curl -s $(minikube service aceest-canary-svc --url)/version; done` (≈25% show 1.1.0) | `kubectl scale deploy/aceest-canary --replicas=0` |
| Shadow | install Istio, `kubectl apply -f k8s/shadow/` | hit service; check `kubectl logs deploy/aceest-v2` shows mirrored requests | `kubectl delete -f k8s/shadow/` |
| A/B testing | `kubectl apply -f k8s/ab-testing/` | `curl -H "Host: aceest.local" $(minikube ip)/version` vs adding `-H "X-Variant: B"` | `kubectl delete ing aceest-ab-variant-b` |

Endpoint URL for submission: `minikube service <svc> --url` (or `kubectl port-forward`; for a publicly reachable URL use a cloud cluster or ngrok).
