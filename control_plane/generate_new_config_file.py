import boto3
import json
import random

iot_cli = boto3.client("iot")
s3_cli = boto3.client("s3")


def generate_config_file(dev_name, iot_endpoint, r):
    cfg = {
        "device_name": dev_name,
        "iot_endpoint": iot_endpoint,
        "cert": r["certificatePem"],
        "key": r['keyPair']['PrivateKey'],
        "device-type": "bulb",
        "root_ca": "-----BEGIN CERTIFICATE-----\nMIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF\nADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6\nb24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL\nMAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv\nb3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj\nca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM\n9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw\nIFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6\nVOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L\n93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm\njgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\nAYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA\nA4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI\nU5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs\nN+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv\no/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU\n5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy\nrqXRfboQnoZsG4q5WTP468SQvvG5\n-----END CERTIFICATE-----\n"
    }

    with open("/tmp/{}.cfg".format(dev_name), "w") as dev_file:
        dev_file.write("%s" % json.dumps(cfg))

    return "{}.cfg".format(dev_name)

r = iot_cli.describe_endpoint(
    endpointType='iot:Data-ATS'
)

iot_endpoint = r["endpointAddress"]

r = iot_cli.create_keys_and_certificate(
    setAsActive=True
)

dev_name = "dev-DDQA"
generate_config_file(dev_name, iot_endpoint, r)

certificate_arn = r['certificateArn']
policy_name = "{}-{}".format(dev_name, "Policy")

r = iot_cli.attach_thing_principal(
    thingName=dev_name,
    principal=certificate_arn
)

r = iot_cli.attach_policy(
    policyName=policy_name,
    target=certificate_arn
)

BUCKET_NAME="dreis-sandbox-temp"
dest = "{}.{}.cfg".format(dev_name, random.randint(1,10000))
s3_cli.upload_file("/tmp/{}.cfg".format(dev_name), BUCKET_NAME, dest)

print(dest)