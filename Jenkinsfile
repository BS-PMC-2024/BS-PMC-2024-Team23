pipeline {
    agent none
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'python:3.11'
                }
            }
            steps {
                script {
                    // קומפילציה של קבצי Python כדי לוודא שאין שגיאות סינטקס
                    sh 'python -m py_compile sources/add2vals.py sources/calc.py'
                }
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'qnib/pytest'
                }
            }
            steps {
                script {
                    // הרצת הבדיקות והפקת תוצאות בקובץ XML
                    sh 'py.test --verbose --junit-xml test-reports/results.xml sources/test_calc.py'
                }
            }
            post {
                always {
                    // פרסום תוצאות הבדיקות ל-Jenkins
                    junit 'test-reports/results.xml'
                    // ניקוי סביבות עבודה לאחר סיום
                    cleanWs()
                }
            }
        }
    }
    environment {
        // אם יש משתנים סודיים או משתנים נוספים, הוסף אותם כאן
        // MY_ENV_VAR = 'value'
    }
}
