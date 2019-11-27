#!/usr/bin/env python

import pytz 
import datetime 
import traceback

from homie.device_base import Device_Base

from homie.node.node_base import Node_Base

from homie.node.property.property_float import Property_Float
from homie.node.property.property_string import Property_String


class Device_iCloud_Account(Device_Base):

    def __init__(self, device_id, name, icloud_account=None, homie_settings=None, mqtt_settings=None):

        super().__init__ (device_id, name, homie_settings, mqtt_settings)

        self.icloud_account = icloud_account

        node = (Node_Base(self,'account','iCloud Account','account'))
        self.add_node (node)

        self.account_username = Property_String (node, id='account', name="Accout User Name")
        node.add_property (self.account_username)

        self.trusted_device = Property_String (node, id='trusteddevice', name="Trusted Device")
        node.add_property (self.trusted_device)

        self.connection_status = Property_String (node, id='connection', name="iCloud Connection Status")
        node.add_property (self.connection_status)

        self.device_list = Property_String (node, id='devices', name="Devices")
        node.add_property (self.device_list)

        self.verification_code = Property_String (node, id='verificationcode', name="Verification Code", settable=True,set_value=icloud_account.send_verification_code)
        node.add_property (self.verification_code)

        self.start()

        self.account_username.value = 'Unknown'
        self.trusted_device.value = 'Unknown'

    def update(self):
        self.account_username.value = self.icloud_account.username
        self.trusted_device.value = self.icloud_account._trusted_device_name
        self.device_list.value = ", ".join (self.icloud_account.device_name_list)

