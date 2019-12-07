#!/bin/bash

function list_envs() {
    ACC_ID=`aws sts get-caller-identity --query "Account" --output text --profile $1`
    echo "Listing Cloud9 PROFILE $1 / ACC_ID: $ACC_ID"
    
    # export AWS_DEFAULT_REGION="us-east-1"
    # cdk deploy iot-playground codepipeline devicedefender \
    #     --require-approval never \
    #     --profile $1
    
    # export AWS_DEFAULT_REGION="us-east-2"
    # cdk deploy iot-playground codepipeline devicedefender \
    #     --require-approval never \
    #     --profile $1
    
    export AWS_DEFAULT_REGION="us-west-2"
    aws cloud9 list-environments \
            --profile $1
    
    # export AWS_DEFAULT_REGION="eu-west-1"
    # cdk deploy iot-playground codepipeline devicedefender \
    #     --require-approval never \
    #     --profile $1
}

function diff_cdk_stacks() {
    echo "Listing CDK Stacks PROFILE $1"
    export AWS_DEFAULT_REGION="us-west-2"
    cdk diff --profile $1 --region "us-west-2"
}


diff_cdk_stacks "ws10"
diff_cdk_stacks "ws01"
diff_cdk_stacks "ws02"
diff_cdk_stacks "ws03"
diff_cdk_stacks "ws04"
diff_cdk_stacks "ws05"
diff_cdk_stacks "ws06"
diff_cdk_stacks "ws07"
diff_cdk_stacks "ws08"
diff_cdk_stacks "ws09"

list_envs "ws10"
list_envs "ws01"
list_envs "ws02"
list_envs "ws03"
list_envs "ws04"
list_envs "ws05"
list_envs "ws06"
list_envs "ws07"
list_envs "ws08"
list_envs "ws09"

