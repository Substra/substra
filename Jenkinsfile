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
          sh "python bin/generate_cli_documentation.py --output-path docs/cli.md.tmp && cmp --silent docs/cli.md docs/cli.md.tmp"
          sh "pydocmd simple substra.sdk+ substra.sdk.Client+ > docs/sdk.md.tmp  && cmp --silent docs/sdk.md docs/sdk.md.tmp"
          sh "rm -rf docs/*.tmp"
        }
      }
    }
  }
}
