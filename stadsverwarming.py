###############################################################################
# Kamstrup Multical 66C import script for Home Assistant                      #
# Version 0.3                                                                 #
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
compare_previous_readings = config['main']['compare_previous_readings']
if compare_previous_readings:
    energy_threshold = config['main']['energy_threshold']
    volume_threshold = config['main']['volume_threshold']

# Load mqtt and ssl if mqtt is selected
#################################
if destination == 'mqtt':
    import paho.mqtt.client as mqtt
    if 'certificate' in config['mqtt']:
        import ssl

# Declaring variables
#################################
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
def get_meter_readings():
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
    data = mc66c.read(87).split()
    mc66c.close()
    return data

# Check if previous readings file exist and if not disable comparing
###############################
previous_readings_filepath = os.path.join\
(os.path.dirname(os.path.realpath(__file__)),'previous_readings.txt')  
if not os.path.isfile(previous_readings_filepath):
    compare_previous_readings = False


# Getting information from Kamstrup Multical 66C
###############################
new_data = get_meter_readings()

# Decode and transform new data
###############################
new_energy = int((new_data[0]).decode('utf-8'))/1000
new_volume = int((new_data[1]).decode('utf-8'))/1000
new_temp_in = int((new_data[3]).decode('utf-8'))/100
new_temp_out = int((new_data[4]).decode('utf-8'))/100

# Comparing previous readings
###############################
compare_successful = False
if compare_previous_readings:
    previous_readings = open(previous_readings_filepath,'r').read().split(',')
    previous_energy = float(previous_readings[0])
    previous_volume = float(previous_readings[1])
    
    if (abs(new_energy-previous_energy)) < energy_threshold and \
    new_energy >= previous_energy and \
    (abs(new_volume-previous_volume)) < volume_threshold and \
    new_volume >= previous_volume:
        compare_successful = True
    else:
        print("Compare failed, not updating values")
    
# Updating values
###############################
if compare_successful or not compare_previous_readings:
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
        mqttc.loop_stop()
        print("MQTT data published: " +state)
    if destination == 'screen':
        print("Energy: "+str(new_energy))
        print("Volume: "+str(new_volume))
        print("Temperature in: "+str(new_temp_in))
        print("Temperature out: "+str(new_temp_out))

# Updating values
    previous_readings_file = open(previous_readings_filepath,'w')
    previous_readings_file.write(str(new_energy)+","\
    +str(new_volume))
    previous_readings_file.close()
