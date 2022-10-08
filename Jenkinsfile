pipeline {
    options {
        timeout(time: 10, unit: 'MINUTES')
        }
    agent any
    stages {
        stage('Python Environment') {
            steps {
                sh '''
                virtualenv venv -p python3.9
                . venv/bin/activate
                pip install --upgrade pip
                pip install .[dev]
                '''
            }
        }
        stage('Code Formatter') {
            steps {
                sh '''
                . venv/bin/activate
                black --check --diff tp_timesheet
                '''
            }
        }
        stage('Linter') {
            steps {
                sh '''
                . venv/bin/activate
                pylint tp_timesheet
                '''
            }
        }
        stage('Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                tox
                '''
            }
        }
    }
    post {
        always {
            cleanWs(cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    notFailBuild: true,
                    patterns: [[pattern: '.gitignore', type: 'INCLUDE'],
                               [pattern: '.propsfile', type: 'EXCLUDE']])
        }
    }
}
