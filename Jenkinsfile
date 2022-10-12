pipeline {
    options {
        timeout(time: 5, unit: 'MINUTES')
    }
    agent {
        docker {
            image 'python:3.8-slim'
	    args '-e "HOME=$WORKSPACE"'
        }
    }
    stages {
        stage('Python Environment') {
            steps {
                sh '''
                echo "HOME: $HOME"
                echo "~/"
		pwd
                python -m venv venv
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
                pytest
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
