###############################################################################
# Kamstrup Multical 66C import script for Home Assistant                      #
# Version 0.1                                                                 #
# Author: RuntimeError123 / L. Bosch                                          #
# MIT License                                                                 #
# Copyright (c) 2018 RuntimeError123 / L. Bosch                               #
# Permission is hereby granted, free of charge, to any person obtaining a     #
# copy of this software and associated documentation files (the "Software"),  #
# to deal in the Software without restriction, including without limitation   #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
# and/or sell copies of the Software, and to permit persons to whom the       #
# Software is furnished to do so, subject to the following conditions:        #
#                                                                             #
# The above copyright notice and this permission notice shall be included in  #
# all copies or substantial portions of the Software.                         #
#                                                                             #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
###############################################################################
# Please check README file for requirements, and other info

# Importing modules
#################################
import os
import serial
import requests
from time import sleep
import yaml
import json

# Loading config
#################################
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), \
'config.yaml')
config = yaml.safe_load(open(configfile))
destination = config['main']['destination']
serialport = config['main']['serialport']

# Load mqtt and ssl if mqtt is selected
#################################
if destination == 'mqtt':
    import paho.mqtt.client as mqtt
    import ssl

# Declaring variables
#################################
if destination == 'http':
    protocol = config['http']['protocol']
    homeassistant_ip = config['http']['homeassistant_ip']
    port = str(config['http']['port'])
    if 'api_password' in config['http']:
        api_password = config['http']['api_password']
    energy_entity_id = config['http']['energy_entity_id']
    energy_friendly_name = config['http']['energy_friendly_name']
    energy_icon = config['http']['energy_icon']
    volume_entity_id = config['http']['volume_entity_id']
    volume_friendly_name = config['http']['volume_friendly_name']
    volume_icon = config['http']['volume_icon']
    temp_in_entity_id = config['http']['temp_in_entity_id']
    temp_in_friendly_name = config['http']['temp_in_friendly_name']
    temp_in_icon = config['http']['temp_in_icon']
    temp_out_entity_id = config['http']['temp_out_entity_id']
    temp_out_friendly_name = config['http']['temp_out_friendly_name']
    temp_out_icon = config['http']['temp_out_icon']

if destination == 'mqtt':
    broker = config['mqtt']['broker']
    port = config['mqtt']['port']
    if 'username' in config['mqtt']:
        username = config['mqtt']['username']
        password = config['mqtt']['password']
    if 'certificate' in config['mqtt']:
        certificate = config['mqtt']['certificate']
        tls_version = config['mqtt']['tls_version']
        tls_insecure = config['mqtt']['tls_insecure']
    topic = config['mqtt']['topic']

# Function
#################################
def http_change_entity_state(entity_id: str,
    friendly_name: str,
    unit_of_measurement: str,
    icon: str,
    new_state: float):
        url = protocol+'://'+homeassistant_ip+':'+port+'/api/states/'+entity_id
        try:
            api_password
        except:
            headers = {'content-type' : 'application/json'}
        else:
            headers = {'x-ha-access' : api_password, \
            'content-type' : 'application/json'}
        data = json.dumps({'state' : new_state, \
        'attributes' : {'unit_of_measurement' : unit_of_measurement, \
        'friendly_name' : friendly_name, 'icon' : icon}})
        response = requests.post(url, headers=headers, data=data)
        return response

# Getting information from Kamstrup Multical 66C
###############################
mc66c = serial.Serial(port=serialport,
    bytesize=serial.SEVENBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=2)
mc66c.baudrate = 300
mc66c.write('/#1'.encode('utf-8'))
mc66c.flush()
sleep(1)
mc66c.baudrate = 1200
mc66c.flushInput()
new_data = mc66c.read(87).split()
mc66c.close()

# Decode and transform new data
###############################
new_energy = int((new_data[0]).decode('utf-8'))/1000
new_volume = int((new_data[1]).decode('utf-8'))/1000
new_temp_in = int((new_data[3]).decode('utf-8'))/100
new_temp_out = int((new_data[4]).decode('utf-8'))/100

# Updating HomeAssistant values
###############################
if destination == 'http':
    energy_response = http_change_entity_state(energy_entity_id,
        energy_friendly_name,
        'GJ',
        energy_icon,new_energy)
    print("Energy updated: ",energy_response)
    volume_response = http_change_entity_state(volume_entity_id,
        volume_friendly_name,
        'M3',
        volume_icon,new_volume)
    print("Volume updated: ",volume_response)
    temp_in_response = http_change_entity_state(temp_in_entity_id,
        temp_in_friendly_name,
        '°C',
        temp_in_icon,
        new_temp_in)
    print("Temperature in updated: ",temp_in_response)
    temp_out_response = http_change_entity_state(temp_out_entity_id,
        temp_out_friendly_name,
        '°C',
        temp_out_icon,
        new_temp_out)
    print("Temperature out updated: ",temp_out_response)

if destination == 'mqtt':
    state = json.dumps({'Energy' : new_energy, \
    'Volume' : new_volume, \
    'Temperature_in' : new_temp_in, \
    'Temperature_out' : new_temp_out})
    mqttc = mqtt.Client()
    try:
        certificate
    except:
        pass
    else:
        mqttc.tls_set(certificate, certfile=None, \
        keyfile=None, \
        cert_reqs=ssl.CERT_REQUIRED, \
        tls_version=(getattr(ssl,'PROTOCOL_'+tls_version)), \
        ciphers=None)
        mqttc.tls_insecure_set(tls_insecure)
    try:
        username
    except:
        pass
    else:
        mqttc.username_pw_set(username, password=password)
    mqttc.connect(broker, port=port)
    mqttc.loop_start()
    mqttc.publish(topic, state)
    mqttc.disconnect()
    mqttc.loop_start()
    print("MQTT data published: " +state)
