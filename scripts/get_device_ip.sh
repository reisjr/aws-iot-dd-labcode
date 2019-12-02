#!/bin/bash

CLUSTER_NAME=`aws ssm get-parameter \
    --name iot-playground-clustername \
    --query "Parameter.Value" \
    --output text`

TASK_ID=`aws ecs list-tasks \
    --started-by "$1" \
    --cluster "$CLUSTER_NAME" \
    --query "taskArns[0]" \
    --output text`

ENI_ID=$(aws ecs describe-tasks \
    --tasks "$TASK_ID" \
    --cluster "$CLUSTER_NAME" \
    --query "tasks[0].attachments[0].details[?name==\`networkInterfaceId\`].value" \
    --output text)

PUBLIC_IP=`aws ec2 describe-network-interfaces \
    --filter Name=network-interface-id,Values="$ENI_ID" \
    --query NetworkInterfaces[0].Association.PublicIp \
    --output text`

echo "DEVICE DATA"
echo "CLUSTER NAME: $CLUSTER_NAME"
echo "   DEVICE ID: $1"
echo "     TASK ID: $TASK_ID"
echo "      ENI ID: $ENI_ID"
echo "   PUBLIC IP: $PUBLIC_IP"

