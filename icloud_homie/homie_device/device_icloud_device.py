#!/usr/bin/env python

import pytz 
import datetime 
import traceback

from homie.device_base import Device_Base

from homie.node.node_base import Node_Base

from homie.node.property.property_float import Property_Float
from homie.node.property.property_temperature import Property_Temperature
from homie.node.property.property_battery import Property_Battery
from homie.node.property.property_enum import Property_Enum
from homie.node.property.property_string import Property_String

DEVICESTATUSSET = [
    "features",
    "maxMsgChar",
    "darkWake",
    "fmlyShare",
    "deviceStatus",
    "remoteLock",
    "activationLocked",
    "deviceClass",
    "id",
    "deviceModel",
    "rawDeviceModel",
    "passcodeLength",
    "canWipeAfterLock",
    "trackingInfo",
    "location",
    "msg",
    "batteryLevel",
    "remoteWipe",
    "thisDevice",
    "snd",
    "prsId",
    "wipeInProgress",
    "lowPowerMode",
    "lostModeEnabled",
    "isLocating",
    "lostModeCapable",
    "mesg",
    "name",
    "batteryStatus",
    "lockedTimestamp",
    "lostTimestamp",
    "locationCapable",
    "deviceDisplayName",
    "lostDevice",
    "deviceColor",
    "wipedTimestamp",
    "modelDisplayName",
    "locationEnabled",
    "isMac",
    "locFoundEnabled",
]

STATUSREQUEST = [
    "deviceStatus",
    "statusCode",
    "location",
    "msg",
    "batteryLevel",
    "isLocating",
    "lostModeCapable",
    "mesg",
    "batteryStatus",
    "locationCapable",
    "deviceDisplayName",
    "modelDisplayName",
    "locationEnabled",
]

DEVICESTATUSCODES = {
    "200": "online",
    "201": "offline",
    "203": "pending",
    "204": "unregistered",
}

class Device_iCloud_Device(Device_Base):

    def __init__(self, device_id, name, icloud_device=None, homie_settings=None, mqtt_settings=None):

        super().__init__ (device_id, name, homie_settings, mqtt_settings)

        self.icloud_device = icloud_device

        node = (Node_Base(self,'status','Status','status'))
        self.add_node (node)

        self.device_status = Property_String (node, id='devicestatus', name="Device Status")
        node.add_property (self.device_status)

        self.battery_level = Property_Battery (node)
        node.add_property (self.battery_level)

        self.battery_status = Property_String (node, id='batterystatus', name="Battery Status")
        node.add_property (self.battery_status)

        self.latitude = Property_Float (node, id='latitude', name="Latitude", settable=False)
        node.add_property (self.latitude)

        self.longitude = Property_Float (node, id='longitude', name="Longitude", settable=False)
        node.add_property (self.longitude)

        self.location_accuracy = Property_Float (node, id='accuracy', name="Location Accuracy", settable=False)
        node.add_property (self.location_accuracy)

        self.location_lastupdate = Property_String (node, id='lastupdate', name="Location Last Update")
        node.add_property (self.location_lastupdate)

        self.start()

        self.update()

    def update(self):
        status = self.icloud_device.status (STATUSREQUEST)
        location = self.icloud_device.location ()

        try:
            self.device_status.value = DEVICESTATUSCODES[status["deviceStatus"]]
            self.battery_level.value = round(float(status["batteryLevel"])*100,0)
            self.battery_status.value = status["batteryStatus"]
            if location is not None:
                self.location_lastupdate.value = datetime.datetime.fromtimestamp(float(location["timeStamp"])/1000).strftime("%d/%m/%Y %H:%M:%S")
                self.latitude.value = float(location["latitude"])
                self.longitude.value = float(location["longitude"])
                self.location_accuracy.value = float(location["horizontalAccuracy"])
            else:
                self.location_lastupdate.value = "Unknown"
                self.latitude.value = 0
                self.longitude.value = 0
                self.location_accuracy.value = 0

        except:
            traceback.print_exc()
            self.battery_level.value = 0
            self.battery_status.value = "Unknown"
            self.location_lastupdate.value = "Unknown"
            self.latitude.value = 0
            self.longitude.value = 0
            self.location_accuracy.value = 0
