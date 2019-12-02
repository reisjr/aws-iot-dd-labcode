#!/bin/bash

function destroy_stacks() {
    ACC_ID=`aws sts get-caller-identity --query "Account" --output text --profile $1`
    echo "Destroying PROFILE $1 / ACC_ID: $ACC_ID"

    export AWS_DEFAULT_REGION="us-east-1"
    cdk destroy iot-playground codepipeline devicedefender \
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

destroy_stacks "ws01"
destroy_stacks "ws02"
destroy_stacks "ws03"
destroy_stacks "ws04"
destroy_stacks "ws05"
destroy_stacks "ws06"
destroy_stacks "ws07"
destroy_stacks "ws08"