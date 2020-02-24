#!/usr/bin/env python

import pytz
import time
import datetime
import traceback
import logging
import traceback

logger = logging.getLogger(__name__)

from homie.device_base import Device_Base

from homie.node.node_base import Node_Base

from homie.node.property.property_float import Property_Float
from homie.node.property.property_switch import Property_Switch
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
    def __init__(
        self,
        device_id,
        name,
        update_interval,
        icloud_device=None,
        homie_settings=None,
        mqtt_settings=None,
    ):

        super().__init__(device_id, name, homie_settings, mqtt_settings)

        self.last_refresh_time = 0
        self.icloud_device = icloud_device

        node = Node_Base(self, "status", "Status", "status")
        self.add_node(node)

        self.device_status = Property_String(
            node, id="devicestatus", name="Device Status"
        )
        node.add_property(self.device_status)

        self.battery_level = Property_Battery(node)
        node.add_property(self.battery_level)

        self.battery_status = Property_String(
            node, id="batterystatus", name="Battery Status"
        )
        node.add_property(self.battery_status)

        self.latitude = Property_Float(
            node, id="latitude", name="Latitude", settable=False
        )
        node.add_property(self.latitude)

        self.longitude = Property_Float(
            node, id="longitude", name="Longitude", settable=False
        )
        node.add_property(self.longitude)

        self.location_accuracy = Property_Float(
            node, id="accuracy", name="Location Accuracy", settable=False
        )
        node.add_property(self.location_accuracy)

        self.location_type = Property_String(
            node, id="locationtype", name="Location Type"
        )
        node.add_property(self.location_type)

        self.location = Property_String(node, id="location", name="Location")
        node.add_property(self.location)

        self.location_lastupdate = Property_String(
            node, id="lastupdate", name="Location Last Update"
        )
        node.add_property(self.location_lastupdate)

        self.location_combined = Property_String(
            node, id="locationcombined", name="All Location Data"
        )
        node.add_property(self.location_combined)

        node = Node_Base(self, "control", "Control", "control")
        self.add_node(node)

        self.enable_location = Property_Switch(
            node,
            id="enablelocation",
            name="Enable Location",
            value="ON",
            set_value=self.set_enable_location,
        )
        node.add_property(self.enable_location)

        self.enable_cache = Property_Switch(
            node,
            id="enablelocationcache",
            name="Enable Location Cache",
            value="ON",
            set_value=self.set_location_cache,
        )
        node.add_property(self.enable_cache)

        self.refresh_timer = Property_Float(
            node,
            id="refreshtimer",
            name="Refresh Timer",
            value=update_interval,
            set_value=self.set_refresh_timer,
        )
        node.add_property(self.refresh_timer)

        self.findmyphone = Property_Switch(
            node, id="findphone", name="Find My Phone", set_value=self.set_find_my_phone
        )
        node.add_property(self.findmyphone)

        self.refresh = Property_Switch(
            node, id="refresh", name="Refresh", set_value=self.set_refresh
        )
        node.add_property(self.refresh)

        self.start()

        self.update()

    def update(self):
        try:
            location = None
            if (time.time() - self.last_refresh_time) > self.refresh_timer.value * 60:
                status = self.icloud_device.status(STATUSREQUEST)
                if self.enable_location.value == "ON":
                    location = self.icloud_device.location()
                    if self.enable_cache.value == "OFF":
                        time.sleep(20)
                        location = self.icloud_device.location()
                self.last_refresh_time = time.time()
            else:
                return
            # print (location)
        except Exception as e:
            traceback.print_exc()
            logger.warning("Error updating device {}. Error {}".format(self.device_id,e))
            return

        try:
            self.device_status.value = DEVICESTATUSCODES[status["deviceStatus"]]
            self.battery_level.value = round(float(status["batteryLevel"]) * 100, 0)
            self.battery_status.value = status["batteryStatus"]
            if location is not None:
                self.location_lastupdate.value = datetime.datetime.fromtimestamp(
                    float(location["timeStamp"]) / 1000
                ).strftime("%d/%m/%Y %H:%M:%S")
                self.latitude.value = float(location["latitude"])
                self.longitude.value = float(location["longitude"])
                self.location.value = "{},{}".format(
                    location["latitude"], location["longitude"]
                )
                self.location_accuracy.value = float(location["horizontalAccuracy"])
                self.location_type.value = location["positionType"]

                location = {
                    'latitude':float(location["latitude"]),
                    'longitude':float(location["longitude"]),
                    'accuracy':float(location["horizontalAccuracy"]),
                    'type': location["positionType"],
                }

                self.location_combined.value = str(location)

            else:
                self.location_lastupdate.value = "Unknown"
                self.latitude.value = 0
                self.longitude.value = 0
                self.location_accuracy.value = 0
                self.location_type.value = "Unknown"

        except:
            traceback.print_exc()
            self.battery_level.value = 0
            self.battery_status.value = "Unknown"
            self.location_lastupdate.value = "Unknown"
            self.latitude.value = 0
            self.longitude.value = 0
            self.location_accuracy.value = 0
            self.location_type.value = "Unknown"

    def set_enable_location(self, value):
        self.enable_location.value = value

    def set_location_cache(self, value):
        self.enable_cache.value = value

    def set_find_my_phone(self, value):
        self.icloud_device.play_sound()
        self.findmyphone.value = "ON"
        self.findmyphone.value = "OFF"

    def set_refresh(self, value):
        self.update()
        self.refresh.value = "ON"
        self.refresh.value = "OFF"

    def set_refresh_timer(self, value):
        self.refresh_timer.value = value
