from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
import boto3
import time
import datetime
import os
import sys

DEFAULT_MQTT_PORT = 8883
DEFAULT_SAMPLING_DELAY = 60


class VirtualDevice:

    _stop = False
    _sampling_delay = DEFAULT_SAMPLING_DELAY
    _next_message_time = datetime.datetime.now()
    _mqtt_client = None
    _lwt_topic = None
    _lwt_message = None
    _clean_disconnect = True

    # Class Attributes
    endpoint = "ep"
    name = "name"
    mqtt_port = DEFAULT_MQTT_PORT    
    mqtt_telemetry_topic = "dt/ac/company1/area1/{}/temp"
    shadow = {}
    unit = "metric" # "imperial"    
    payload = { "temp" : 30 }

    
    def __init__(self, name, endpoint):
        print("New virtual device...")
        print("CLIENT_ID: '{}'".format(name))
        print("ENDPOINT : '{}'".format(endpoint))

        self.name = name
        self.endpoint = endpoint
        self.mqtt_port = DEFAULT_MQTT_PORT
    

    def set_sampling_delay(self, sampling_delay):
        print(">set_sampling_delay '{}'".format(sampling_delay))
        
        self._sampling_delay = sampling_delay
        self._next_message_time = datetime.datetime.now()

        return


    def set_clean_disconnect(self, clean):
        self._clean_disconnect = clean


    def get_shadow(self):
        print(">get_shadow")
        self._mqtt_client.publish("$aws/things/{}/shadow/get".format(self.name), "", 0)
        
        return self.shadow
    
    
    def get_jobs(self):
        print(">get_jobs")
        self._mqtt_client.publish("$aws/things/{}/jobs/get".format(self.name), "", 0)

    
    def handle_job_start_next_execution(self):
        print(">handle_job_start_next_execution")
        
        req = { 
            "statusDetails": {
                "string": "IN_PROGRESS"
            },
            "stepTimeoutInMinutes": 1,
        }

        self._mqtt_client.publish("$aws/things/{}/jobs/start-next".format(self.name), json.dumps(req), 0)

        return

    def handle_job_start_next_execution_ack_callback(self, client, mid, message):
        print(">handle_job_start_next_execution_ack_callback '{}' / '{}' / '{}'".format(client, mid, message))

        print(" handle_job_start_next_execution_ack_callback - Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))

        print(" handle_job_start_next_execution_ack_callback - Doing stuff...")
        
        my_json = message.payload.decode('utf8').replace("'", '"')
        payload = json.loads(my_json)
        
        print(" handle_job_start_next_execution_ack_callback\n{}".format(json.dumps(payload)))
        
        job_id = payload["execution"]["jobId"]
        job_doc = payload["execution"]["jobDocument"]
        version = payload["execution"]["versionNumber"]
        
        print(" handle_job_start_next_execution_ack_callback - JOB_ID: '{}' JOB_DOC: '{}'".format(job_id, job_doc))

        if "action" in job_doc:
            action = job_doc["action"]

            if action.lower() == "rotate-cert":
                print("Rotating cert...")
                self.rotate_certificate(job_doc)
            elif action.lower() == "change-unit":
                print("Changing unit...")
                self.change_unit(job_doc)
            else:
                print("Unknown action '{}'".format(action))

        req = {
            "status": "SUCCEEDED",
            "expectedVersion": version,
            "stepTimeoutInMinutes": 1,
        }

        print(" handle_job_start_next_execution_ack_callback - Stuff done")    
        
        self._mqtt_client.publish("$aws/things/{}/jobs/{}/update".format(self.name, job_id), json.dumps(req), 0)    

        print("<handle_job_start_next_execution_ack_callback Notified")    


    def stop(self):
        print(">stop")
        self._stop = True

    
    def change_unit(self, job_doc):
        print(">change_unit")

        if "unit" in job_doc:
            print("Changing unit...")
            self.unit = job_doc["unit"]    

        return


    def handle_shadow_update_callback(self, client, mid, message):
        print(">handle_shadow_update_callback '{}' / '{}' / '{}'".format(client, mid, message))
        print(" handle_shadow_update_callback - Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        
        my_json = message.payload.decode('utf8').replace("'", '"')
        payload = json.loads(my_json)

        self.shadow = payload

        with open("/tmp/shadow", "w") as file:
            file.write("%s" % json.dumps(payload))
        
        if "state" in payload:
            if "desired" in payload["state"]:
                print(payload["state"]["desired"])

        print("<handle_shadow_update_callback")
        
        return 


    def handle_cmd_reply_callback(self, client, mid, message):
        print(">handle_cmd_reply_callback '{}' / '{}' / '{}'".format(client, mid, message))
        print(" handle_cmd_reply_callback - Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))

        my_json = message.payload.decode('utf8').replace("'", '"')
        payload = json.loads(my_json)

        #type
        #session-id
        #response-topic

        if "type" in payload:
            type = payload["type"]
            session_id = payload["session-id"]
            response_topic = payload["response-topic"]
            
            #get_cmd_id()
            #do_stuff()
            #publish_reply(id)
            
            resp = {
                "session-id" : session_id,
                "status" : "OK"
            }
            
            self._mqtt_client.publish(response_topic, json.dumps(resp), 0)    
            

        print("<handle_cmd_reply_callback")
        return

    def last_will(self):
        return

    def handle_shadow_get_callback(self, client, mid, message):
        print(">handle_shadow_get_callback '{}' / '{}' / '{}'".format(client, mid, message))
        print(" handle_shadow_get_callback - Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        
        topic = str(message.topic)
        print("TOPIC: '{}'".format(topic))

        if "rejected" in topic:
            print("Shadow get rejected")
        else:
            print("Shadow get accepted")
            my_json = message.payload.decode('utf8').replace("'", '"')
            payload = json.loads(my_json)

            self.shadow = payload

            with open("/tmp/shadow", "w") as file:
                file.write("%s" % json.dumps(payload))
            
            if "state" in payload:
                if "desired" in payload["state"]:
                    print(payload["state"]["desired"])

        print("<handle_shadow_get_callback")
        
        return


    def handle_jobs_get_callback(self, client, mid, message):
        print(">handle_jobs_get_callback '{}' / '{}' / '{}'".format(client, mid, message))
        print(" handle_jobs_get_callback - Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        
        my_json = message.payload.decode('utf8').replace("'", '"')
        payload = json.loads(my_json)
        queue_jobs = payload['queuedJobs']
        in_progress_jobs = payload['inProgressJobs']

        print(" handle_jobs_get_callback CLIENT_ID '{}'".format(self.name))
        print(" handle_jobs_get_callback QUEUE_JOBS '{}'".format(queue_jobs))
        print(" handle_jobs_get_callback IN_PROGRESS_JOBS '{}'".format(in_progress_jobs))

        if queue_jobs: 
            self.handle_job_start_next_execution()

        # for q_job in queue_jobs:
        #     job_id = q_job['jobId']
        #     exec_number = q_job['executionNumber']

        #     print(" handle_jobs_get_callback GETTING DATA FOR QUEUED '{}' EXEC_# '{}'".format(job_id, exec_number))

        #     job_req = { 
        #         #"executionNumber": exec_number,
        #         "includeJobDocument": True,
        #         "clientToken": "sample-token" 
        #     }

        #     self._mqtt_client.publish("$aws/things/{}/jobs/{}/get".format(client_id, str(job_id)), json.dumps(job_req), 0)
    
        
        return


    '''
    {
      "timestamp": 1571176725,
      "execution": {
        "jobId": "test2",
        "status": "QUEUED",
        "queuedAt": 1571176724,
        "lastUpdatedAt": 1571176724,
        "versionNumber": 1,
        "executionNumber": 1,
        "jobDocument": {
          "op": "test"
        }
      }
    }
    '''
    def handle_jobs_notify_next_callback(self, client, mid, message):
        print(">handle_jobs_notify_next_callback '{}' / '{}' / '{}'".format(client, mid, message))
        print(" handle_jobs_notify_next_callback - Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))

        my_json = message.payload.decode('utf8').replace("'", '"')
        payload = json.loads(my_json)

        if 'execution' in payload :
            exec_number = payload['execution']['executionNumber']

        #       { 
        #    "executionNumber": long,
        #    "includeJobDocument": boolean,
        #    "clientToken": "string" 
        #}

            job_req = { 
                "executionNumber": exec_number,
                "includeJobDocument": True,
                "clientToken": "sample-token" 
            }

            self.handle_job_start_next_execution()
        else:
            print(" handle_jobs_notify_next_callback - NO PENDING JOB, NOTHING TO DO")

        return

    def handle_job_get_callback(self, client, mid, message):
        print(">handle_job_get_callback '{}' / '{}' / '{}'".format(client, mid, message))
        print(" handle_job_get_callback - Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        
        my_json = message.payload.decode('utf8').replace("'", '"')
        payload = json.loads(my_json)

        return


    def rotate_certificate(self, job_doc):
        print(">rotate_certificate")

        if 'config_file_url' not in job_doc:
            print(" rotate_certificate - config file not found")
            return
        
        cfg_file_url = job_doc['config_file_url']
                
        if sys.version[0:1] == '3':
            import urllib.request as urllib
        else:
            import urllib as urllib

        response = urllib.urlopen(cfg_file_url)
        cfg_file = json.loads(response.read())
        
        return


    def setup(self):
        print(">setup")

        mqtt_shadow_client = AWSIoTMQTTShadowClient(self.name)
        mqtt_shadow_client.disableMetricsCollection()

        # Configurations
        # For TLS mutual authentication
        mqtt_shadow_client.configureEndpoint(self.endpoint, self.mqtt_port)
        mqtt_shadow_client.configureCredentials("/tmp/rootCA.pem", "/tmp/key", "/tmp/cert")
                
        self._mqtt_client = mqtt_shadow_client.getMQTTConnection()
        self._mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self._mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self._mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
        self._mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec

        if self._lwt_topic:
            print("Setting LWT... '{}' / '{}'".format(self._lwt_topic, self._lwt_message))
            mqtt_shadow_client.configureLastWill(self._lwt_topic, self._lwt_message, 1)

        # Connect to AWS IoT
        connect_count = 0
        r = None
        
        try:
            print("Trying to connect '{}' '{}'...".format(self.endpoint, self.mqtt_port))
            r = mqtt_shadow_client.connect()        
        except Exception as e:
            print("FAILED")
            print(e)

        while(not r and connect_count <= 10):
            try:
                time.sleep(5)
                print("Trying to connect '{}' '{}'...".format(self.endpoint, self.mqtt_port))
                r = mqtt_shadow_client.connect()
                connect_count += 1
            except Exception as e:
                print("FAILED")
                print(e)

        if (r):
            print("Device '{}' connected!".format(self.name))
        else:
            print("ERROR: Device '{}' NOT connected!".format(self.name))
            return

        # Create a deviceShadow with persistent subscription
        #deviceShadowHandler = myMQTTShadowClient.createShadowHandlerWithName(client_id, True)
        #shadowCallbackContainer_Bot = shadowCallbackContainer(deviceShadowHandler)

        time.sleep(2)

        #JOBS
        self._mqtt_client.subscribe("$aws/things/{}/jobs/notify-next".format(self.name), 0, self.handle_jobs_notify_next_callback)
        #self._mqtt_client.subscribe("$aws/things/{}/jobs/get/accepted".format(client_id), 1, handle_jobs_get_callback)
        #self._mqtt_client.subscribe("$aws/things/{}/jobs/get/rejected".format(client_id), 1, handle_jobs_get_callback)
        self._mqtt_client.subscribe("$aws/things/{}/jobs/get/#".format(self.name), 0, self.handle_jobs_get_callback)
        self._mqtt_client.subscribe("$aws/things/{}/jobs/+/get/+".format(self.name), 0, self.handle_job_get_callback)
        self._mqtt_client.subscribe("$aws/things/{}/jobs/start-next/#".format(self.name), 0, self.handle_job_start_next_execution_ack_callback)
        
        #SHADOW TOPICS
        #$aws/things/{}/shadow/update/accepted
        #$aws/things/{}/shadow/update/delta
        #$aws/things/{}/shadow/update/documents
        #$aws/things/{}/shadow/get/accepted
        # Subscribing only to accepted topics. In a production environment, the device should handle rejected messages as well.
        self._mqtt_client.subscribe("$aws/things/{}/shadow/get/+".format(self.name), 0, self.handle_shadow_get_callback)
        self._mqtt_client.subscribe("$aws/things/{}/shadow/update/accepted".format(self.name), 0, self.handle_shadow_update_callback)

        #COMMAND / REPLY PATTERN
        self._mqtt_client.subscribe("cmd/ac/{}/req".format(self.name), 0, self.handle_cmd_reply_callback)

        return

    def start(self):
        print(">start")

        # check any pending job
        print("Checking for pending jobs...")
        self.get_jobs()

        # get shadow status
        print("Getting shadow status...")
        self.get_shadow()

        #moving to self to allow fast configuration change
        self._next_message_time = datetime.datetime.now()

        while True:
            current_time = datetime.datetime.now()

            if self._next_message_time <= current_time:
                #payload = { "temp" : 30 }
                print(self._sampling_delay)
                print("Sending to '{}' the payload below\n{}".format(self.mqtt_telemetry_topic, self.payload))
                self._mqtt_client.publish(self.mqtt_telemetry_topic.format(self.name), json.dumps(self.payload), 0)
                self._next_message_time = current_time + datetime.timedelta(0, self._sampling_delay)
                        
            if self._stop: # Using next_message to stop the thread properly
                print("Stopping...")
                if self._clean_disconnect:
                    print("Disconnecting from the broker...")
                    self._mqtt_client.disconnect()
                    print("Disconnected")
                else:
                    print("Sudden disconnect...")

                break
            
            time.sleep(0.5)

    
    def register_last_will_and_testament(self, topic, message):
        print(">register_last_will_and_testament")
        
        self._lwt_topic = topic
        self._lwt_message = message 
        
        return ""


class VirtualSwitch(VirtualDevice):

    target_device = "dev-NANN"

    def __init__(self, name, endpoint):
        VirtualDevice.__init__(self, name, endpoint)


    def set_target_device(self, target_device):
        self.target_device = target_device


    def press_on(self):
        print(">press_on")
        payload = json.dumps({"state": { "desired": { "status": "on" } }})
        self._mqtt_client.publish("$aws/things/{}/shadow/update".format(self.target_device), payload, 0)
        return


    def press_off(self):
        print(">press_off")
        payload = json.dumps({"state": { "desired": { "status": "off" } }})
        self._mqtt_client.publish("$aws/things/{}/shadow/update".format(self.target_device), payload, 0)
        return


class VirtualBulb(VirtualDevice):

    is_on = False 

    def __init__(self, name, endpoint):
        VirtualDevice.__init__(self, name, endpoint)


if __name__ == '__main__':
    vd = VirtualDevice("dev-DDQA", "a1x30szgyfp50b-ats.iot.us-east-1.amazonaws.com")
    vd.setup()
    vd.start()