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
    }
}
