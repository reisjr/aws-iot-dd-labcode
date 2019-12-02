#!/bin/bash

function deploy_stacks() {
    ACC_ID=`aws sts get-caller-identity --query "Account" --output text --profile $1`
    echo "Deploying to PROFILE $1 / ACC_ID: $ACC_ID"
    
    export AWS_DEFAULT_REGION="us-east-1"
    cdk deploy iot-playground codepipeline devicedefender \
        --require-approval never \
        --profile $1
    
    # export AWS_DEFAULT_REGION="us-east-2"
    # cdk deploy iot-playground codepipeline devicedefender \
    #     --require-approval never \
    #     --profile $1
    
    # export AWS_DEFAULT_REGION="us-west-2"
    # cdk deploy iot-playground codepipeline devicedefender \
    #     --require-approval never \
    #     --profile $1
    
    # export AWS_DEFAULT_REGION="eu-west-1"
    # cdk deploy iot-playground codepipeline devicedefender \
    #     --require-approval never \
    #     --profile $1

}

deploy_stacks "ws01"
deploy_stacks "ws02"
deploy_stacks "ws03"
deploy_stacks "ws04"
deploy_stacks "ws05"
deploy_stacks "ws06"
deploy_stacks "ws07"
deploy_stacks "ws08"
