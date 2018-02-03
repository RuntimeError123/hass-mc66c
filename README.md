# Kamstrup Multical 66C import script for Home Assistant
## Author: RuntimeError123 / L. Bosch
## MIT License
#### Copyright (c) 2018 RuntimeError123 / L. Bosch
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

# INTRODUCTION
This script was written to be able to request data (meter readings) from a 
Kamstrup Multical 66C meter. This meter was provided by Nuon (utility company)
to record the energy consumption for the district heating (which we call
'stadsverwarming' in Dutch) in my home. The meter is not connected to the smart
meter in my home, nor it has a serial port which I am able to connect a home
automation solution to. There are no connectors visable. This script uses an 
infrared read/write head to communicate with the meter. Because the meter is 
battery powered, this will eventually drain the battery. According to the 
Kamstrup Multical 66C meter manual the normal battery life of the main battery
should be somewhere around 10 years. This will be shorter when the meter is 
requested to transmit it's readings every few minutes. I am using this script
to update the readings every 30 minutes in Home Assistant. The script uses Home
Assistant's RESTful API to set the value (state) of some HTTP sensors. The
values which are parsed and published to Home Assistant are: total consumed
energy (GJ), total water flow (M3), incoming temperature (°C), outgoing
temperature (°C). There are some values being ignored. One of them is the delta
temperature. I was not finding that interesting because it is just incoming
temperature - outgoing temperature. If required, please use a sensor.template
to accomplish. 

# REQUIREMENTS
To run, this script requires Python 3 with the following modules to be 
installed:
- serial
- requests
- json
- time

This script has been tested on Debian Stretch using the IR Schreibe Lesekopf 
(infrared read write head) from Volkszaehler
(https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf). 
The Home Assistant version used to test was 0.62.1.

# INSTALLATION
Place the files from Git in a separate folder (e.g. 
/home/homeassistant/stadsverwarming). Change the variables listed under the 
variables section in the script according to your needs. Test the script by
running it using python3 stadsverwarming.py . When it is not executed by root
(which I would definitly recommend) the user running should have permission 
to use serial ports. In Debian / Ubuntu this can be accomplished by adding the
user to the 'dialout' group. Schedule the script to run every X minutes / hours
using crontab.
