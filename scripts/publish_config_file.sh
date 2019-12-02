#!/bin/bash

ACC_ID=`aws sts get-caller-identity --query "Account" --output text`
aws s3 mb s3://dreis-temp-$ACC_ID
IOT_ENDPOINT=`aws iot describe-endpoint --endpoint-type iot:Data-ATS --output text --query "endpointAddress"`

aws s3 cp config.json s3://dreis-temp-$ACC_ID
aws s3 presign s3://dreis-temp-$ACC_ID/config.json 