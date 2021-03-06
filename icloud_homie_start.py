#!/usr/bin/env python

import time
import yaml

from icloud_homie.icloud_account import ICloud_Account 

try:
    with open("/etc/icloud_homie.yml", 'r') as ymlfile:
        cfg = yaml.full_load(ymlfile)
except FileNotFoundError:
    with open('icloud_homie.yml', 'r') as ymlfile:
        cfg = yaml.full_load(ymlfile)

ic = []

accounts = cfg['icloud']
for name,account_info in accounts.items():
    ic.append(ICloud_Account(name,account_info ['username'],account_info ['password'],int(cfg ['update_interval']),mqtt_settings=cfg['mqtt']))

try:
    while True:
        time.sleep(int(cfg ['update_interval'])*60)
        for account in ic:
            account.update_devices()

except (KeyboardInterrupt, SystemExit):
    print("Quitting.")  
