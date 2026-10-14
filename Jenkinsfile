pipeline {
    agent any
    stages {
        stage('Checkout')  { steps { checkout scm } }
        stage('Install')   { steps { sh 'python3 -m pip install -r requirements.txt' } }
        stage('Run tests') { steps { sh 'python3 -m pytest tests --junitxml=report.xml' } }
    }
    post { always { junit 'report.xml' } }
}
