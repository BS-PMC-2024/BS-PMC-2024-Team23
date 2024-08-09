pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    // Compile Python files to check for syntax errors
                    sh 'python -m py_compile $(find . -name "*.py")'
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace after build
            cleanWs()
        }
    }
}