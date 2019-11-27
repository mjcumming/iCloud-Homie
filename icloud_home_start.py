#!/usr/bin/env python

import time

import yaml

mqtt_settings = {
    'MQTT_BROKER' : 'OpenHab',
    'MQTT_PORT' : 1883,
}

update_interval = 15 #minutes

from icloud_homie.icloud_account import ICloud_Account 

with open("icloud_homie.yml", 'r') as ymlfile:
    cfg = yaml.full_load(ymlfile)

ic = ICloud_Account(username,password,mqtt_settings=mqtt_settings)


try:
    while True:
        time.sleep(60)

        ic.update_devices()

except (KeyboardInterrupt, SystemExit):
    print("Quitting.")  