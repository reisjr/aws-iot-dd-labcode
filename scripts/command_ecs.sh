aws ecs create-service \
    --cluster DeviceFleetInfra-ECSCluster-1WVW6ZKZIWYSB \
    --service-name fargate-service-2 \
    --task-definition sample-fargate:1 \
    --desired-count 2 \
    --launch-type "FARGATE" \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-02d6e75eb2a2ffba8],securityGroups=[sg-039bef09957ca906c],assignPublicIp=ENABLED}"


aws ecs run-task \
    --cluster DeviceFleetInfra-ECSCluster-1WVW6ZKZIWYSB \
    --task-definition sample-fargate:1 \
    --launch-type "FARGATE" \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-02d6e75eb2a2ffba8],securityGroups=[sg-039bef09957ca906c],assignPublicIp=ENABLED}"
    #[--overrides <value>]
    #[--count <value>]
