pipeline {
  options {
    timestamps ()
    timeout(time: 1, unit: 'HOURS')
    buildDiscarder(logRotator(numToKeepStr: '5'))
    skipDefaultCheckout true
  }

  parameters {
    booleanParam(name: 'E2E', defaultValue: false, description: 'Launch E2E test')
    string(name: 'CHAINCODE', defaultValue: 'dev', description: 'chaincode branch')
    string(name: 'BACKEND', defaultValue: 'jenkins', description: 'substrabac branch')
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
          sh "pip install flake8"
          sh "flake8 substra"
          sh "pip install -e .[test]"
          sh "python setup.py test"
          sh "python bin/generate_cli_documentation.py --output-path references/cli.md.tmp && cmp --silent references/cli.md references/cli.md.tmp"
          sh "pydocmd simple substra.sdk+ substra.sdk.Client+ > references/sdk.md.tmp  && cmp --silent references/sdk.md references/sdk.md.tmp"
          sh "rm -rf references/*.tmp"
        }
      }
    }

    stage('Test with substra-network') {
      when {
        expression { return params.E2E }
      }
      steps {
        build job: 'substra-network/dev', parameters: [string(name: 'CLI', value: env.CHANGE_BRANCH),
                                                       string(name: 'BACKEND', value: params.BACKEND),
                                                       string(name: 'CHAINCODE', value: params.CHAINCODE)], propagate: true
      }
    }

  }
}
