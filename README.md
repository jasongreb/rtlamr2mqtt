# RTLAMR2MQTT: Send RTL-AMR Meter Data Over MQTT

Using an [inexpensive rtl-sdr dongle](https://www.amazon.com/s/ref=nb_sb_noss?field-keywords=RTL2832U), it's possible to listen for signals from compatible smart meters using rtlamr. This script runs as a daemon, launches rtl_tcp and rtlamr, and parses the output from rtlamr. If this matches your meter, it will push the data into MQTT for consumption by Home Assistant, OpenHAB, or custom scripts.

## Requirements

Tested under Debian GNU/Linux 8 (jessie) on NTC C.H.I.P.

### rtl-sdr package

Install RTL-SDR package

`sudo apt-get install rtl-sdr`

### git

`sudo apt-get install git`

### pip3 and paho-mqtt

Install pip for python 3

`sudo apt-get install python3-pip`

Install paho-mqtt package for python3

`sudo pip3 install paho-mqtt`

### golang & rtlamr

Install Go programming language (>1.4) & set gopath

`sudo apt-get install golang`

https://github.com/golang/go/wiki/SettingGOPATH

If only running go to get rtlamr, just set environment temporarily with the following command

`export GOPATH=$HOME/go`


Install rtlamr https://github.com/bemasher/rtlamr

`go get github.com/bemasher/rtlamr`

To make things convenient, I'm copying rtlamr to /usr/local/bin

`sudo cp ~/go/bin/rtlamr /usr/local/bin/rtlamr`

## Install

### Clone Repo
Clone repo into opt

`cd /opt`

`sudo git clone https://github.com/jasongreb/rtlamr2mqtt.git`

### Configure

Edit settings file and replace appropriate values for your configuration

`cd /opt/rtlamr2mqtt`
`sudo nano /opt/rtlamr2mqtt/settings.py`

### Install Service and Start

#### Run installservice.sh

Run bash script

`sudo /opt/rtlamr2mqtt/installservice.sh`

#### Run commands manually

Copy rtlamr2mqtt service configuration into systemd config

`sudo cp /opt/rtlamr2mqtt/rtlamr2mqtt.systemd.service /etc/systemd/system/rtlamr2mqtt.service`

Refresh systemd configuration

`sudo systemctl daemon-reload`

Set rtlamr2mqtt to run on startup

`sudo systemctl enable rtlamr2mqtt.service`

Start rtlamr2mqtt service

`sudo service rtlamr2mqtt start`

### Configure Home Assistant

To use these values in Home Assistant,
```
sensor:
  - platform: mqtt
    state_topic: "readings/meter_type/12345678/meter_reading"
    name: "Water Meter"
    unit_of_measurement: gal

  ```

meter_type will be one of the following values:
- SCM
- SMCplus
- R900
- R900BCD
- IDM (not supported yet)
- NetIDM (not supported yet)

## Testing

Assuming you're using mosquitto as the server, and your meter's id is 12345678, you can watch for events using the command:

`mosquitto_sub -t "readings/meter_type/12345678/meter_reading"`

Or if you've password protected mosquitto

`mosquitto_sub -t "readings/meter_type/12345678/meter_reading" -u <user_name> -P <password>`
