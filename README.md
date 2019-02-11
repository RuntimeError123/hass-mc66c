# hass-mc66c
## Imports meter readings of Kamstrup Multical 66C to Home Assistant or MQTT.
## Author: RuntimeError123 / L. Bosch
## MIT License
#### Copyright © 2019 RuntimeError123 / L. Bosch
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# 1. INTRODUCTION
This script was written to be able to request data (meter readings) from a
Kamstrup Multical 66C meter. This meter was provided by Nuon (utility company)
to record the energy consumption for the district heating (which we call
'stadsverwarming' in Dutch) in my home. The meter is not connected to the smart
meter in my home, nor it has a serial port which I am able to connect a home
automation solution to. There are no connectors visible. This script uses an
infrared read/write head to communicate with the meter. Because the meter is
battery powered, this will eventually drain the battery. According to the
Kamstrup Multical 66C meter manual the normal battery life of the main battery
should be somewhere around 10 years. This will be shorter when the meter is
requested to transmit it's readings every few minutes. I am using this script
to update the readings every 30 minutes in Home Assistant. The script can be 
run with two configurations. 
It uses an MQTT broker (Home Asssistance integrated or stand alone) to send 
the measurements. All values are sent to a single MQTT topic. Home Assistant 
will be able to create separate sensors on a single MQTT topic. For testing 
purposes, this script can also output to the screen.

# 2. REQUIREMENTS
To run, this script requires Python 3 with the following modules to be
installed:
- serial (installable with apt-get install python3-serial)
- requests
- json
- time
- yaml (can be installed with `apt-get install python3-yaml`)

To use this script with MQTT, install Paho MQTT 
(`apt-get install python3-pip && pip3 install paho-mqtt`).

When this script is configured to use SSL/TLS, the Python SSL module is 
required.

To get the meter readings, you will need an IR interface. I am currently using
the IR Schreib Lesekopf (infrared read write head) from Volkszaehler
(https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf) which 
I recommend.

# 3. INSTALLATION
Place the files from Git in a separate folder (e.g.
/home/homeassistant/stadsverwarming). Edit the config.yaml file according to 
your situation. Please see next paragraph for more information. Test the script 
by running it using python3 stadsverwarming.py . When it is not executed by 
root (which I would strongly recommend) the user running this script must 
have permission to use serial ports. In Debian / Ubuntu this can be
accomplished by adding the user to the 'dialout' group. Schedule the script to
run every X minutes / hours using crontab.

# 4. DEFINITION OF VARIABLES
The config.yaml file should be placed in the same directory as the 
stadsverwarming.py script. The config file provides all settings required by
the script. This paragraph will explain the purpose of these settings. To make
it easier to configure this script, a demo config.yaml is supplied on GitHub.

## main section
This section is used for the main configuration of the script.

- serialport (required)

    The serial port used to contact the IR Schreib Lesekopf (or compatible).
    This usually corresponds to a Linux serial port (like /dev/ttyUSB1). If you
    experience that this changes after a reboot, please use a udev rule to make
    a static mapping. On systems running Windows it will probably work to use
    COM1 or the COM port which corresponds to the port which is used to connect
    to the IR Schreib Lesekopf.
    
- destination (required)

    Can be 'mqtt', 'http' or 'screen'. Defines what to do with the data 
    received from the meter. Http sends the readings directly to the Home 
    Assistant RESTful API. MQTT needs an MQTT broker which can be subscribed to
    by Home Assistant or another home automation application which supports
    MQTT. Screen can be used for debugging or testing purposes as it just shows
    the meter readings to the screen. It does not need parameters set in any 
    other section.
    
- compare_previous_readings

    Can be True or False.
    On the first run (even when set to False) a text file called
    'previous_readings.txt' will be created, containing the energy and volume
    reading. If set to True the new reading will be compared to the old 
    reading. Because the meter can only count forwards, no new values lower
    than the previous one will be allowed. This feature is implemented because 
    my meter sometimes gives wrong information back (not sure why). When 
    selected, the script will also check if the difference between the new
    reading is not too big. To configure this the following options can be 
    used.  
    
- energy_threshold (optional)

    This section is only required when compare_previous_readings is enabled. 
    Enter how much GJ difference between the previous reading and current 
    reading should be considered normal. 
    
- volume_threshold (optional): 
    
    This section is only required when compare_previous_readings is enabled. 
    Enter how much M3 difference between the previous reading and current 
    reading should be considered normal. 
    
## mqtt section

This section is required if destination is set to mqtt

- broker (required)

    Ip address or FQDN of MQTT broker. The script will use this broker to send
    the measurements values. Only a single MQTT topic will be used.

- port (required)

    The port where the MQTT service is listening on. MQTT default is 1883, 
    default when using ssl/tls is 8883.

- username (optional)

    If authentication on the MQTT broker is required, please specify the 
    username. If this setting removed from the configration, no authentication 
    will be attempted. I recommend protecting MQTT with a username and a strong 
    password.
    
- password (optional)

    If authentication on the MQTT broker is required, please specify the 
    password. This setting requires a username to be defined.
    
- certificate (optional)

    Specify a certificate to verify the connection to the MQTT broker. Might
    be /etc/ssl/certs/ca_certificates.crt when the server certificate has been
    signed by a generally trusted authority. If this setting is removed from
    the configuration, plain text MQTT will be used. I recommend using ssl/tls.
    
- tls_version (optional)

    Specify the tls version to be used. Choose one of the following:
    - SSLv23
    - TLS
    - TLSv1
    - TLSv1_1
    - TLSv1_2
    
    I recommend selecting TLSv1_2 which corresponds to TLS v1.2. 
    This setting requires a certificate to be defined.

- tls_insecure (optional)

    Set to true if you want to switch off checking the  hostname in the used 
    certificate.  I recommend leaving this configured to 'false'. This setting 
    requires a certificate to be defined.
    
- topic: (required)

    The script will send the measurement values as JSON to this topic.

- retain (required): 

    Specify the retain flag for the message. It will be set as 'last known 
    good' or retained on the broker.
    
# Home Assistant configuration

As an example you can make a configuration item in Home Assistant's
configuration.yaml. You need to define the connection to the MQTT broker if it
does not already exist. It is also possible to define this connection in a 
separate yaml file and link it by using !include <yamlfile>.

        mqtt:
          broker: 192.168.1.x
          port: 8883
          username: homeassistant
          password: password
          certificate: /etc/ssl/certs/ca_certificates.crt
          tls_version: '1.2'

Also you will need to define a few sensors to use with the stadsverwarming 
script. Those are situated on the 'sensors:' configuration item in the 
configuration.yaml. This may also be placed in a separate file linked by 
!include <yamlfile>. An example of how to do this is:

        - platform: mqtt
          state_topic: home-assistant/stadsverwarming
          name: "Temperature in"
          unit_of_measurement: "°C"
          value_template: "{{ value_json.Temperature_in }}"
        - platform: mqtt
          state_topic: home-assistant/stadsverwarming
          name: "Temperature out"
          unit_of_measurement: "°C"
          value_template: "{{ value_json.Temperature_out }}"
        - platform: mqtt
          state_topic: home-assistant/stadsverwarming
          name: "Volume"
          unit_of_measurement: "M3"
          value_template: "{{ value_json.Volume }}"
        - platform: mqtt
          state_topic: home-assistant/stadsverwarming
          name: "Energy"
          unit_of_measurement: "GJ"
          value_template: "{{ value_json.Energy }}"

# Tests

This script has been tested on Debian Stretch using the IR Schreib Lesekopf
(infrared read write head) from Volkszaehler
(https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf).
The Home Assistant versions used to test were 0.62.1 and 0.67.0. The MQTT part 
has been tested with Mosquitto (1.4.15-0mosquitto3)

The script has been tested with the following destinations / settings:

- http with password
- http without password
- https with password
- mqtt with TLS1.2 and password
- mqtt without encryption and without password
