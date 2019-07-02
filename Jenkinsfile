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
        dir("substra-cli") {
          checkout scm
          sh "pip install -r requirements.txt"
          sh "pip install ."
          sh "pip install flake8"
          sh "flake8 substra"
          sh "pip install -e .[test]"
          sh "python setup.py test"
          sh "python doc/generate_cli_documentation.py --output-path doc/README.md.tmp && cmp --silent doc/README.md doc/README.md.tmp"
          sh "pydocmd simple substra_sdk_py+ substra_sdk_py.Client+ > docs/api.md.tmp  && cmp --silent docs/api.md docs/api.md.tmp"
          sh "rm -rf docs/api.md.tmp"
        }
      }
    }
  }
}
