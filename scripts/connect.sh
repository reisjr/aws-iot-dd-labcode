#!/bin/bash

CRED_ENDPOINT=`aws iot describe-endpoint \
    --endpoint-type iot:Data-ATS \
    --output text --query endpointAddress`

if [ ! -f rootCA.pem ]; then
    wget "https://www.amazontrust.com/repository/AmazonRootCA1.pem" -O rootCA.pem
fi

DEV="dev-DDQA"

for i in {1..10}; do
    sleep 3

    mosquitto_pub \
        --cafile rootCA.pem \
        --cert $DEV.pem.cer \
        --key $DEV.pem.key \
        -h $CRED_ENDPOINT -p 8883 \
        -q 1 -t "dt/ac/company1/area1/$DEV/temp" -i $DEV \
        --tls-version tlsv1.2 -m "{ \"msg\" : \"Hello\"}" -d
done