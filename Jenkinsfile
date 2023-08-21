pipeline {
    agent { label 'docker && linux' }
    options {
        timeout(time: 30, unit: 'MINUTES')
    }
    environment {
        DOCKER_IMAGE = 'python'
    }
    stages {
        stage('Build And Test Pipeline') {
            matrix {
                agent {
                    docker {
                        image "${DOCKER_IMAGE}:${DOCKER_TAG}"
                        args '-e "HOME=$WORKSPACE"'
                    }
                }
                axes {
                    axis {
                        name 'DOCKER_TAG'
                        values '3.8-slim', '3.9-slim', '3.10-slim', '3.11-slim'
                    }
                }
                stages {
                    stage('Python Environment') {
                        options {
                            timeout(time: 5, unit: 'MINUTES')
                        }
                        steps {
                            echo "Environment: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            sh '''
                            python -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install .[dev]
                            '''
                        }
                    }
                    stage('Code Format') {
                        options {
                            timeout(time: 30, unit: 'SECONDS')
                        }
                        steps {
                            echo "Environment: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            sh '''
                            . venv/bin/activate
                            black --check --diff tp_timesheet
                            '''
                        }
                    }
                    stage('Linter') {
                        options {
                            timeout(time: 1, unit: 'MINUTES')
                        }
                        steps {
                            echo "Environment: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            sh '''
                            . venv/bin/activate
                            pylint tp_timesheet
                            '''
                        }
                    }
                    stage('Unit Tests') {
                        options {
                            timeout(time: 5, unit: 'MINUTES')
                        }
                        environment {
                            CLOCKIFY_CRED = credentials('ClockifyCredentials')
                        }
                        steps {
                            echo "Environment: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            sh '''
                            . venv/bin/activate
                            # Skip clockify tests due to missing API keys.
                            pytest -s -k 'not test_clockify'
                            '''
                        }
                    }
                }
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
