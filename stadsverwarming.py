##################################################################################
# Kamstrup Multical 66C import script for Home Assistant                         #
# Version 0.1                                                                    #
# Author: RuntimeError123 / L. Bosch                                             #
# MIT License                                                                    #
# Copyright (c) 2018 RuntimeError123 / L. Bosch                                  #
# Permission is hereby granted, free of charge, to any person obtaining a copy   #
# of this software and associated documentation files (the "Software"), to deal  #
# in the Software without restriction, including without limitation the rights   #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell      #
# copies of the Software, and to permit persons to whom the Software is          #
# furnished to do so, subject to the following conditions:                       #
#                                                                                #
# The above copyright notice and this permission notice shall be included in all #
# copies or substantial portions of the Software.                                #
#                                                                                #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR     #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,       #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER         #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  #
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  #
# SOFTWARE.                                                                      #
##################################################################################
# Please check README file for requirements, and other info


# Variables
#################################
serialport = '/dev/ttyUSB13'
protocol = 'http'
homeassistant_ip = '192.168.1.X'
port = '8123'
homeassistant_password = 'password'
energy_entity_id = 'sensor.stadsverwarming_energy'
energy_friendly_name = 'Stadsverwarming energie'
energy_icon = 'mdi:gauge'
volume_entity_id = 'sensor.stadsverwarming_volume'
volume_friendly_name = 'Stadsverwarming volume'
volume_icon = 'mdi:water'
temp_in_entity_id = 'sensor.stadsverwarming_temperature_in'
temp_in_friendly_name = 'Stadsverwarming inkomend'
temp_in_icon = 'mdi:thermometer'
temp_out_entity_id = 'sensor.stadsverwarming_temperature_out'
temp_out_friendly_name = 'Stadsverwarming uitgaand'
temp_out_icon = 'mdi:thermometer'

# Importing modules
#################################
import serial
import requests
import json
from time import sleep

# Change entity state function
#################################
def change_entity_state(entity_id: str, friendly_name: str, unit_of_measurement: str, icon: str, new_state: float):
	url = protocol+'://'+homeassistant_ip+':'+port+'/api/states/'+entity_id
	headers = {'x-ha-access' : homeassistant_password ,'content-type' : 'application/json'}
	data = json.dumps({'state' : new_state,'attributes' : {'unit_of_measurement' : unit_of_measurement,'friendly_name' : friendly_name, 'icon' : icon}})
	response = requests.post(url, headers=headers, data=data)
	return response

# Getting information from Kamstrup Multical 66C
###############################
mc66c = serial.Serial(port=serialport, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=2)
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
energy_response = change_entity_state(energy_entity_id, energy_friendly_name,'GJ',energy_icon,new_energy)
print('Energy updated: ',energy_response)
volume_response = change_entity_state(volume_entity_id, volume_friendly_name,'M3',volume_icon,new_volume)
print('Energy updated: ',volume_response)
temp_in_response = change_entity_state(temp_in_entity_id,temp_in_friendly_name,'°C',temp_in_icon,new_temp_in)
print('Energy updated: ',temp_in_response)
temp_out_response = change_entity_state(temp_out_entity_id,temp_out_friendly_name,'°C',temp_out_icon,new_temp_out)
print('Energy updated: ',temp_out_response)
