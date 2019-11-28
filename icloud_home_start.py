#!/usr/bin/env python

import time

import yaml

from icloud_homie.icloud_account import ICloud_Account 

with open("icloud_homie.yml", 'r') as ymlfile:
    cfg = yaml.full_load(ymlfile)

accounts = cfg['icloud']
for name,account_info in accounts.items():
    ic = ICloud_Account(name,account_info ['username'],account_info ['password'],mqtt_settings=cfg['mqtt'])

update_interval = int(cfg ['update_interval'])


try:
    while True:
        time.sleep(update_interval*60)

        ic.update_devices()

except (KeyboardInterrupt, SystemExit):
    print("Quitting.")  