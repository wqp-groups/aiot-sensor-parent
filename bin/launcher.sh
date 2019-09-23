#!/bin/bash
nohup java -jar /aiot/server/aiot-edge-sense-0.0.1-SNAPSHOT.jar > /aiot/server/java-nohup.out 2>&1 &
nohup python3 /aiot/server/aiot-edge-sense-0.0.1/source/main/core/launcher.py > /aiot/server/python-nohup.out 2>&1 &