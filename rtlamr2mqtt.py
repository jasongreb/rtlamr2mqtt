#!/usr/bin/env python3
'''
Runs rtlamr to watch for broadcasts from power meter. If meter ID
is in the list, usage is sent to 'readings/{msg_type}/{meter id}/meter_reading'
topic on the MQTT broker specified in settings. It also outputs the meter type
in 'readings/{msg_type}/{meter id}/meter_type'.

WATCHED_METERS = A Python list indicating those meter IDs to record and post.
MQTT_HOST = String containing the MQTT server address.
MQTT_PORT = An int containing the port the MQTT server is active on.
MSG_TYPES = Comma separated list of the message types passed to rtlamr to scan for.

'''
import os
import subprocess
import signal
import sys
import time
import paho.mqtt.publish as publish
import json
import settings

# uses signal to shutdown and hard kill opened processes and self
def shutdown(signum, frame):
    rtltcp.send_signal(15)
    rtlamr.send_signal(15)
    time.sleep(1)
    rtltcp.send_signal(9)
    rtlamr.send_signal(9)
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

auth = None

if len(settings.MQTT_USER) and len(settings.MQTT_PASSWORD):
	auth = {'username':settings.MQTT_USER, 'password':settings.MQTT_PASSWORD}

DEBUG=os.environ.get('DEBUG', '').lower() in ['1', 'true', 't']

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

# send data to MQTT broker defined in settings
def send_mqtt(topic, payload,):
    try:
        publish.single(topic, payload=payload, qos=1, hostname=settings.MQTT_HOST, port=settings.MQTT_PORT, auth=auth)
    except Exception as ex:
        print("MQTT Publish Failed: " + str(ex))

# start the rtl_tcp program
rtltcp = subprocess.Popen([settings.RTL_TCP + " > /dev/null 2>&1 &"], shell=True,
    stdin=None, stdout=None, stderr=None, close_fds=True)
time.sleep(5)

# start the rtlamr program.
if settings.WATCHED_METERS != "":
    filterids = ','.join([str(elem) for elem in settings.WATCHED_METERS])
    rtlamr_cmd = [settings.RTLAMR, '-msgtype='+settings.MSG_TYPES, '-format=json', '-filterid='+filterids]
else:
    rtlamr_cmd = [settings.RTLAMR, '-msgtype='+settings.MSG_TYPES, '-format=json']
rtlamr = subprocess.Popen(rtlamr_cmd, stdout=subprocess.PIPE, universal_newlines=True)

while True:
    try:
        amrline = rtlamr.stdout.readline().strip()
        amrdata = json.loads(amrline)

        if amrdata["Type"] == "SCM" or amrdata['Type'] == "R900" or amrdata['Type'] == "R900BCD":
            meter_id = amrdata['Message']['ID']
            meter_type = amrdata['Message']['Type']
            consumption = amrdata['Message']['Consumption']
        if amrdata["Type"] == "SCM+":
            meter_id = amrdata['Message']['EndpointID']
            meter_type = amrdata['Message']['EndpointType']
            consumption = amrdata['Message']['Consumption']
        else:
            meter_id = 'unknown'
            meter_type = 'unknown'
            consumption = 0

        msg_type = amrdata['Type'].replace('+','plus')

        debug_print('Sending meter {} reading: {}'.format(meter_id, consumption))
        send_mqtt('readings/{}/{}/meter_reading'.format(msg_type, meter_id), consumption)
        send_mqtt('readings/{}/{}/meter_type'.format(msg_type, meter_id), meter_type)

    except Exception as e:
        debug_print('Exception squashed! {}: {}', e.__class__.__name__, e)
        time.sleep(2)
