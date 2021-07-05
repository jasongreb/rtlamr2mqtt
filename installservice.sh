#!/bin/bash

cp /opt/rtlamr2mqtt/rtlamr2mqtt.systemd.service /etc/systemd/system/rtlamr2mqtt.service
systemctl daemon-reload
systemctl enable rtlamr2mqtt.service
service rtlamr2mqtt start
