pipeline {
  agent any
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Test') { steps { sh '''python3 -m venv .venv
      . .venv/bin/activate
      pip install -r requirements.txt
      pytest -q''' } }
    stage('Build Docker image') { steps { sh 'docker build -t aws-community-portal:${BUILD_NUMBER} .' } }
    // Next milestones: add image scanning, ECR push, staging deployment, health checks and approval.
  }
}
