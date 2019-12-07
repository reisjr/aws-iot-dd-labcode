#!/bin/bash

PROFILE=sandbox
URL=`aws s3 presign --expires-in 3000000 s3://dreis-sandbox-temp/dev-DDQA.json`
PORT=8080

echo "export AWS_PROFILE=$PROFILE"
echo "export CONFIG_FILE_URL=\"$URL\""
echo "export PORT=$PORT"