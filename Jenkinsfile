// Prereqs on Jenkins: Docker, kubectl, SonarQube Scanner tool ("SonarScanner"),
// SonarQube server named "SonarQube", credentials: dockerhub-creds (user/pass), kubeconfig (file)
pipeline {
  agent any
  triggers { pollSCM('H/2 * * * *') }   // poll GitHub every ~2 min (or use a webhook)
  environment {
    IMAGE   = "yamunahegade/aceest-fitness"
    VERSION = "${env.TAG_NAME ?: "1.0.${env.BUILD_NUMBER}"}"
    KUBECONFIG = credentials('kubeconfig')
  }
  options { timestamps(); disableConcurrentBuilds() }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Unit Tests') {
      steps {
        sh '''
          python3 -m venv venv && . venv/bin/activate
          pip install -q -r requirements-dev.txt
          pytest -q --cov=. --cov-report=xml --junitxml=report.xml
        '''
      }
      post { always { junit 'report.xml' } }
    }

    stage('SonarQube Analysis') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh "${tool 'SonarScanner'}/bin/sonar-scanner"
        }
      }
    }
    stage('Quality Gate') {
      steps { timeout(time: 5, unit: 'MINUTES') { waitForQualityGate abortPipeline: true } }
    }

    stage('Build Image') {
      steps { sh "docker build --build-arg APP_VERSION=${VERSION} -t ${IMAGE}:${VERSION} -t ${IMAGE}:latest ." }
    }
    stage('Tests in Container') {
      steps { sh "docker run --rm ${IMAGE}:${VERSION} pytest -q" }
    }
    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'U', passwordVariable: 'P')]) {
          sh '''
            echo "$P" | docker login -u "$U" --password-stdin
            docker push ${IMAGE}:${VERSION}
            docker push ${IMAGE}:latest
          '''
        }
      }
    }

    stage('Deploy (Rolling Update)') {
      steps {
        sh '''
          kubectl apply -f k8s/rolling/
          kubectl set image deployment/aceest-rolling app=${IMAGE}:${VERSION}
          kubectl rollout status deployment/aceest-rolling --timeout=120s
        '''
      }
    }
    stage('Smoke Test') {
      steps {
        sh '''
          kubectl run smoke-${BUILD_NUMBER} --rm -i --restart=Never --image=curlimages/curl -- \
            curl -sf http://aceest-rolling-svc/health
        '''
      }
    }
  }
  post {
    failure {
      echo 'Deployment failed - rolling back to last stable revision'
      sh 'kubectl rollout undo deployment/aceest-rolling || true'
    }
    always { archiveArtifacts artifacts: 'report.xml, coverage.xml', allowEmptyArchive: true }
  }
}
