# Kamstrup Multical 66C import script for Home Assistant
## Author: RuntimeError123 / L. Bosch
## MIT License
#### Copyright © 2018 RuntimeError123 / L. Bosch
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
It can use Home Assistant's RESTful API to set the value (state) of some HTTP 
sensors. The values which are parsed and published to Home Assistant are: total
consumed energy (GJ), total water flow (M3), incoming temperature (°C), 
outgoing temperature (°C). There are some values being ignored. One of them is 
the delta temperature. I was not finding that interesting because it is just 
incoming temperature minus outgoing temperature. If required, please use a 
sensor.template to accomplish.
Starting with this release, the script also supports sending the measurements 
to a MQTT broker. When this option is selected, all values are sent to a single
MQTT topic. Home Assistant will be able to create separate sensors on a single
MQTT topic.

# 2. REQUIREMENTS
To run, this script requires Python 3 with the following modules to be
installed:
- serial (installable with apt-get install python3-serial)
- requests
- json
- time
- yaml (installable with `apt-get install python3-yaml`)

To use this script with MQTT, install Paho MQTT 
(`apt-get install python3-pip && pip3 install paho-mqtt`).

To get the meter readings, you will need an IR interface. I am currently using
the IR Schreib Lesekopf (infrared read write head) from Volkszaehler
(https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf) which 
I recommend.

# 3. INSTALLATION
Place the files from Git in a separate folder (e.g.
/home/homeassistant/stadsverwarming). Edit the config.yaml file according to 
your situation. Please see next paragraph for more information. Test the script 
by running it using python3 stadsverwarming.py . When it is not executed by 
root (which I would definitely recommend) the user running this script must 
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

    Can be either 'mqtt' or 'http'. Defines what to do with the data received
    from the meter.
    
## http section
This section is required if destination is set to http.

- protocol (required)

    The protocol used to connect to Home Assistant. Supportes http and
    https. When using https, please make sure that the certificate provided is 
    trusted by the machine running this script. For security reasons I 
    recommend https.
    
- homeassistant_ip (required)

    The IP address used to connect to Home Assistant. FQDN's are also
    supported.

- port (required)

    The port used to connect to Home Assistant. Home Assistant's default is 
    8123.

- api_password (optional)

    Password which is configured as api_password in Home Assistant's
    configuration.yaml or secrets.yaml. Leave empty if your Home Assistant is 
    not protected by a password. I recommend configuring an api password for
    Home Assistant.

- [energy/volume/temp_in/temp_out]\_entity_id (required)

  Device identifier which must be unique to this specific device in Home
    Assistant. Must be in the format [component name].[platform]\_name .

- [energy/volume/temp_in/temp_out]\_friendly\_name (required)

    Friendly name, how device will be displayed in Home Assistant. Can be
    overridden by customize.yaml.

- [energy/volume/temp_in/temp_out]\_icon (required)

    Icon used for the sensor in GUI. Append with "mdi:" and the Material Design
    Icon name. Icon "alert" would become "mdi:alert".
    
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
    username. If this setting is not defined, no authentication will be 
    attempted. I recommend protecting MQTT with a username and a strong 
    password.
    
- password (optional)

    If authentication on the MQTT broker is required, please specify the 
    password.
    
- certificate (optional)

    Specify a certificate to verify the connection to the MQTT broker. Might
    be /etc/ssl/certs/ca_certificates.crt when the server certificate has been
    signed by a generally trusted authority. If this setting is not defined, 
    plain text MQTT will be used. I recommend using ssl/tls.
    
- tls_version (optional)

    Specify the tls version to be used. Choose one of the following:
    - SSLv23
    - TLS
    - TLSv1
    - TLSv1_1
    - TLSv1_2
    
    I recommend selecting TLSv1_2 which corresponds to TLS v1.2.

- tls_insecure (optional)

    Set to true if you want to switch off checking the  hostname in the used 
    certificate.  I recommend leaving this configured to 'false'.
    
- topic: (required)

    The script will send the measurement values as JSON to this topic.
    
# Home Assistant configuration

## http
No specific configuration required

## mqtt

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
          retain: true
        - platform: mqtt
          state_topic: home-assistant/stadsverwarming
          name: "Temperature out"
          unit_of_measurement: "°C"
          value_template: "{{ value_json.Temperature_out }}"
          retain: true
        - platform: mqtt
          state_topic: home-assistant/stadsverwarming
          name: "Volume"
          unit_of_measurement: "M3"
          value_template: "{{ value_json.Volume }}"
          retain: true
        - platform: mqtt
          state_topic: home-assistant/stadsverwarming
          name: "Energy"
          unit_of_measurement: "GJ"
          value_template: "{{ value_json.Energy }}"
          retain: true


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
