pipeline {
  options {
    timestamps ()
    timeout(time: 1, unit: 'HOURS')
    buildDiscarder(logRotator(numToKeepStr: '5'))
    skipDefaultCheckout true
  }

  agent none

  stages {
    stage('Abort previous builds'){
      steps {
        milestone(Integer.parseInt(env.BUILD_ID)-1)
        milestone(Integer.parseInt(env.BUILD_ID))
      }
    }

    stage('Test') {
      agent {
        kubernetes {
          label 'python'
          defaultContainer 'python'
          yaml """
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: python
                image: python:3.7
                command: [cat]
                tty: true
            """
        }
      }

      steps {
        dir("substra-sdk-py") {
          checkout([$class: 'GitSCM',
            branches: [[name: '*/dev']],
            userRemoteConfigs: [[credentialsId: 'substra-deploy', url: 'https://github.com/SubstraFoundation/substra-sdk-py.git']]
          ])

          sh "pip install -r requirements.txt"
          sh "pip install ."
        }

        dir("substra-cli") {
          checkout scm
          pip install flake8
          flake8 substra
          sh "pip install -e .[test]"
          sh "python setup.py test"
        }
      }
    }
  }
}
