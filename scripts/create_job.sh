#!/bin/bash

aws iot delete-job \
    --job-id teste \
    --force

sleep 3

aws iot create-job \
    --job-id teste \
    --targets "arn:aws:iot:us-east-1:255847889927:thing/dev-DDQA" \
    --document-source  s3://dreis-sandbox-temp/sample_job.json

