#!/usr/bin/env python

import logging
import traceback
import os

from pyicloud import PyiCloudService
from pyicloud.exceptions import (
    PyiCloudException,
    PyiCloudFailedLoginException,
    PyiCloudNoDevicesException,
)

from .homie_device.device_icloud_device import Device_iCloud_Device
from .homie_device.device_icloud_account import Device_iCloud_Account

logger = logging.getLogger(__name__)

PERMITTED_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz-" 

class ICloud_Account (object):

    def __init__(self, name, username, password, homie_settings=None, mqtt_settings=None):

        self.homie_settings = homie_settings
        self.mqtt_settings = mqtt_settings
        self.username = username
        self.password = password

        self.api = None

        self._trusted_device = None
        self._trusted_device_name = "None"

        self.device_account = Device_iCloud_Account(device_id=name, name= name + ' iCloud Account', icloud_account=self, homie_settings=homie_settings, mqtt_settings=mqtt_settings)
        self.device_account.connection_status.value ="Not Connected"

        self.device_name_list = []
        self.homie_devices = []

        self.connect_icloud()

    def connect_icloud(self):
        try:
            self.api = PyiCloudService(self.username,self.password,cookie_directory=os.getcwd(),verify=True)
            self.device_account.connection_status.value ="Connected"

        except PyiCloudFailedLoginException as error:
            self.api = None
            logger.error("Error logging into iCloud Service: %s", error)
            self.device_account.connection_status.value ="Login Error {}".format(error)
            return

        if self.api.requires_2fa:
            try:
                if self._trusted_device is None:
                    self._trusted_device = self.get_trusted_device()
                    self._trusted_device_name = "device"+"".join(c for c in self._trusted_device.get('phoneNumber') if c in PERMITTED_CHARS)
                    self.device_account.update()

                    if not self.api.send_verification_code(self._trusted_device):
                        logger.error("Failed to send verification code")
                        self._trusted_device = None
                        self.device_account.connection_status.value ="Failed sending verification code"
                        return

            except PyiCloudException as error:
                self.device_account.connection_status.value ="2FA Error"
                logger.error("Error setting up 2FA: %s", error)
                return
        
        try:
            self.api.authenticate()
            self.connected()

        except PyiCloudFailedLoginException as msg:
            logger.error("Failed to authenticate {}", msg)


    def connected (self):
        self.device_account.connection_status.value ="Ready"
        self.add_devices()
    
    def get_trusted_device (self):
        devices = self.api.trusted_devices
        for i, device in enumerate(devices):
            #print ( "deviceName", "SMS to %s" % device.get("phoneNumber"))
            return device
        return None

    def add_devices (self):
        for device_id,device_info in self.api.devices.items():
            try:
                print (device_id,device_info)
                device = self.api.devices [device_id]
                status = device.status (["name","rawDeviceModel","deviceStatus"])
                print(device, status["deviceStatus"])

                name = "".join(c for c in (status["name"]+'-'+status["rawDeviceModel"]).lower() if c in PERMITTED_CHARS)
                logger.info ('New icloud device {}'.format(name))

                if status["deviceStatus"] in ["200","201"]:
                    logger.info ('Adding icloud device {}'.format(name))
                    print  ('adding')

                    ic = Device_iCloud_Device (device_id=name,name=name,icloud_device=device,mqtt_settings=self.mqtt_settings)

                    self.homie_devices.append(ic)
                    self.device_name_list.append(name)
                    self.device_account.update()
                else:
                    logger.info ('Skipping icloud device {}'.format(name))
            except Exception as e:
                logger.warning ('Error adding device. Error {}'.format(e))

    
    def send_verification_code (self,code):
        try:
            if self.api.validate_verification_code(self._trusted_device, code):
                self.connected()
            else:
                logger.error("Failed to verify verification code: %s", error)

        except PyiCloudException as error:
            logger.error("Failed to verify verification code: %s", error)

    def update_devices(self):
        for device in self.homie_devices:
            device.update()
